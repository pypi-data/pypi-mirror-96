# -*- coding:utf-8; tab-width:4; mode:python -*-
import sys

import os
from unittest import TestCase
from six import BytesIO
from signal import SIGINT

import hamcrest
from doublex import Stub, Spy, assert_that, called

sys.path.insert(0, '.')
import prego
from prego import Status, gvars


class TestStatus(TestCase):
    def test_repr(self):
        self.assertEquals(str(Status.FAIL), 'FAIL')
        self.assertEquals(str(Status.OK), 'OK')
        self.assertEquals(str(Status.NOEXEC), 'NOEXEC')


class Tasks(TestCase):
    def test_zero_tasks_is_ok(self):
        prego.init()
        prego.commit()
        self.assertEquals(0, len(gvars.tasks))

    def test_one_task(self):
        prego.init()
        prego.Task().command('true')
        self.assertEquals(1, len(gvars.tasks))

    def test_init(self):
        prego.init()
        prego.Task().command('true')
        prego.init()
        self.assertEquals(0, len(gvars.tasks))

    def test_2_cmds(self):
        prego.init()
        task = prego.Task()
        task.command('true')
        task.command('ls')
        prego.commit()


class AssertionTest(object):
    def assert_that(self, actual, matcher):
        task = prego.Task()
        return task.assert_that(actual, matcher)


class CommandOuts(TestCase):
    def tearDown(self):
        try:
            os.remove('/tmp/task-out')
        except OSError:
            pass

    def test_stdout_with_bytesio(self):
        class FakeFile:
            closed = False

            def __init__(self):
                self.buff = bytes()

            def write(self, data):
                self.buff += data

        prego.init()
        out = FakeFile()
        out.name = "bytes-io"

        task = prego.Task()
        task.command('echo hi', stdout=out)
        task.run()

        self.assertIn(b'hi', out.buff)

    def test_stdout_with_filename(self):
        prego.init()
        fname = '/tmp/task-out'

        try:
            os.remove(fname)
        except OSError:
            pass

        task = prego.Task()
        task.command("echo hi", stdout=fname)
        task.assert_that(prego.File('/tmp/task-out').content,
                         hamcrest.contains_string('hi'))

        task.run()

        content = open(fname).read()

        self.assert_(os.path.exists(fname))
        self.assertIn('hi', content)

    def test_stdout_was_closed(self):
        prego.init()
        out = BytesIO()
        out.name = "bytes-io"

        task = prego.Task()
        task.command(u'echo hi', stdout=out)
        task.run()

        self.assert_(out.closed)

    def test_logging_output(self):
        prego.init()
        task = prego.Task()
        cmd = task.command('python test/utils/log.py hi')
        task.assert_that(cmd.stderr.content,
                         hamcrest.contains_string('hi'))
        task.run()

        self.assertIn('hi', cmd.stderr.read())
        self.assertEquals(Status.OK, task.status)


class OutContentMatchers(TestCase, AssertionTest):
    def test_out_contains__explicit_filename(self):
        prego.init()
        task = prego.Task()
        cmd = task.command('echo hi', stdout='/tmp/somename.out')
        task.assert_that(cmd.stdout.content,
                         hamcrest.contains_string('hi'))
        prego.commit()

    def test_out_contains__AUTO(self):
        prego.init()
        task = prego.Task()
        cmd = task.command('echo hi', stdout=prego.AUTO)
        task.assert_that(cmd.stdout.content,
                         hamcrest.contains_string('hi'))
        prego.commit()

    def test_out_contains__AUTO_wo_hamcrest_contains(self):
        task = prego.Task()
        cmd = task.command('echo hi', stdout=prego.AUTO)
        task.run()

        self.assertIn('hi', cmd.stdout.read())

    def test_out_contains__implicit(self):
        prego.init()
        task = prego.Task()
        cmd = task.command('echo hi')
        task.assert_that(cmd.stdout.content,
                         hamcrest.contains_string('hi'))
        prego.commit()

    def test_err_contains_explicit_filename(self):
        prego.init()
        task = prego.Task()
        cmd = task.command('echo hi >&2', stderr='/tmp/somename.err')
        task.assert_that(cmd.stderr.content,
                         hamcrest.contains_string('hi'))
        prego.commit()

    def test_err_contains_AUTO(self):
        prego.init()
        task = prego.Task()
        cmd = task.command('echo hi >&2', stderr=prego.AUTO)
        task.assert_that(cmd.stderr.content,
                         hamcrest.contains_string('hi'))
        prego.commit()

    def test_err_contains_AUOT_wo_hamcrest_contains(self):
        task = prego.Task()
        cmd = task.command('echo hi >&2', stderr=prego.AUTO)
        task.run()

        self.assertIn('hi', cmd.stderr.read())

    def test_err_contains__implicit(self):
        prego.init()
        task = prego.Task()
        cmd = task.command('echo hi >&2')
        task.assert_that(cmd.stderr.content,
                         hamcrest.contains_string('hi'))
        prego.commit()


