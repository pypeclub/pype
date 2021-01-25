# -*- coding: utf-8 -*-
"""Main entry point for Pype command.

Bootstrapping process of Pype is as follows:

`PYPE_PATH` is checked for existence - either one from environment or
from user settings. Precedence takes the one set by environment.

On this path we try to find zip files with `pype-repositories-v3.x.x.zip`
format.

If no Pype repositories are found in `PYPE_PATH (user data dir)
then **Igniter** (Pype setup tool) will launch its GUI.

It can be used to specify `PYPE_PATH` or if it is _not_ specified, current
*"live"* repositories will be used to create such zip file and copy it to
appdata dir in user home. Version will be determined by version specified
in Pype module.

If Pype repositories zip file is found in default install location
(user data dir) or in `PYPE_PATH`, it will get list of those zips there and
use latest one or the one specified with optional `--use-version` command
line argument. If the one specified doesn't exist then latest available
version will be used. All repositories in that zip will be added
to `sys.path` and `PYTHONPATH`.

If Pype is live (not frozen) then current version of Pype module will be
used. All directories under `repos` will be added to `sys.path` and
`PYTHONPATH`.

Pype depends on connection to `MongoDB`_. You can specify MongoDB connection
string via `AVALON_MONGO` set in environment or it can be set in user
settings or via **Igniter** GUI.

Todo:
    Move or remove bootstrapping environments out of the code.

.. _MongoDB:
   https://www.mongodb.com/

"""
import os
import re
import sys
import traceback

from igniter.tools import load_environments, add_acre_to_sys_path

from igniter import BootstrapRepos

try:
    import acre
except ImportError:
    add_acre_to_sys_path()
    import acre


def set_environments() -> None:
    """Set loaded environments.

    .. todo:
        better handling of environments

    """
    # FIXME: remove everything except global
    env = load_environments(["global"])
    env = acre.merge(env, dict(os.environ))
    os.environ.clear()
    os.environ.update(env)


def set_modules_environments():
    """Set global environments for pype's modules.

    This requires to have pype in `sys.path`.
    """

    from pype.modules import ModulesManager

    modules_manager = ModulesManager()

    module_envs = modules_manager.collect_global_environments()
    publish_plugin_dirs = modules_manager.collect_plugin_paths()["publish"]

    # Set pyblish plugins paths if any module want to register them
    if publish_plugin_dirs:
        publish_paths_str = os.environ.get("PYBLISHPLUGINPATH") or ""
        publish_paths = publish_paths_str.split(os.pathsep)
        _publish_paths = set()
        for path in publish_paths:
            if path:
                _publish_paths.add(os.path.normpath(path))
        for path in publish_plugin_dirs:
            _publish_paths.add(os.path.normpath(path))
        module_envs["PYBLISHPLUGINPATH"] = os.pathsep.join(_publish_paths)

    # Metge environments with current environments and update values
    if module_envs:
        parsed_envs = acre.parse(module_envs)
        env = acre.merge(parsed_envs, dict(os.environ))
        os.environ.clear()
        os.environ.update(env)


