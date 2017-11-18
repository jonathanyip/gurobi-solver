import argparse
import subprocess
import sys

from workspace import Workspace

class Solver:
    def __init__(self):
        self.run_number = 0

        self.vars = set()
        self.workspace = None

        self.pause = True
        self.show_gurobi = True

        self.parse_arguments()
        self.parse_vars()
        self.run()

    def parse_arguments(self):
        """
        Takes in command line arguments and parses it into settings
        """
        # Define what can be taken as arguments
        parser = argparse.ArgumentParser()
        parser.add_argument('ilp_filename', help="The file containing your ILP formulation. It should end in .lp")
        parser.add_argument('vars_filename', help="The file containing a newline-separated list of variables, which we should try and get all feasible combinations of.")
        parser.add_argument('-w', '--workspace', help="The name of the directory to store our work. It will be created in the current working directory. Default is 'work'")
        parser.add_argument('-f', '--force-save', help="Overrides the workspace directory, if it exists.", action='store_true')
        parser.add_argument('-g', '--no-gurobi-output', help="Set to disable gurobi output.", action='store_true')
        parser.add_argument('-n', '--no-pause', help="Set to disable pausing after each run.", action='store_true')

        # Parse the actual arguments
        args = parser.parse_args()
        self.workspace = Workspace(args.workspace, args.ilp_filename, args.force_save)
        self.vars_filename = args.vars_filename
        self.pause = not args.no_pause
        self.show_gurobi = not args.no_gurobi_output

    def parse_vars(self):
        """
        Parses the list of variables and stores it in a set
        """
        vars_list = []
        with open(self.vars_filename, 'r') as f:
            lines = [x.strip() for x in f.readlines()]
        
        for line in lines:
            if line != '':
                vars_list.append(line)
        
        self.vars = set(vars_list)

    def run(self):
        # Increment the run number
        self.run_number += 1
        self.workspace.create_run(self.run_number)

        print("Run #{} ==============================".format(str(self.run_number).zfill(4)))

        self.modify_ilp()
        self.run_gurobi()
        self.analyze_results()

        print("========================================")

        # Pause so we can see the results
        if self.pause:
            raw_input()

    def modify_ilp(self):
        """
        Modify the ILP to find new solutions
        """
        pass

    def run_gurobi(self):
        """
        Execute gurobi using the ILP file generated, writing the output to file and to stdout.
        """
        print("Gurobi =================================")

        output_file = self.workspace.join(self.run_number, 'gurobi.out')
        solution_file = self.workspace.join(self.run_number, 'solution.sol')
        ilp_file = self.workspace.join(self.run_number, 'formula.lp')

        with open(output_file, 'w+') as f:
            gurobi = subprocess.Popen(['gurobi_cl', 'resultfile={}'.format(solution_file), ilp_file], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in iter(gurobi.stdout.readline, ''):
                if self.show_gurobi:
                    sys.stdout.write(line)
                f.write(line)

    def analyze_results(self):
        """
        Read the solution file and determine what's been set to 1
        """
        print("Results ================================")
        solution_file = self.workspace.join(self.run_number, 'solution.sol')

        with open(solution_file, 'r') as f:
            lines = [x.strip() for x in f.readlines()]
        
        for line in lines:
            # If the last characters are ' 1', then this variable is 1
            if line[-2:] == ' 1':
                # Extract everything except the last two characters
                variable = line[:-2]
