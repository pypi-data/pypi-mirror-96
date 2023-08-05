#!/usr/bin/env python3
'''
    Run a command using python subprocess.

    Copyright 2018-2020 DeNova
    Last modified: 2021-02-02
'''

from glob import glob
from os import waitpid
from queue import Queue
import shlex
import subprocess
import sys
from threading import Thread
from time import sleep

# log init delayed to avoid circular imports
log = None

def run(*command_args, **kwargs):
    ''' Run a command line.

        Much simpler than using python subprocess directly.

        Returns subprocess.CompletedProcess, or raises
        subprocess.CalledProcessError.

        Example::

            >>> result = run('echo', 'word1', 'word2')
            >>> result.stdout
            'word1 word2'

        By default run() captures stdout and stderr. It returns a
        subprocess.CompletedProcess with stdout and stderr, plus a
        combined stderrout as a string. Use run_verbose() if you
        want stdout and stderr to be redirected to sys.stdout and sys.stderr.

        Each command line arg should be a separate run() arg so
        subprocess.check_output can escape args better.

        Unless output_bytes=True, the .stdout, and .stderr attributes
        of CompletedProcess are returned as unicode strings, not
        bytes. For example stdout is returned as stdout.decode().strip().
        The default is output_bytes=False. This is separate from
        universal_newlines processing, and does not affect stdin.

        Unless glob=False, args are globbed.

        Except for 'output_bytes' and 'glob', keyword args are passed
        to subprocess.run().

        On error raises subprocess.CalledProcessError.
        The error has an extra data member called 'output' which is a
        string containing stderr and stdout.

        To see the program's output when there is an error::

            try:
                run(...)

            except subprocess.CalledProcessError as cpe:
                print(cpe)
                print(f'error output: {cpe.stderrout}')

        'stderrout' combines both stderr and stdout. You can also choose
        just 'stderr' or 'stdout'.

        Because we are using PIPEs, we need to use Popen() instead of
        run(), and call Popen.communicate() to avoid zombie processes.
        But to get run()'s timeout, input and check params, we don't.
        Zombie processes are worrisome, but do no real harm.

        See https://stackoverflow.com/questions/2760652/how-to-kill-or-avoid-zombie-processes-with-subprocess-module

        run() does not process special shell characters. It treats
        them as plain strings.

        >>> from tempfile import gettempdir
        >>> tmpdir = gettempdir()
        >>> command_args = ['ls', '-l', f'{tmpdir}/denova*']
        >>> kwargs = {}
        >>> result = run(*command_args, **kwargs)
        >>> result.returncode
        0
        >>> len(result.args) > 3
        True

        >>> from tempfile import gettempdir
        >>> tmpdir = gettempdir()
        >>> command_args = ['ls', '-l', f'{tmpdir}/denova*']
        >>> kwargs = {'glob': False, 'shell': True}
        >>> result = run(*command_args, **kwargs)
        >>> result.args
        ['ls', '-l', '/tmp/denova*']
        >>> result.returncode
        0

        >>> command_args = ['echo', '"denova*"']
        >>> result = run(*command_args)
        >>> result.args
        ['echo', '"denova*"']
        >>> result.returncode
        0
    '''

    _init_log()
    result = None

    try:
        args, kwargs = get_run_args(*command_args, **kwargs)

        log(f'args: {args}')
        if kwargs:
            log(f'kwargs: {kwargs}')

        if 'output_bytes' in kwargs:
            output_bytes = kwargs['output_bytes']
            del kwargs['output_bytes']
            log(f'output bytes: {output_bytes}')
        else:
            output_bytes = False

        for output in ['stdout', 'stderr']:
            if output not in kwargs:
                kwargs[output] = subprocess.PIPE

        result = subprocess.run(args,
                                check=True,
                                **kwargs)

    except subprocess.CalledProcessError as cpe:
        handle_run_error(command_args, cpe)
        raise

    except Exception as e:
        log(f'command got Exception: {command_args}')
        log(f'error NOT subprocess.CalledProcessError: {type(e)}')
        log(e)
        raise

    else:
        result = format_output(result)

    return result

def run_verbose(*args, **kwargs):
    ''' Run program with stdout and stderr directed to
        sys.stdout and sys.stderr.

        Doctests can't have stdout redirected so we disable interactive in
        the following test. Under normal circumstances you don't want to set
        interactive to False. If you do not want the command to run interactive,
        just use the run() function.

        >>> from tempfile import gettempdir
        >>> tmpdir = gettempdir()
        >>> kwargs = {'interactive': False}
        >>> command_args = ['ls', '-l', f'{tmpdir}']
        >>> result = run_verbose(*command_args, **kwargs)
        >>> result.args
        ['ls', '-l', '/tmp']
        >>> result.returncode
        0
    '''

    if kwargs is None:
        kwargs = {}

    if 'interactive' not in kwargs:
        kwargs['interactive'] = True

    result = run(*args, **kwargs)

    return result