def boot():
    """Bootstrap Pype."""

    from pype.lib.terminal_splash import play_animation
    play_animation()

    # find pype versions
    bootstrap = BootstrapRepos()
    pype_versions = bootstrap.find_pype()

    # check for `--use-version=3.0.0` argument.
    use_version = None

    for arg in sys.argv:
        m = re.search(r"--use-version=(?P<version>\d+\.\d+\.\d*.+?)", arg)
        if m and m.group('version'):
            use_version = m.group('version')
            break

    if not os.getenv("PYPE_MONGO"):
        try:
            pype_mongo = bootstrap.registry.get_secure_item("pypeMongo")
        except ValueError:
            print("*** No DB connection string specified.")
            print("--- launching setup UI ...")
            import igniter
            igniter.run()
            return
        else:
            os.environ["PYPE_MONGO"] = pype_mongo

    set_environments()
    if getattr(sys, 'frozen', False):
        if not pype_versions:
            import igniter
            igniter.run()

        version_path = BootstrapRepos.get_version_path_from_list(
            use_version, pype_versions)
        if version_path:
            # use specified
            bootstrap.add_paths_from_archive(version_path)

        else:
            if use_version is not None:
                print(("!!! Specified version was not found, using "
                       "latest available"))
            # use latest
            version_path = pype_versions[-1].path
            bootstrap.add_paths_from_archive(version_path)
            use_version = str(pype_versions[-1])

        os.environ["PYPE_ROOT"] = version_path.as_posix()
    else:
        # run through repos and add them to sys.path and PYTHONPATH
        pype_root = os.path.dirname(os.path.realpath(__file__))
        local_version = bootstrap.get_local_version()
        if use_version and use_version != local_version:
            version_path = BootstrapRepos.get_version_path_from_list(
                use_version, pype_versions)
            if version_path:
                # use specified
                bootstrap.add_paths_from_archive(version_path)

        os.environ["PYPE_ROOT"] = pype_root
        repos = os.listdir(os.path.join(pype_root, "repos"))
        repos = [os.path.join(pype_root, "repos", repo) for repo in repos]
        # add self to python paths
        repos.insert(0, pype_root)
        for repo in repos:
            sys.path.append(repo)

        pythonpath = os.getenv("PYTHONPATH", "")
        paths = pythonpath.split(os.pathsep)
        paths += repos
        os.environ["PYTHONPATH"] = os.pathsep.join(paths)

    # DEPRECATED: remove when `pype-config` dissolves into Pype for good.
    # .-=-----------------------=-=. ^ .=-=--------------------------=-.
    os.environ["PYPE_MODULE_ROOT"] = os.environ["PYPE_ROOT"]

    # delete Pype module from cache so it is used from specific version
    try:
        del sys.modules["pype"]
        del sys.modules["pype.version"]
    except AttributeError:
        pass

    from pype import cli
    from pype.lib import terminal as t
    from pype.version import __version__
    print(">>> loading environments ...")
    set_environments()
    set_modules_environments()

    info = get_info()
    info.insert(0, ">>> Using Pype from [ {} ]".format(
        os.path.dirname(cli.__file__)))

    info_length = len(max(info, key=len))
    info.insert(0, f"*** Pype [{__version__}] " + "-" * info_length)
    for i in info:
        t.echo(i)

    try:
        cli.main(obj={}, prog_name="pype")
    except Exception:
        exc_info = sys.exc_info()
        print("!!! Pype crashed:")
        traceback.print_exception(*exc_info)
        sys.exit(1)


def get_info() -> list:
    """Print additional information to console."""
    from pype.lib.mongo import get_default_components
    from pype.lib.log import PypeLogger

    components = get_default_components()

    infos = []
    if not getattr(sys, 'frozen', False):
        infos.append(("Pype variant", "staging"))
    else:
        infos.append(("Pype variant", "production"))
    infos.append(("Running pype from", os.environ.get('PYPE_ROOT')))
    infos.append(("Using mongodb", components["host"]))

    if os.environ.get("FTRACK_SERVER"):
        infos.append(("Using FTrack at",
                      os.environ.get("FTRACK_SERVER")))

    if os.environ.get('DEADLINE_REST_URL'):
        infos.append(("Using Deadline webservice at",
                      os.environ.get("DEADLINE_REST_URL")))

    if os.environ.get('MUSTER_REST_URL'):
        infos.append(("Using Muster at",
                      os.environ.get("MUSTER_REST_URL")))

    # Reinitialize
    PypeLogger.initialize()

    log_components = PypeLogger.log_mongo_url_components
    if log_components["host"]:
        infos.append(("Logging to MongoDB", log_components["host"]))
        infos.append(("  - port", log_components["port"] or "<N/A>"))
        infos.append(("  - database", PypeLogger.log_database_name))
        infos.append(("  - collection", PypeLogger.log_collection_name))
        infos.append(("  - user", log_components["username"] or "<N/A>"))
        if log_components["auth_db"]:
            infos.append(("  - auth source", log_components["auth_db"]))

    maximum = max([len(i[0]) for i in infos])
    formatted = []
    for info in infos:
        padding = (maximum - len(info[0])) + 1
        formatted.append(
            "... {}:{}[ {} ]".format(info[0], " " * padding, info[1]))
    return formatted


if __name__ == "__main__":
    boot()