import os
import subprocess

from collections import defaultdict
from log import Log

class ILP(object):
    """
    Represents an ILP formulation
    Attributes:
        objective: The objective function
        constraints: A list of constrains
        binary_variables: A list of binary variables
    """
    def __init__(self, filename=None):
        """
        Kwargs:
            filename: If provided, will parse this ILP file
        """
        self.objective = ""
        self.constraints = []
        self.binary_variables = []

        if filename:
            self.parse_ilp(filename)

    def parse_ilp(self, filename):
        """
        Parses an ILP file
        Args:
            filename: The location of the .lp file
        """
        with open(filename, 'r') as f:
            lines = [x.strip() for x in f.readlines()]

        # Parse the ILP file
        begin_constraints = False
        begin_binary_variables = False

        for line in lines:
            if not line:
                continue

            lower = line.lower()
            if any(x in lower for x in ['subject to', 'such that', 's.t.']):
                # If constraints, start collecting them
                begin_constraints = True
                begin_binary_variables = False
            elif any(x in lower for x in ['binary', 'binaries', 'bin']):
                # If binary variables, start collecting them
                begin_binary_variables = True
                begin_constraints = False
            elif any(x in lower for x in ['general', 'generals', 'gen', 'semi-continuous', 'semis', 'semi', 'sos', 'pwlobj', 'lazy constraints']):
                # If some other gurobi syntax thing, ignore it, as this is ILP only
                begin_binary_variables = False
                begin_constraints = False
            elif any(x in lower for x in ['maximize', 'minimize', 'minimum', 'maximum', 'max', 'min']):
                self.set_objective(line)
            elif 'end' in lower:
                break
            elif begin_constraints:
                self.add_constraint(line)
            elif begin_binary_variables:
                self.add_binary_variable(line)

    def set_objective(self, objective):
        """
        Changes the objective function to the provided objective function
        Args:
            objective: What to change the objective to
        """
        self.objective = objective

    def add_constraint(self, constraint):
        """
        Adds this constraint to this ILP
        Args:
            constraint: The constraint to add
        """
        self.constraints.append(constraint)

    def add_binary_variable(self, var):
        """
        Adds a binary variable to this ILP
        Args:
            var: The binary variable to add
        """
        self.binary_variables.append(var)

    def save(self, filename):
        """
        Saves the ILP file to the specified filename
        Args:
            filename: The name of where to save it
        """
        with open(filename, 'w+') as f:
            f.write(self.objective + '\n')
            f.write('such that\n')
            for constraint in self.constraints:
                f.write(constraint + '\n')
            f.write('binary\n')
            for binary in self.binary_variables:
                f.write(binary + '\n')
            f.write('end\n')

class Solution(object):
    """
    Represents the solutions from Gurobi
    Attributes:
        infeasible: Set to True if this ILP is infeasible!
        objective_value: Contains the objective value
        vars: A dictionary of lists, which contains variables. Keys are the values of those variables.
            Example:
            {
                0: ['C(0)', 'C(1)'],
                1: ['C(2)', 'C(3)'],
                ...
            }
    """
    def __init__(self, filename):
        """
        Args:
            filename: The name of the solutions file to parse
        """
        with open(filename, 'r') as f:
            lines = [x.strip() for x in f.readlines()]

        # Solution file is blank. Must be infeasible...
        self.infeasible = False
        if not len(lines):
            self.infeasible = True
            return

        # The first line should contain the objective value
        self.objective_value = int(lines[0][20:])
        self.vars = defaultdict(list)

        for line in lines[1:]:
            if not line:
                continue

            var, number = line.split()
            self.vars[int(number)].append(var)

class Gurobi(object):
    """
    Represents a runnable Gurobi configuration
    Attributes:
        ilp: The ILP Object that Gurobi will run
        solution: The Solution Object that contains the solution.
            Must call self.run() before using!
    """

    def __init__(self, working_dir, ilp, silent=False):
        """
        Args:
            working_dir: Where Gurobi should save all its files
            ilp: ILP that Gurobi will run (ILP Object)
            silent: Whether Gurobi should be silent, and not print out anything
        """
        self.ilp = ilp
        self.solution = None
        self.silent = silent

        self.output_filename = os.path.join(working_dir, 'output.txt')
        self.ilp_filename = os.path.join(working_dir, 'ilp.lp')
        self.result_filename = os.path.join(working_dir, 'results.sol')

    def run(self):
        """
        Runs Gurobi
        """
        Log.println('Gurobi', "Running Gurobi command...", color=Log.colors.GREEN)

        # Save the gurobi ILP file, so gurobi can run it
        self.ilp.save(self.ilp_filename)

        # Run the gurobi command
        with open(self.output_filename, 'w+') as f:
            gurobi = subprocess.Popen(['gurobi_cl', 'resultfile={}'.format(self.result_filename), self.ilp_filename], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in iter(gurobi.stdout.readline, ''):
                if not self.silent:
                    Log.write('Gurobi', line, color=Log.colors.GREEN)
                f.write(line)

        # Save the solution
        self.solution = Solution(self.result_filename)
