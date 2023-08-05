# -*- mode: python; coding: utf-8 -*-
import time

import hamcrest
from hamcrest.core.base_matcher import BaseMatcher

from commodity.thread_ import start_new_thread
from commodity.type_ import checked_type
from commodity.str_ import Printable
from commodity.log import UniqueFilter
from commodity.pattern import memoizedproperty
from commodity.log import CallerData
from commodity.path import child_relpath

from .const import Status, INDENTST, term, IDENTIFIERS, PREGO_TMP
from .exc import (PregoAssertionException, log_traceback, UserBreak)
from .tools import Interpolator
from .item import File
from .assertion import (Assertion, DeferredAssertion, PollDeferredAssertion, Delay)
from .command import Command, exits_with, ran_for_time
from . import config
from . import gvars
from .assertion import Matcher

from .tools import create_logger, StatusFilter
# set_logger_default_formatter()


class MatcherRequiredError(Exception):
    pass


class Task(Printable):
    identifiers = []

    def __init__(self, desc='', detach=False):

        # print "stdout:", config.stdout
        # print "stderr:", config.stderr
        # print "keep-going:", config.keep_going

        gvars.tasks.append(self)
        self.interpolator = Interpolator()
        self.desc = checked_type(str, desc)
        self.detach = checked_type(bool, detach)

        self.gen = []
        self.thread = None
        self.status = Status.NOEXEC
        self.tinit = None
        self.elapsed = 0
        self.reason = None

        self.assertions = []

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    @classmethod
    def get_index(cls, objid):
        try:
            i = cls.identifiers.index(objid)
            return IDENTIFIERS[i]
        except IndexError:
            return str(i - 52)
        except ValueError:
            cls.identifiers.append(objid)
            return cls.get_index(objid)

    @property
    def index(self):
        return self.get_index(id(self))

    @property
    def name(self):
        return self.index

    def gen_assertion_index(self):
        return len(self.assertions)

    @memoizedproperty
    def log(self):
        retval = create_logger(self.name)
        retval.addFilter(StatusFilter(self))
        retval.addFilter(UniqueFilter())
        return retval

    def terminate(self):
        self.log.debug("%s$name   waiting for detached task", INDENTST)

        for a in self.assertions:
            a.terminate()

    def run(self):
        if self.detach:
            self.detached_run()
            return

        self.sync_run()

    def detached_run(self):
        self.thread = start_new_thread(self.sync_run)
        self.wait_starts_or_finish()

    def current_elapsed(self):
        return time.time() - self.tinit

    def wait_starts_or_finish(self):
        time.sleep(0.1)

        while 1:
            if self.is_finished() or self.is_running():
                break

            time.sleep(0.1)

            if self.current_elapsed() > 3:
                self.log.critical("%s$name does not start after 3s", INDENTST)
                break

    def sync_run(self):
        self.task_start()

        assertion_iter = iter(self.assertions)
        try:
            for a in assertion_iter:
                a.eval()
                a.log_status()

            self.status = Status.OK

        except PregoAssertionException as e:
            self.set_reason(Status.FAIL, e.assertion)

        except KeyboardInterrupt as e:
            a.status = Status.ERROR
            a.log_status('USER BREAK')
            a.terminate()
            self.set_reason(Status.ERROR, a)
            raise UserBreak()

        except Exception as e:
            # FIXME: convert e to an Assertion
            # self.set_reason(Status.ERROR, e)
            log_traceback(self.log, prefix='%s| ' % INDENTST)

        finally:
            for a in assertion_iter:
                try:
                    if config.keep_going:
                        a.eval()
                    a.log_status()
                except PregoAssertionException:
                    pass

            elapsed = self.current_elapsed()
            self.log.info("$status   $name   Task end - elapsed: %.2fs", elapsed)

    def task_start(self):
        self.tinit = time.time()
        detach_advice = ' [DETACHED]' if self.detach else ''
        msg = '$status   %s$name   Task starts%s: %s%s' % (
            term().bold, detach_advice, self.desc, term().normal)
        self.log.debug(msg)
        self.status = Status.UNKNOWN

    def assert_that(self, actual, matcher=None, reason=''):
        if matcher and not isinstance(matcher, BaseMatcher):
            raise MatcherRequiredError("%s should be a hamcrest Matcher" % str(matcher))
        assertion = DeferredAssertion(self, actual, matcher, reason)
        assertion.caller = CallerData()
        return assertion

    def wait_that(self, actual, matcher, reason='', delta=1, timeout=5):
        assertion = PollDeferredAssertion(
            self, actual, matcher, reason, delta, timeout)
        assertion.caller = CallerData()
        return assertion

#    def fail(self):
#        return FailAssertion(self)

    def command(self, cmdline, **kargs):
        cmd = Command(self, cmdline, **kargs)
        cmd.caller = CallerData()

        if cmd.timeout is not None:
            assertion = DeferredAssertion(
                self, cmd, ran_for_time(hamcrest.less_than(cmd.timeout)))
            assertion.caller = CallerData()

        if cmd.expected is not None:
            assertion = DeferredAssertion(self, cmd, exits_with(cmd.expected))
            assertion.caller = CallerData()

        return cmd

    def delay(self, n=1):
        return Delay(self, n)

    @property
    def lastcmd(self):
        try:
            return [x for x in self.assertions if isinstance(x, Command)][-1]
        except IndexError:
            raise IndexError("No command assertions was defined")

    def is_running(self):
        return self.status == Status.UNKNOWN

    def is_finished(self):
        return self.status not in [Status.UNKNOWN, Status.NOEXEC]

    def wait_detached(self, timeout=None):
        if self.thread:
            self.thread.join(timeout)

    def set_reason(self, status, reason):
        self.status = status
        self.reason = checked_type(Assertion, reason)
        reason.log_status()

    def generate_files(self, *fnames):
        self.gen.extend([File(x) for x in fnames])

    def remove_gen(self):
        def get_relpaths(files):
            return [child_relpath(f.path, start=PREGO_TMP) for f in files]

        if not self.gen:
            return

        if config.dirty:
            self.log.info('%s  $name dirty mode: generated files not removed: %s ',
                          Status.indent(), get_relpaths(self.gen))
            return

        self.log.debug("%s$name   removing %s", INDENTST, get_relpaths(self.gen))

        for f in self.gen:
            f.remove()

    # FIXME: may have serveral command (or none)
    # FIXME: log format
    def __unicode__(self):
        return self.index


class Running(Matcher):
    def _matches(self, cmd):
        return cmd.is_running()

    def describe_to(self, description):
        description.append_text('is running ')


def running():
    return Running()


def terminated():
    return hamcrest.is_not(Running())


# FIXME
def command(cmd, **kargs):
    test = Task()
    test.command(cmd, **kargs)
    return test
