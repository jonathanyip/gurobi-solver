# Gurobi Solver

Uses Gurobi to find multiple solutions for Integer Linear Programs (ILPs)

## `IterGurobiSolver.py`
Runs Gurobi on the ILP iteratively, before each run introducing a constraint to not find the same solution set.

**How it works:**

For every variable C(i) that set to 1, do

  `sum(C(i)) <= (Objective Value) - 1`

This ensures that we don't select all of them again, but we can select a subset of them.

**Usage:** `python IterGurobiSolver.py --numSols=[num solutions to find] --resultile=[results.sol] [ilp-filename.lp]`

**Limitations:**

This only works with ILPs that only use binary variables, because of the way it makes the new constraints.

## `NativeGurobiSolver.py`
Runs Gurobi on the ILP, but uses the native Gurobi API to search for the `n` best solutions.

**Usage:** `python NativeGurobiSolver.py --numSols=[num solutions to find] --resultile=[results.sol] [ilp-filename.lp]`
