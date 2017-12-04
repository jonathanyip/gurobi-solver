# Gurobi Solver

Uses Gurobi to iteratively find multiple solutions for Integer Linear Programs (ILPs)

### Max Clique Problem

Running `python GurobiSolver [ilp-filename]` solves the max clique problem for all solutions. See `simple_clique.lp` for an example ILP file.

Run `python GurobiSolver --help` to see all options you can pass into the current program (for example, to change the minimum Objective Value).

### Colorama License
Uses `colorama` for nice terminal colors! Packaged in `GurobiSolver` so no external installation is needed.

See `GurobiSolver/colorama/LICENSE.txt` for the license.
