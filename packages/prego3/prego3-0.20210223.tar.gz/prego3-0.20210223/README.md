### System test framework with Python

[![PyPI version](https://badge.fury.io/py/prego3.svg)](https://badge.fury.io/py/prego3) ![](https://github.com/davidvilla/prego3/workflows/test/badge.svg)

Prego is a library consisting on a set of clases and hamcrest matchers usefull
to specify shell command interactions through files, environment variables,
network ports. It provides support to run shell commands on background, send
signal to processes, set assertions on command stdout or stderr, etc.


### Subjects


A summary of subjects and their associated assertions.

#### ``Task(desc='', detach=False)``

Usuallys involve the execution of a program, pre-conditions and post-conditions as assertions.

Common assertions:

- ``assert_that``, for single shot checking.
- ``wait_that``, for polling recurrent checking.
- ``command``, to run arbitrary shell command.

Specific assertions:

- ``running()``, the task is still running.
- ``terminated()``, the task is over.


##### ``Task.command(cmd_line, stdout, stderr, expected, timeout, signal, cwd, env)``

Checks program execution.

Arguments:

- ``expected``: check command line return code. Assertion fails if value does not match.

  - Default value: 0.
  - Return code is ignored if is set to None.

- ``timeout``: assertion fails if execution time exceed timeout (in seconds)

  - Default value is 5.
  - With 0, timeout is not checked.

- ``signal``: send the given signal number to kill command.
- ``cwd``: change to the specified directory before execute command.
- ``env``: a diccionary of environment variables.

Assertions:

- ``running()``
- ``exits_with(value)``
- ``killed_by(signal)``


#### ``File(path)``

Check local files.

- ``exists()``: the file ``path`` exists.


#### ``File().content``

Checks contents of files.

- any hamcrest string matchers (ie: contains_string)

  - example: ``task.wait_that(File('foo'), hamcrest.is_(File('bar'))``


#### ``Variable(nam)``

Checks environment variables.

- ``exists()``: the variable ``name`` exists.
- any hamcrest string matchers (ie: contains_string)

  - example: ``task.assert_that(Variable(SHELL), hamcrest.constains_string('bash'))``



#### ``Host(hostname)``

Checks a network computer.

- ``listen_port(number, proto='tcp')``: a server is listen at ``port``.
- ``reachable()``: host answer to ping.


#### ``Package(name)``

Checks a Debian package

- ``installed()``


### context

The ``context`` is an object whose attributes may be automatically interpolated in command
and filename paths.

Some of them are set as default values for command() parameters too. If ``context.cwd`` is
set, all commands in the same test method will use that value as CWD (Current Working
Directory) unless you define a different value as ``command()`` keyarg.

Context attributes that defaults command() parameters are ``cwd``, ``timeout``,
``signal`` and ``expected``.


### Interpolation

Available interpolation variables are:

- ``$basedir``: the directory where prego is executed (relative).
- ``$fullbasedir``: absolute path of $basedir.
- ``$testdir``: the directory where the running test file is.
- ``$fulltestdir``: absolute path of $testdir.
- ``$testfilename``: the file name of the running test.
- ``$tmpbase``: a safe directory (per user) to put temporary files.
- ``$tmp``: a safe directory (per user and prego instance) to put temporary files.
- ``$pid``: the prego instance PID.


### Examples


#### Testing netcat

    import hamcrest
    from prego import Task, TestCase, context as ctx, running
    from prego.net import localhost, listen_port
    from prego.debian import Package, installed


    class Net(TestCase):
        def test_netcat(self):
            ctx.port = 2000
            server = Task(desc='netcat server', detach=True)
            server.assert_that(Package('nmap'), installed())
            server.assert_that(localhost,
                               hamcrest.is_not(listen_port(ctx.port)))
            cmd = server.command('ncat -l -p $port')
            server.assert_that(cmd.stdout.content,
                               hamcrest.contains_string('bye'))

            client = Task(desc='ncat client')
            client.wait_that(server, running())
            client.wait_that(localhost, listen_port(ctx.port))
            client.command('ncat -c "echo bye" localhost $port')


This test may be executed using nosetest::

    $ nosetests examples/netcat.py
    .
    ----------------------------------------------------------------------
    Ran 1 test in 1.414s

    OK


But prego provides a wrapper (the ``prego`` command) that has some interesting options:

    $ prego -h
    usage: prego [-h] [-c FILE] [-k] [-d] [-o] [-e] [-v] [-p] ...

    positional arguments:
      nose-args

    optional arguments:
      -h, --help            show this help message and exit
      -c FILE, --config FILE
                            explicit config file
      -k, --keep-going      continue even with failed assertion or tests
      -d, --dirty           do not remove generated files
      -o, --stdout          print tests stdout
      -e, --stderr          print tests stderr
      -v, --verbose         increase log verbosity


Same ncat test invoking ``prego``:

    [II] ------  Net.test_netcat BEGIN
    [II] [ ok ]   B.0 wait that A is running
    [II] [ ok ]   A.0 assert that nmap package is installed
    [II] [ ok ]   A.1 assert that localhost not port 2000/tcp to be open
    [II] [fail]   B.1 wait that localhost port 2000/tcp to be open
    [II] [ ok ]   B.1 wait that localhost port 2000/tcp to be open
    [II]          A.2.out| bye
    [II] [ ok ]   B.2 Command 'ncat -c "echo bye" localhost 2000' code (0:0) time 5:1.28
    [II] [ ok ]   B.3 assert that command B.2 returncode to be 0
    [II] [ ok ]   B.4 assert that command B.2 execution time to be a value less than <5>s
    [II] [ OK ]   B   Task end - elapsed: 1.17s
    [II] [ ok ]   A.2 Command 'ncat -l -p 2000' code (0:0) time 5:1.33
    [II] [ ok ]   A.3 assert that command A.2 returncode to be 0
    [II] [ ok ]   A.4 assert that command A.2 execution time to be a value less than <5>s
    [II] [ ok ]   A.5 assert that File '/tmp/prego-david/26245/A.2.out' content a string containing 'bye'
    [II] [ OK ]   A   Task end - elapsed: 1.32s
    [II] [ OK ]  Net.test_netcat END
    ----------------------------------------------------------------------
    Ran 1 test in 1.396s

    OK


#### Testing google reachability

    import hamcrest
    from prego import TestCase, Task
    from prego.net import Host, reachable

    class GoogleTest(TestCase):
        def test_is_reachable(self):
            link = Task(desc="Is interface link up?")
            link.command('ip link | grep wlan0 | grep "state UP"')

            router = Task(desc="Is the local router reachable?")
            router.command("ping -c2 $(ip route | grep ^default | cut -d' ' -f 3)")

            for line in file('/etc/resolv.conf'):
                if line.startswith('nameserver'):
                    server = line.split()[1]
                    test = Task(desc="Is DNS server {0} reachable?".format(server))
                    test.command('ping -c 2 {0}'.format(server))

            resolve = Task(desc="may google name be resolved?")
            resolve.command('host www.google.com')

            ping = Task(desc="Is google reachable?")
            ping.command('ping -c 1 www.google.com')
            ping.assert_that(Host('www.google.com'), reachable())
            ping.assert_that(Host('www.googlewrong.com'), hamcrest.is_not(reachable()))

            web = Task(desc="get index.html")
            cmd = web.command('wget http://www.google.com/webhp?hl=en -O-')
            web.assert_that(cmd.stdout.content,
                            hamcrest.contains_string('value="I\'m Feeling Lucky"'))