def background(*command_args, **kwargs):
    ''' Run a command line in background.

        If your command file is not executable and starts with '#!',
        background() will use 'shell=True'.

        Passes along all keywords to subprocess.Popen().
        That means you can force the subprocess to run in the foreground
        with e.g. timeout= or check=. But command.run() is a better
        choice for this case.

        Returns a subprocess.Popen object, or raises
        subprocess.CalledProcessError.

        If you redirect stdout/stderr, be sure to catch execution errors:

            This example is not a doctest because doctests spoof sys.stdout.
            try:
                command_args = ['python', '-c', 'not python code']
                kwargs = {'stdout': sys.stdout, 'stderr': sys.stderr}
                program = background(*command_args, **kwargs)
                wait(program)
            except Exception as exc:
                print(exc)

        The caller can simply ignore the return value, poll() for when
        the command finishes, wait() for the command, or communicate()
        with it.

        Do not use Popen.wait(). Use denova.os.command.wait().

        >>> program = background('sleep', '0.5')

        >>> print('before')
        before

        >>> wait(program)

        >>> print('after')
        after

    '''

    if not command_args:
        raise ValueError('missing command')

    _init_log()

    # if there is a single string arg with a space, it's a command line string
    if len(command_args) == 1 and isinstance(command_args[0], str) and ' ' in command_args[0]:
        # run() is better able to add quotes correctly when each arg is separate
        command_args = shlex.split(command_args[0])

    command_str = ' '.join(command_args)
    kwargs_str = ''
    for key in kwargs:
        if kwargs_str:
            kwargs_str = kwargs_str + ', '
        kwargs_str = kwargs_str + f'{key}={kwargs[key]}'

    try:
        process = subprocess.Popen(command_args, **kwargs)

    except OSError as ose:
        log.debug(f'command: {command_str}')
        log.debug(f'kwargs: {kwargs_str}')
        log.exception()

        if ose.strerror:
            if 'Exec format error' in ose.strerror:
                # if the program file starts with '#!' retry with 'shell=True'.
                program_file = command_args[0]
                with open(program_file) as program:
                    first_chars = program.read(2)
                    if str(first_chars) == '#!':

                        process = subprocess.Popen(command_args, shell=True, **kwargs)

                    else:
                        log.debug(f'no #! in {program_file}')
                        raise

            else:
                raise

        else:
            raise

    except Exception as e:
        log.debug(f'command: {command_str}')
        log.debug(f'kwargs: {kwargs_str}')
        log.debug(e)
        raise

    else:
        log.debug(f"background process started: \"{' '.join(process.args)}\", pid: {process.pid}")
        return process

def get_run_args(*command_args, **kwargs):
    '''
        Get the args in list with each item a string.

        >>> _init_log()

        >>> from tempfile import gettempdir
        >>> command_args = ['ls', '-l', gettempdir()]
        >>> kwargs = {}
        >>> get_run_args(*command_args, **kwargs)
        (['ls', '-l', '/tmp'], {})

        >>> # test command line with glob=False
        >>> tmpdir = gettempdir()
        >>> command_args = ['ls', '-l', f'{gettempdir()}/denova*']
        >>> kwargs = {'glob': False}
        >>> get_run_args(*command_args, **kwargs)
        (['ls', '-l', '/tmp/denova*'], {})
    '''

    if kwargs is None:
        kwargs = {}

    if 'interactive' in kwargs:
        if kwargs['interactive']:
            del kwargs['interactive']
            kwargs.update(dict(stdin=sys.stdin,
                               stdout=sys.stdout,
                               stderr=sys.stderr))
        else:
            del kwargs['interactive']

    if 'glob' in kwargs:
        globbing = kwargs['glob']
        del kwargs['glob']
    else:
        globbing = True

    # subprocess.run() wants strings
    args = []
    for arg in command_args:
        arg = str(arg)

        # see if the arg contains an inner string so we don't mistake that inner string
        # containing any wildcard chars. e.g., arg = '"this is an * example"'
        encased_str = ((arg.startswith('"') and arg.endswith('"')) or
                       (arg.startswith("'") and arg.endswith("'")))

        if ('*' in arg or '?' in arg):
            if globbing and not encased_str:
                args.extend(glob(arg))
                log(f'globbed: {arg}')
            else:
                args.append(arg)
        else:
            args.append(arg)

    return args, kwargs

