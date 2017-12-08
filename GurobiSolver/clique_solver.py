import argparse

from log import Log
from workspace import Workspace
from gurobi import Gurobi, ILP

class CliqueSolver(object):
    def __init__(self):
        self.workspace = Workspace()
        self.run_number = 1

        self.ilp_filename = None
        self.ilp = None

        self.parse_args()
        self.setup()
        self.run()

    def parse_args(self):
        """
        Takes in command line arguments and parses it into settings
        """
        # Define what can be taken as arguments
        parser = argparse.ArgumentParser()
        parser.add_argument('ilpFilename', help="The file containing your ILP formulation. It should end in .lp")
        parser.add_argument('-m', '--min', type=int, default=0, help="The minimum Objective Value to reach before we stop iterating. Stops when we reach this value. Default: 0.")
        parser.add_argument('-q', '--quiet', help="Include this flag if you don't want to see Gurobi output.", action='store_true')

        # Parse the actual arguments
        args = parser.parse_args()
        self.ilp_filename = args.ilpFilename
        self.quiet = args.quiet
        self.min = int(args.min)

    def setup(self):
        """
        Parse the ILP file into the ILP Object
        """
        self.ilp = ILP(self.ilp_filename)

    def run(self):
        """
        Continue running Gurobi until we're forced to break for some reason
        """
        while True:
            Log.println("Solver", "Starting Run #{}".format(self.run_number))

            # Create a space for gurobi to run
            self.workspace.create_run(self.run_number)

            # Run gurobi with the ILP
            gurobi = Gurobi(self.workspace.get_run(self.run_number), self.ilp, self.quiet)
            gurobi.run()

            # Check whether this returns a valid solution
            if gurobi.solution.infeasible or not len(gurobi.solution.vars[1]):
                Log.println("Solver", "This run results in an ILP that is infeasible. Quitting...")
                break

            if gurobi.solution.objective_value <= self.min:
                Log.println("Solver", "Reached minimum objective value of {}.".format(self.min))
                break;

            # Append this solution to the results file
            Log.println("Solver", "Found a solution: [{}]".format(", ".join(gurobi.solution.vars[1])))
            Log.println("Solver", "With Objective Value: {}".format(gurobi.solution.objective_value))
            self.write_solution(gurobi.solution)

            # Compile a new constraint to get different values
            # For every variable C(i) that set to 1, do
            # sum(C(i)) <= (# Of 1's Variables) - 1
            # This ensures that we don't select all of them again, but we can select a subset of them
            constraint = " + ".join(gurobi.solution.vars[1])
            constraint += " <= {}".format(len(gurobi.solution.vars[1]) - 1)

            # Add the constraint to the ILP
            Log.println("Solver", "Adding constraint: {}".format(constraint))
            self.ilp.add_constraint(constraint)

            # Go to the next run
            self.run_number += 1

        Log.println("Solver", "Complete! :)")

    def write_solution(self, solution):
        """
        Append a solution to the results file.
        Args:
            solution: A Solution Object, which we want to write to the results file
        """
        with open(self.workspace.join('results.txt'), 'a+') as f:
            solution_line = "{}: [{}]\n".format(solution.objective_value, ", ".join(solution.vars[1]))
            f.write(solution_line)
