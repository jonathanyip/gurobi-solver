import sys
import argparse

from gurobipy import GRB, read

class NativeGurobiSolver(object):
    """
    Takes in a ILP file, and (using Gurobi Python API) natively tries to find all solutions
    """

    def __init__(self):
        self.ilp_filename = None
        self.num_solutions = None
        self.resultfile = None

        self.parse_args()
        self.run_gurobi()

    def parse_args(self):
        """
        Get the arguments from the command line
        """
        parser = argparse.ArgumentParser()
        parser.add_argument('ilpFilename', help="The file containing your ILP formulation. It should end in .lp")
        parser.add_argument('-r', '--resultfile', help="Where to store the results.")
        parser.add_argument('-n', '--numSols', default=2000000000, help="Gets the n most optional solutions. Default: As many as Gurobi can handle (2 billion).")

        args = parser.parse_args()
        self.ilp_filename = args.ilpFilename
        self.num_solutions = args.numSols
        self.resultfile = args.resultfile

    def run_gurobi(self):
        """
        Reads in the ILP file, and runs Gurobi
        """
        model = read(self.ilp_filename)

        # Search for as many solutions as possible
        model.setParam(GRB.Param.PoolSearchMode, 2)

        # Store as many solutions as specified, or as we can possibly find
        model.setParam(GRB.Param.PoolSolutions, self.num_solutions)

        # Run Gurobi
        model.optimize()

        # Prevent Gurobi from printing out random junk, like how we set an attribute...
        model.setParam(GRB.Param.OutputFlag, False)

        # Check the model
        self.check_model(model)

        # Get the solutions
        self.get_solutions(model)

    def check_model(self, model):
        """
        Checks the given model to see if it had any problems optimizing
        """
        if model.status != GRB.Status.OPTIMAL:
            if model.status == GRB.Status.INFEASIBLE:
                self.log("[Gurobi:ERROR]: Model is infeasible.", error=True)
            elif model.status == GRB.Status.INF_OR_UNBD:
                self.log("[Gurobi:ERROR]: Solution found was infinite or unbounded.", error=True)
            else:
                self.log("[Gurobi:ERROR]: Gurobi exited with status {}.".format(model.status), error=True)
            exit(1)

    def get_solutions(self, model):
        """
        Given a model, prints out the solutions (and saves them it applicable)
        """
        # Iterate through all the solutions
        self.log("Found the following solutions:")

        # Get the solution count and variables
        solution_count = model.getAttr(GRB.Attr.SolCount)
        variables = model.getVars()

        solutions = []
        for i in range(solution_count):
            model.setParam(GRB.Param.SolutionNumber, i)
            obj_value = model.getAttr(GRB.Attr.PoolObjVal)
            values = model.getAttr(GRB.Attr.Xn)

            solutions.append("# Objective Value = {}".format(int(obj_value)))
            for i, value in enumerate(values):
                solutions.append("{} {}".format(variables[i].getAttr(GRB.Attr.VarName), int(value)))
            solutions.append("")

        # Print the solution string to console
        solution_string = "\n".join(solutions)
        print(solution_string)

        # Write out to file if specified
        if self.resultfile:
            with open(self.resultfile, 'w+') as f:
                f.write(solution_string)

    def log(self, string, error=False):
        """
        Prints out stuff
        """
        if error:
            print("[NativeGurobiSolver:ERROR]: {}".format(string))
        else:
            print("[NativeGurobiSolver]: {}".format(string))

NativeGurobiSolver()
