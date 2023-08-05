# -*- coding:utf-8; tab-width:4; mode:python -*-

import os
from signal import SIGTERM
import time
from functools import partial
import io

import hamcrest

from commodity.type_ import checked_type
from commodity.os_ import SubProcess, FileTee, FuncAsTextFile
from commodity.log import PrefixLogger

from .assertion import Assertion, Matcher
from .tools import create_file, create_logger, Interpolator, file_types
from .const import PREGO_TMP, AUTO, INDENTST
from .item import File, DeferredAttr
from . import config
from . import gvars
from .const import Status, term

NoneType = type(None)


DEFAULT = '__DEFAULT__'


class Command(Assertion):
    def __init__(self, task, cmdline,
                 stdout=None, stderr=None,
                 expected=DEFAULT, timeout=DEFAULT,
                 signal=None, cwd=None, env={}):

        self._returncode = None
        self.interpolator = Interpolator()
        self.cmdline = self.interpolator.apply(checked_type(str, cmdline))

        self._set_expected(expected)
        super(Command, self).__init__(task)

        self._stdout = self.interpolator.apply(stdout)
        self._stderr = self.interpolator.apply(stderr)

        self._set_cwd(cwd)

        self.tinit = self.tend = None

        self._set_timeout(timeout)
        self._set_signal(signal)
        self._set_env(env)

        self.sp = None
        self._enable_outs_if_requested()

        if self.timeout is None and not self.task.detach:
            self.log.warning('%s$name %sNo timeout command in a non detached task could block forever!%s', INDENTST, term().bold_red, term().normal)

    def _set_cwd(self, cwd):
        cwd = cwd or gvars.context.get('cwd', '.')
        self.cwd = self.interpolator.apply(checked_type(str, cwd))

    def _set_expected(self, expected):
        if expected == DEFAULT:
            expected = gvars.context.get('expected', 0)
        self.expected = checked_type((int, NoneType), expected)

    def _set_timeout(self, timeout):
        if timeout == DEFAULT:
            timeout = gvars.context.get('timeout', 5)
        self.timeout = checked_type((int, NoneType), timeout)

    def _set_signal(self, signal):
        signum = signal or gvars.context.get('signal', SIGTERM)
        self.signal = checked_type(int, signum)

    def _set_env(self, env):
        self.env = os.environ.copy()
        context_env = checked_type(dict, gvars.context.get('env', {}))
        self.env.update(context_env)
        self.env.update((str(k), str(v)) for k, v in env.items())

    def do_eval(self):
        return self.run()

    def is_running(self):
        return self.status is Status.UNKNOWN and not self.terminated

    @property
    def terminated(self):
        if self.sp is None:
            return False

        return self.sp.terminated()

    def _enable_outs_if_requested(self):
        self._enable_out('out', bool(self._stdout) or config.stdout)
        self._enable_out('err', bool(self._stderr) or config.stderr)

    def _enable_out(self, outname, state=True):
        assert outname in ['out', 'err'], "Internal Error"
        if not state:
            return

        out = getattr(self, "_std%s" % outname)
        if out is None and state:
            out = AUTO

        if out is AUTO:
            out = os.path.join(PREGO_TMP, '%s.%s' % (self.name, outname))

        if isinstance(out, str):
            out = create_file(out, 'wb', 0)

        if isinstance(out, file_types):
            assert out.writable(), "%s must be writable" % out.name
            out = File.from_fd(out)

        setattr(self, "_std%s" % outname, out)
        self.task.gen.append(out)

    @property
    def stdout(self):
        if self._stdout is None:
            self._stdout = AUTO
            self._enable_out('out')

        return self._stdout

    @property
    def stderr(self):
        if self._stderr is None:
            self._stderr = AUTO
            self._enable_out('err')

        return self._stderr

    def _any_out_activated(self):
        return any([self.stdout, self.stderr])

    def run(self):
        def decorate_out_with_logger(out, suffix, activate):
            if out is None:
                return

            if not activate:
                return out

            out_logger_name = '{0}.{1}'.format(self.name, suffix)
            out_logger = create_logger(out_logger_name)
            prefix = '%s%s| ' % (9 * ' ', out_logger.name)
            return FileTee(
                out, to_textfile_wrapper(
                    FuncAsTextFile(out_logger.info, prefix)))

        stdout = decorate_out_with_logger(self._stdout, 'out', config.stdout)
        stderr = decorate_out_with_logger(self._stderr, 'err', config.stderr)

        if self._any_out_activated():
            self.log_status()

        logger = PrefixLogger(self.log, '%s%s ' % (INDENTST, self.name))

        self.tinit = time.time()
        self.sp = SubProcess(
            self.cmdline,
            stdout=stdout, stderr=stderr,
            close_outs=True,
            cwd=self.cwd,
            shell=True,
            signal=self.signal,
            env=self.env,
            logger=logger)

        if not self.terminated:
            self.log_status()

        self.wait()
        self.tend = time.time()
        return True

    @property
    def returncode(self):
        if self._returncode is not None:
            return self._returncode

        # FIXME: is this required?
        return DeferredAttr(self, 'returncode', 'sync_returncode')

    @property
    def sync_returncode(self):
        return self.sp.returncode

    def _current_elapsed(self):
        return time.time() - self.tinit

    def elapsed(self):
        return self.tend - self.tinit

    def on_time(self):
        return self._current_elapsed() < self.timeout

    def wait(self):
        def terminate():
            if self.terminated:
                return

            msg = '{0}$name timeout exceeded: {1:1.2f}s >= {2:1.2f}s, terminating...'
            self.log.debug(msg.format(INDENTST, self._current_elapsed(),
                                      self.timeout))
            self.terminate()

        if self.timeout is not None:
            while self.on_time() and not self.terminated:
                time.sleep(0.05)

            terminate()

        self.sp.wait()
        self._returncode = self.sp.returncode

    def terminate(self):
        if self.sp is None:
            self.log.warning('%s$name terminate: task never started' % INDENTST)
            return

        self.sp.terminate()
        assert self.terminated

    def __unicode__(self):
