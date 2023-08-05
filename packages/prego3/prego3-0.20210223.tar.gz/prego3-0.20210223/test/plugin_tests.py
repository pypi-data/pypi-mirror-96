# -*- coding:utf-8; tab-width:4; mode:python -*-

import hamcrest

from prego import Task, TestCase, exists, context, running
from prego.net import Host, localhost, listen_port
from prego.shell import Variable
from prego.debian import Package, installed

from .unit_tests import AssertionTest


class Net(TestCase):
    def test_localhost_listen_port(self):
        Task().assert_that(localhost, hamcrest.is_not(listen_port(9999)))

    def test_remote_host_listen_port(self):
        Task().assert_that(Host('www.google.com'), listen_port(80))

    def test_netcat(self):
        context.port = 2000
        server = Task(desc='netcat server', detach=True)
        server.assert_that(Package('nmap'), installed())
        server.assert_that(localhost,
                           hamcrest.is_not(listen_port(context.port)))
        cmd = server.command('ncat -l -p $port')
        server.wait_that(cmd.stdout.content,
                         hamcrest.contains_string('bye'))

        client = Task(desc='netcat client')
        client.wait_that(server, running())
        client.wait_that(localhost,
                         listen_port(context.port))
        client.command('echo bye | ncat localhost $port')


class ShellMatchers(TestCase, AssertionTest):
    def test_variable_defined(self):
        Task().assert_that(Variable('SHELL'), exists())

    def test_variable_contains(self):
        Task().assert_that(Variable('SHELL'),
                           hamcrest.contains_string('/bin/'))


#class MailMatchers(TestCase):
#    def test_smtp(self):
#        task = Task()
#        smtp = task.smtp('default')
#        task.assert_that(stmp.send('text'), )
#
#        imap = IMAP('default')
#        task.assert_that(imap, contains_message(subject('hi')))
