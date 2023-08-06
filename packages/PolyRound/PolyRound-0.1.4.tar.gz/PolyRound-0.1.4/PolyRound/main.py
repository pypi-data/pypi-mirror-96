import numpy as np
import sys
import os

sys.path.insert(0, os.getcwd())
from PolyRound.static_classes.parse_sbml_stoichiometry import StoichiometryParser
from PolyRound.static_classes.hdf5_csv_io import HDF5
import time
import argparse
from PolyRound.api import PolyRoundApi

from PolyRound.default_settings import default_hp_flags
from cobra.util.solver import solvers


if "gurobi" in solvers:
    pref_backend = "gurobi"
else:
    pref_backend = "glpk"


def main(args):
    inputs = args.files
    path = args.path
    thresh = args.thresh
    verbose = args.v
    # set hp flags
    hp_flags = default_hp_flags
    if args.hp:
        hp_flags = {
            "NumericFocus": 3,
            "FeasibilityTol": 1e-09,
            "OptimalityTol": 1e-09,
            "MarkowitzTol": 0.999,
        }

    for input in inputs:
        input_name = input.split("/")[-1].split(".")[0]
        if input.endswith(".xml"):
            polytope = StoichiometryParser.parse_sbml_cobrapy(input)
        else:
            polytope = HDF5.h5_to_polytope(input)
        start_time = time.time()
        if not args.ie:
            polytope = PolyRoundApi.simplify_transform_and_round(
                polytope,
                backend=args.backend,
                hp_flags=hp_flags,
                thresh=thresh,
                verbose=verbose,
                sgp=args.sgp,
            )
        else:
            polytope = PolyRoundApi.round_polytope(polytope, verbose=verbose)
        end_time = time.time()
        HDF5.polytope_to_h5(
            polytope, os.path.join(path, input_name + "_reduced_rounded.hdf5")
        )
        return end_time - start_time


def pars_args():
    # Create the parser
    parser = argparse.ArgumentParser(description="List the content of a folder")

    # Add the arguments
    parser.add_argument(
        "-hp", action="store_true", help="run the program with high precision option"
    )
    parser.add_argument(
        "-ie",
        action="store_true",
        help="input is inequality constraints only (only for hdf5 input)",
    )
    parser.add_argument("-sgp", action="store_true", help="show gurobi progress")
    parser.add_argument("-v", action="store_true", help="run in verbose mode")
    parser.add_argument(
        "-thresh",
        type=float,
        default=1e-7,
        help="Threshold parameter for minimal width of a dimension",
    )
    parser.add_argument(
        "-path", type=str, default="PolyRound/output/", help="Output path"
    )
    parser.add_argument(
        "-backend",
        type=str,
        default=pref_backend,
        help="Backend for solving linear programs. Possible inputs is gurobi and glpk. gurobi is default in case it is available.",
    )
    parser.add_argument("files", nargs="*")

    args = parser.parse_args()
    print(args)
    # Do the input arguments make sense?
    contains_xml = np.any([file.endswith(".xml") for file in args.files])
    if contains_xml and args.ie:
        print("Argument -ie only available for hdf5 inputs")
        raise IOError

    legal_format = np.all(
        [file.endswith(".xml") or file.endswith(".hdf5") for file in args.files]
    )
    if not legal_format:
        print("Only file extensions .xml and .hdf5 allowed")
        raise IOError

    return args


if __name__ == "__main__":
    print(main(pars_args()))
