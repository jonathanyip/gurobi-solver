import os, errno

from log import Log

class Workspace(object):
    def __init__(self):
        self.path = None
        self.create_workspace()

    def create_workspace(self):
        """
        Attempts to create a results directory.
        If it exists already, try creating a directory with a suffixed number.
        """
        cwd = os.getcwd()
        path_format = os.path.join(cwd, 'results_{}')

        num = 1
        while True:
            try:
                path = path_format.format(str(num).zfill(3))
                os.makedirs(path)
                break
            except OSError as e:
                if e.errno != errno.EEXIST:
                    Log.error("Workspace", "Uh oh! Uncaught exception while trying to create the results folder!")
                    Log.error("Workspace", "Make sure we have permissions to edit this folder!")
                    raise
                num += 1

        self.path = path

    def join(self, *args, **kwargs):
        """
        Joins the path with the workspace path
        Args:
            The same as os.path.join()
        Kwargs:
            The same as os.path.join()
        """
        return os.path.join(self.path, *args, **kwargs)

    def create_run(self, run_number):
        """
        Creates a working directory for this run
        Args:
            run_number: The number of this run
        """
        os.makedirs(self.join(str(run_number).zfill(3)))

    def get_run(self, run_number, filename=None):
        """
        Returns path to this particular run directory
        Args:
            run_number: The number of this run
        Kwargs:
            filename: If filename is set, then we append the filename to the path
        """
        if filename:
            return self.join(str(run_number).zfill(3), filename)
        return self.join(str(run_number).zfill(3))
