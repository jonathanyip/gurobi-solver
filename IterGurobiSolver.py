import sys
import argparse

from gurobipy import GRB, read

class IterGurobiSolver(object):
    """
    Takes in a ILP file, and (using Gurobi Python API) iteratively tries to find all solutions
    """
    def __init__(self):
        self.ilp_filename = None
        self.num_solutions = None
        self.resultfile = None
        self.solutions = []

        self.parse_args()
        self.run_gurobi()

    def parse_args(self):
        """
        Get the arguments from the command line
        """
        parser = argparse.ArgumentParser()
        parser.add_argument('ilpFilename', help="The file containing your ILP formulation. It should end in .lp")
        parser.add_argument('-r', '--resultfile', help="Where to store the results.")
        parser.add_argument('-n', '--numSols', type=int, default=2000000000, help="Gets the n most optional solutions. Default: As many as possible.")

        args = parser.parse_args()
        self.ilp_filename = args.ilpFilename
        self.num_solutions = args.numSols
        self.resultfile = args.resultfile

    def run_gurobi(self):
        """
        Reads in the ILP file, and runs Gurobi
        """
        self.log("Running Gurobi...")
        model = read(self.ilp_filename)

        # Start the iterative approach
        run_number = 1
        while run_number <= self.num_solutions:
            # Allow Gurobi to print out stuff
            model.setParam(GRB.Param.OutputFlag, True)

            # Run Gurobi
            model.optimize()

            # Prevent Gurobi from printing out random junk, like how we set an attribute...
            model.setParam(GRB.Param.OutputFlag, False)

            # Check the model
            ret_code = self.check_model(model)
            if not ret_code:
                break

            # Retrieves the solutions and adds new constraints
            self.get_solution_and_add_constraints(model)

            # Go to the next run number
            run_number += 1

        self.log("Completed! :)")
        self.write_solutions()

    def check_model(self, model):
        """
        Checks the given model to see if it had any problems optimizing
        Returns True if the model is still OK.
        """
        if model.status != GRB.Status.OPTIMAL:
            if model.status == GRB.Status.INFEASIBLE:
                self.log("Model is infeasible.", error=True)
            elif model.status == GRB.Status.INF_OR_UNBD:
                self.log("Solution found was infinite or unbounded.", error=True)
            else:
                self.log("Gurobi exited with status {}.".format(model.status), error=True)
            return False
        return True

    def get_solution_and_add_constraints(self, model):
        """
        Given a model, gets the solution for one iteration
        """
        self.log("Found a solution!")
        this_solution = []

        # Get the solution count and variables
        solution_count = model.getAttr(GRB.Attr.SolCount)
        variables = model.getVars()

        obj_value = model.objVal

        this_solution.append("# Objective Value = {}".format(int(obj_value)))

        # Collect the variables that are set to 1
        ones_vars = []
        for var in variables:
            var_name = var.varName
            var_value = int(var.x)

            this_solution.append("{} {}".format(var_name, var_value))

            if var_value == 1:
                ones_vars.append(var)
        this_solution.append("")

        # Print the solution string to console
        solutions_string = "\n".join(this_solution)
        print(solutions_string)

        # Add this solution to the list of all solutions
        self.solutions += this_solution

        # Compile a new constraint to get different values
        # For every variable C(i) that set to 1, do
        # sum(C(i)) <= (# Of 1's Variables) - 1
        # This ensures that we don't select all of them again, but we can select a subset of them
        constraints = sum(ones_vars)
        model.addConstr(constraints <= (obj_value - 1))

    def write_solutions(self):
        """
        Write out solutions to file if specified
        """
        if self.resultfile:
            with open(self.resultfile, 'w+') as f:
                solutions_string = "\n".join(self.solutions)
                f.write(solutions_string)

    def log(self, string, error=False):
        """
        Prints out stuff
        """
        if error:
            print("[IterGurobiSolver:ERROR]: {}".format(string))
        else:
            print("[IterGurobiSolver]: {}".format(string))

if __name__ == "__main__":
    IterGurobiSolver()
