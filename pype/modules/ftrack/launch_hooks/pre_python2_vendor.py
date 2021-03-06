import os
from pype.lib import PreLaunchHook
from pype.modules.ftrack import FTRACK_MODULE_DIR


class PrePyhton2Support(PreLaunchHook):
    """Add python ftrack api module for Python 2 to PYTHONPATH.

    Path to vendor modules is added to the beggining of PYTHONPATH.
    """
    # There will be needed more granular filtering in future
    app_groups = ["maya", "nuke", "nukex", "hiero", "nukestudio"]

    def execute(self):
        # Prepare vendor dir path
        python_2_vendor = os.path.join(FTRACK_MODULE_DIR, "python2_vendor")

        # Add Python 2 modules
        python_paths = [
            # `python-ftrack-api`
            os.path.join(python_2_vendor, "ftrack-python-api", "source"),
            # `arrow`
            os.path.join(python_2_vendor, "arrow"),
            # `builtins` from `python-future`
            # - `python-future` is strict Python 2 module that cause crashes
            #   of Python 3 scripts executed through pype (burnin script etc.)
            os.path.join(python_2_vendor, "builtins"),
            # `backports.functools_lru_cache`
            os.path.join(
                python_2_vendor, "backports.functools_lru_cache"
            )
        ]

        # Load PYTHONPATH from current launch context
        python_path = self.launch_context.env.get("PYTHONPATH")
        if python_path:
            python_paths.append(python_path)

        # Set new PYTHONPATH to launch context environments
        self.launch_context.env["PYTHONPATH"] = os.pathsep.join(python_paths)