#        cmd = self.sp or repr(self.cmdline)
        expected = self.expected
        if expected is None:
            expected = ''

        returncode = self.returncode
        if isinstance(returncode, DeferredAttr):
            returncode = ''

        timeout = self.timeout if self.timeout is not None else ''

        elapsed = ''
        if self.terminated and self.tend is not None:
            elapsed = '%.2f' % (self.tend - self.tinit)

        time = ''
        if timeout or elapsed:
            time = ' time {0}:{1}'.format(timeout, elapsed)

        cwd = ''
#        if self.cwd != self.interpolator.testdir:
#            cwd = ' cwd:{0}'.format(self.cwd)

        return u"Command {0!r} code ({1}:{2}){3}{4}".format(
            self.cmdline, expected, returncode, time, cwd)

    def brief(self):
        return "command " + self.name


class CommandExitsWith(Matcher):
    def __init__(self, expected):
        self.expected = expected

    def _matches(self, cmd):
        self.cmd = checked_type(Command, cmd)
        return self.cmd.returncode == self.expected

    def describe_to(self, description):
        description.append_text("returncode %s" % (self.expected))

    def describe_mismatch(self, cmd, mismatch_description):
        mismatch_description.append_text('was %s' % self.cmd.returncode)

    def brief(self):
        return u'exit code'


def exits_with(expected):
    return CommandExitsWith(expected)


def killed_by(signal):
    return CommandExitsWith(-signal)


class RanForTime(Matcher):
    def __init__(self, expected):
        self.expected = expected

    def _matches(self, cmd):
        self.cmd = checked_type(Command, cmd)
        return hamcrest.is_(self.expected).matches(cmd.elapsed())

    def describe_to(self, description):
        description.append_text("execution time %ss" % (self.expected))

    def describe_mismatch(self, cmd, mismatch_description):
        mismatch_description.append_text('was %.2fs' % self.cmd.elapsed())


def ran_for_time(secs):
    return RanForTime(secs)


class to_textfile_wrapper:
    def __init__(self, fd):
        self.fd = fd

    def write(self, data):
        self.fd.write(data.decode(errors='ignore'))

    def flush(self):
        pass

    @property
    def closed(self):
        return self.fd.closed

    def close(self):
        pass