class TaskMatchers(TestCase, AssertionTest):
    def test_ok(self):
        prego.init()
        task = prego.Task()
        cmd = task.command('echo hi')
        task.assert_that(cmd, prego.exits_with(0))
        prego.commit()

        self.assertEquals(Status.OK, task.status)

    def test_task_running(self):
        with Stub() as cmd:
            cmd.is_running().returns(True)
            cmd.brief().returns('STUB')

        c = self.assert_that(cmd, prego.running())
        c.eval()

    def test_task_running_fail(self):
        with Stub() as cmd:
            cmd.is_running().returns(False)
            cmd.brief().returns('STUB')

        c = self.assert_that(cmd, prego.running())
        with self.assertRaises(prego.PregoAssertionFailed):
            c.eval()


class WaitThat(TestCase):
    def test_wait_3_tries_ok(self):
        with Spy() as other_task:
            other_task.is_running().delegates([False, False, True])

        task = prego.Task()
        c = task.wait_that(other_task, prego.running(), delta=0.1, timeout=1)
        c.eval()

        assert_that(other_task.is_running, called().times(3))

    def test_wait_fail(self):
        with Spy() as cmd:
            cmd.is_running().delegates([False, False, False])

        task = prego.Task()
        c = task.wait_that(cmd, prego.running(), delta=0.1, timeout=0.3)

        with self.assertRaises(prego.PregoAssertionFailed):
            c.eval()

        assert_that(cmd.is_running, called().times(3))


class CommandReturncodes(TestCase):
    def test_no_commands_is_ok(self):
        prego.init()
        task = prego.Task()
        task.run()

        self.assertEquals(Status.OK, task.status)

    def test_ok(self):
        prego.init()
        task = prego.Task()
        task.command('echo hi')
        task.run()

        self.assertEquals(Status.OK, task.status)

    def test_fail(self):
        prego.init()
        task = prego.Task()
        task.command("false")
        task.run()

        self.assertEquals(Status.FAIL, task.status)

    def test_ls_ok(self):
        prego.init()
        task = prego.Task()
        task.command('ls')
        task.run()

        self.assertEquals(Status.OK, task.status)

    def test_ls_fail(self):
        task = prego.Task()
        task.command("ls /missing-file")
        task.run()

        self.assertEquals(Status.FAIL, task.status)


class Tasks_with_shell(TestCase):
    pass
#    def task_pipe_no_shell(self):
#        task = prego.Task('date | cat')
#        task.run()
#
#        self.assertEquals(Status.FAIL, task.status)