def format_output(result):
    '''
        Format the output from a run().

        result = format_output({'returncode': 0, 'stdout': b'Hello ', 'stderr: None})
        result.returncode == 0
        True
        result.stdout
        'Hello'
    '''

    if (result.stdout is not None) and (not isinstance(result.stdout, str)):
        result.stdout = result.stdout.decode()
        result.stdout = result.stdout.strip()
    if (result.stderr is not None) and (not isinstance(result.stderr, str)):
        result.stderr = result.stderr.decode()
        result.stderr = result.stderr.strip()

    return result

def handle_run_error(command_args, cpe):
    '''
        Handle an error from run().
    '''

    command_str = ' '.join(map(str, command_args))

    log(f'command failed. "{command_str}", returncode: {cpe.returncode}')
    log(f'cpe: {cpe}')
    log(cpe) # DEBUG

    cpe.stderrout = None
    if cpe.stderr:
        err = cpe.stderr.decode().strip()
        log(f'stderr:\n{err}')
        cpe.stderrout = err
    if cpe.stdout:
        out = cpe.stdout.decode().strip()
        log(f'stdout:\n{out}')
        if cpe.stderrout is None:
            cpe.stderrout = out
        else:
            cpe.stderrout = cpe.stderrout + '\n' + out

    """ delete if unused 2021-03-01
    if cpe.stderr and cpe.stdout:
        cpe.stderrout = (cpe.stderr.decode().strip() +
                         '/n' +
                         cpe.stdout.decode().strip())
    elif cpe.stderr:
        cpe.stderrout = cpe.stderr.decode().strip()
    elif cpe.stdout:
        cpe.stderrout = cpe.stdout.decode().strip()

    if cpe.stderrout:
        log(f'cpe stderr and stdout:\n{cpe.stderrout}')
    """

def nice(*command_args, **kwargs):
    ''' Run a command line at low priority, for both cpu and io.

        This can greatly increases responsiveness of the user interface.

        nice() effective prefixes the command with::

            nice nice ionice -c 3 ...

        In Debian 10 "buster" ionice must be applied on the command line
        immediately before the executable task. This means our 'nicer'
        and 'ionicer' bash scripts don't work. nice() does.

        Because ionice must be used immediately before the executable
        task, commands like this won't work as expected::

            nice(['tar', 'cvf', 'test.tar', gettempdir()])

        In this case only 'bash' will get the effect of ionice, not 'tar'.

        #>>> shared_host = nice('this-is-sharedhost')
        #>>> shared_host.stderr
        #''
        #>>> print('sharedhost' in shared_host.stdout)
        #True
    '''

    nice_args = ['nice', 'nice', 'ionice', '--class', '3']
    args = nice_args + list(command_args)
    return run(*args, **kwargs)

def nice_args(*command_args):
    ''' Modify command to run at low priority. '''

    return ('nice', 'nice', 'ionice', '--class', '3') + tuple(command_args)

def wait(program):
    ''' Wait for a background command to finish.

        >>> program = background('sleep', '0.5')

        >>> print('before')
        before

        >>> wait(program)

        >>> print('after')
        after
    '''

    if not isinstance(program, subprocess.Popen):
        raise ValueError('program must be an instance of subprocess.Popen')

    waitpid(program.pid, 0)

def _init_log():
    ''' Initialize log. '''

    global log

    if log is None:
        # log import delayed to avoid recursive import.
        from denova.python.log import Log
        log = Log()

def show_stderr(*proc_args, **kwargs):
    '''
        How to print program's stderr
        This also handles unicode encoded bytestreams better

        Currently unused.
    '''

    class CompletedProcessStub:
        pass

    proc = subprocess.Popen(proc_args,
                            **kwargs)

    # stderr to the console's stdout
    proc_stderr = ''
    err_data = proc.stderr.readline()
    while err_data:
        line = err_data.decode()
        proc_stderr = proc_stderr + line
        # lines already have a newline
        print(line, end='')
        err_data = proc.stderr.readline()

    # get any stdout from the proc
    proc_stdout, _ = proc.communicate()

    result = CompletedProcessStub()
    result.resultcode = proc.wait()
    result.stdout = proc_stdout
    result.stderr = proc_stderr


if __name__ == "__main__":
    import doctest
    doctest.testmod()
