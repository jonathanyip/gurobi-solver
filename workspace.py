import errno
import os
import sys
import shutil

class Workspace:
    DEFAULT_PATH = 'work'

    def __init__(self, path, ilp_filename, force_save):
        """
        Tries to create the directory to store all of our work
        """
        # Set the default workspace
        if not path:
            path = Workspace.DEFAULT_PATH

        # Make it in the current working directory
        cwd = os.getcwd()
        self.base_path = os.path.join(cwd, path)

        # If forced, remove the directory first
        if force_save:
            shutil.rmtree(self.base_path)

        # Try to make the directory
        try:
            os.makedirs(self.base_path)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
            print("Directory {} that we were going to use for the workspace already exists!".format(self.base_path))
            print("Please delete/move it, specify a new workspace using the -w flag, or specify the -f flag to override it.")
            exit(1)
        
        # Try to copy over the ILP formulation
        self.base_ilp = self.join('base.lp')

        try:
            shutil.copyfile(ilp_filename, self.base_ilp)
        except IOError as e:
            print("Couldn't copy the ILP .lp file. Are you sure you typed it in correctly?")
            exit(1)

    def create_run(self, run_number):
        """
        Creates a directory for this run to run in.
        Makes a copy of the ILP in that directory so it can be edited and used.
        """
        run_path = self.join(run_number)
        os.makedirs(run_path)

    def get_base_ilp(self):
        """
        :returns: The path to the base ILP formulation
        """
        return self.base_ilp

    def join(self, *paths):
        """
        Joins the provided path with the workspace directory
        :param *path: Variable number of paths to join
        :returns: The provided path with the workspace directory
        """
        return os.path.join(self.base_path, *[str(p) for p in paths])