class PreAndPostAssertions(TestCase):
    def test_ok(self):
        task = prego.Task()
        task.command('true')
        task.run()

        self.assertEquals(Status.OK, task.status)

    def test_fail(self):
        task = prego.Task()
        task.command('false')
        task.run()

        self.assertEquals(Status.FAIL, task.status)

    def test_just_1_assertion_ok(self):
        task = prego.Task()
        task.assert_that('hello world', hamcrest.contains_string('llo'))
        task.run()

        self.assertEquals(1, len(task.assertions))
        self.assertEquals(Status.OK, task.status)

    def test_just_1_assertion_fail(self):
        task = prego.Task()
        task.assert_that('hello world', hamcrest.contains_string('missing'))
        task.run()

        self.assertEquals(Status.FAIL, task.status)
        self.assertEquals(Status.FAIL, task.assertions[0].status)

    def test_with_preassertion_fail_by_assertion(self):
        task = prego.Task()
        task.assert_that('hello world', hamcrest.contains_string('missing'))
        task.command('true')
        task.run()

        self.assertEquals(4, len(task.assertions))
        self.assertEquals(Status.FAIL, task.status)
        self.assertEquals(Status.FAIL, task.assertions[0].status)

    def test_with_postassertion_fail_by_assertion(self):
        task = prego.Task()
        task.command('true')
        task.assert_that('hello world', hamcrest.contains_string('missing'))
        task.run()

        self.assertEquals(4, len(task.assertions))
        self.assertEquals(Status.FAIL, task.status)
        self.assertEquals(Status.FAIL, task.assertions[3].status)

    def test_with_preassertion_fail_by_cmd(self):
        task = prego.Task()
        task.assert_that('hello world', hamcrest.contains_string('worl'))
        task.command('false')
        task.run()

        self.assertEquals(Status.FAIL, task.status)
        self.assertEquals(Status.OK, task.assertions[0].status)

    def test_with_postassertion_fail_by_cmd__assertion_not_executed(self):
        task = prego.Task()
        task.command('false')
        task.assert_that('hello world', hamcrest.contains_string('worl'))
        task.run()

        self.assertEquals(Status.FAIL, task.status)
        self.assertEquals(Status.NOEXEC, task.assertions[3].status)

    def test_cmd_pre_and_postassertion(self):
        task = prego.Task()
        task.assert_that('hello world', hamcrest.contains_string('worl'))
        task.command('true')
        task.assert_that(2, hamcrest.greater_than(1))
        task.run()

        self.assertEquals(Status.OK, task.status)
        self.assertEquals(Status.OK, task.assertions[0].status)
        self.assertEquals(Status.OK, task.assertions[2].status)


class CommandTimeout(TestCase):
    def test_fail_by_timeout(self):
        prego.init()
        task = prego.Task()
        task.command('sleep 2', timeout=1, expected=None)
        task.run()

        self.assertEquals(Status.FAIL, task.status)

    def test_meet_default_timeout(self):
        prego.init()
        task = prego.Task()
        task.command('sleep 2')
        prego.commit()


class ConmmandSignal(TestCase):
    def test_task_is_killed_by_specified_signal(self):
        prego.init()
        task = prego.Task()
        cmd = task.command('sleep 5', signal=SIGINT, timeout=1)

        try:
            prego.commit()
            self.fail()
        except prego.TestFailed:
            self.assertEquals(cmd.returncode, -SIGINT)


class CommandEnv(prego.TestCase):
    def test_env(self):
        task = prego.Task()
        task.command('echo $MYVAR', env={'MYVAR': '100'})
        task.assert_that(task.lastcmd.stdout.content, hamcrest.contains_string('100'))

    def test_env_no_str(self):
        task = prego.Task()
        task.command('echo $MYVAR', env={'MYVAR': 100})
        task.assert_that(task.lastcmd.stdout.content, hamcrest.contains_string('100'))


class PregoCase(prego.TestCase):
    def task_simple(self):
        task = prego.Task()
        task.command('echo hi')

# class sync_wait_that_tests(TestCase):
#     def setUp(self):
#         prego.a ssert_that(prego.localhost, hamcrest.is_not(prego.listen_port(2000)))
#         self.server = SubProcess('ncat -l 2000')
#
#     def tearDown(self):
#         self.server.terminate()
#
#     def test_wait_server_become_ready(self):
#         prego.wait_that(prego.localhost, prego.listen_port(2000))


class lastcmd(prego.TestCase):
    def test_non_exising_lastcmd(self):
        task = prego.Task()
        with self.assertRaises(IndexError):
            task.assert_that(task.lastcmd, prego.running())


class DealingWithDetach(prego.TestCase):
    def test_this(self):
        t = prego.Task('cat', detach=True)
        c = t.command("sleep 1; echo 'ready'; sleep 10",
                      expected=-15)

        o = prego.Task()
        o.wait_that(
            c.stdout.content,
            hamcrest.contains_string("ready"))

        prego.Task().delay()
