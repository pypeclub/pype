import logging
import os
import subprocess

from .log import PypeLogger as Logger

log = logging.getLogger(__name__)


def execute(args,
            silent=False,
            cwd=None,
            env=None,
            shell=None):
    """Execute command as process.

    This will execute given command as process, monitor its output
    and log it appropriately.

    .. seealso::

        :mod:`subprocess` module in Python.

    Args:
        args (list): list of arguments passed to process.
        silent (bool): control output of executed process.
        cwd (str): current working directory for process.
        env (dict): environment variables for process.
        shell (bool): use shell to execute, default is no.

    Returns:
        int: return code of process

    """

    log_levels = ['DEBUG:', 'INFO:', 'ERROR:', 'WARNING:', 'CRITICAL:']

    log = Logger().get_logger('execute')
    log.info("Executing ({})".format(" ".join(args)))
    popen = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1,
        cwd=cwd,
        env=env or os.environ,
        shell=shell
    )

    # Blocks until finished
    while True:
        line = popen.stdout.readline()
        if line == '':
            break
        if silent:
            continue
        line_test = False
        for test_string in log_levels:
            if line.startswith(test_string):
                line_test = True
                break
        if not line_test:
            print(line[:-1])

    log.info("Execution is finishing up ...")

    popen.wait()
    return popen.returncode


def run_subprocess(*args, **kwargs):
    """Convenience method for getting output errors for subprocess.

    Output logged when process finish.

    Entered arguments and keyword arguments are passed to subprocess Popen.

    Args:
        *args: Variable length arument list passed to Popen.
        **kwargs : Arbitary keyword arguments passed to Popen. Is possible to
            pass `logging.Logger` object under "logger" if want to use
            different than lib's logger.

    Returns:
        str: Full output of subprocess concatenated stdout and stderr.

    Raises:
        RuntimeError: Exception is raised if process finished with nonzero
            return code.
    """

    # Get environents from kwarg or use current process environments if were
    # not passed.
    env = kwargs.get("env") or os.environ
    # Make sure environment contains only strings
    filtered_env = {k: str(v) for k, v in env.items()}

    # Use lib's logger if was not passed with kwargs.
    logger = kwargs.pop("logger", log)

    # set overrides
    kwargs['stdout'] = kwargs.get('stdout', subprocess.PIPE)
    kwargs['stderr'] = kwargs.get('stderr', subprocess.PIPE)
    kwargs['stdin'] = kwargs.get('stdin', subprocess.PIPE)
    kwargs['env'] = filtered_env

    proc = subprocess.Popen(*args, **kwargs)

    full_output = ""
    _stdout, _stderr = proc.communicate()
    if _stdout:
        _stdout = _stdout.decode("utf-8")
        full_output += _stdout
        logger.debug(_stdout)

    if _stderr:
        _stderr = _stderr.decode("utf-8")
        # Add additional line break if output already containt stdout
        if full_output:
            full_output += "\n"
        full_output += _stderr
        logger.warning(_stderr)

    if proc.returncode != 0:
        exc_msg = "Executing arguments was not successful: \"{}\"".format(args)
        if _stdout:
            exc_msg += "\n\nOutput:\n{}".format(_stdout)

        if _stderr:
            exc_msg += "Error:\n{}".format(_stderr)

        raise RuntimeError(exc_msg)

    return full_output
