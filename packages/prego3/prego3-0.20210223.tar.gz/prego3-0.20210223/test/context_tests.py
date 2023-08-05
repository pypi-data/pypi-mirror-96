# -*- coding:utf-8; tab-width:4; mode:python -*-

import sys
sys.path.insert(0, '.')

import signal
import unittest

from hamcrest import contains_string, is_not
from prego import Task, context, init, commit, TestFailed


class ContextTests(unittest.TestCase):
    def test_set_read_var(self):
        init()
        context.port = 2030
        task = Task()
        cmd = task.command('echo $port')
        task.assert_that(cmd.stdout.content, contains_string('2030'))
        commit()

    def test_z_read_missing(self):
        init()
        task = Task()
        cmd = task.command('echo $port')
        task.assert_that(cmd.stdout.content, is_not(contains_string('2030')))
        commit()

    def test_default_cwd(self):
        init()
        context.cwd = '/tmp'
        task = Task()
        task.command('pwd')
        task.assert_that(task.lastcmd.stdout.content, contains_string('/tmp'))
        commit()

    def test_default_timeout(self):
        init()
        context.timeout = 3
        task = Task()
        task.command('true')

        commit()
        self.assertEquals(task.lastcmd.timeout, 3)

    # it is the same test as Signals.test_task_is_killed_by_specified_signal
    def test_default_signal(self):
        init()
        context.signal = signal.SIGINT
        task = Task()
        cmd = task.command('sleep 5', timeout=1)

        try:
            commit()
            self.fail()
        except TestFailed:
            self.assertEquals(cmd.returncode, -signal.SIGINT)

    def test_default_env(self):
        init()
        context.env = {'MY_ENV_VAR': '42'}
        task = Task()
        task.command('echo $MY_ENV_VAR')
        task.assert_that(task.lastcmd.stdout.content, contains_string('42'))
        commit()

    def test_env(self):
        init()
        context.env = {'PREGO_SAMPLE': 'hello'}
        task = Task()
        task.command('echo $PREGO_SAMPLE')
        task.assert_that(task.lastcmd.stdout.content, contains_string('hello'))
        commit()
