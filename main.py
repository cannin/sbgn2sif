# SPDX-License-Identifier: Apache-2.0
# Copyright 2020 Augustin Luna

import argparse
import os
import logging 
from simplify_bipartite import simplify_bipartite
from extract_sbgn_edges import extract_sbgn_edges


def main(sbgnml_file, convert_dot, verbose):
    if verbose: 
        logging.basicConfig(level=logging.DEBUG)
    else: 
        logging.basicConfig(level=logging.INFO)

    logging.info("SBGNML: " + sbgnml_file)

    sif_file=list(os.path.splitext(sbgnml_file))
    sif_file[1]="_intermediate.sif"
    sif_file="".join(sif_file)

    if convert_dot: 
        bipartite_dot_file=list(os.path.splitext(sbgnml_file))
        bipartite_dot_file[1]="_bipartite.dot"
        bipartite_dot_file="".join(bipartite_dot_file)

        projected_dot_file=list(os.path.splitext(sbgnml_file))
        projected_dot_file[1]="_projected.dot"
        projected_dot_file="".join(projected_dot_file)
    else: 
        bipartite_dot_file = None
        projected_dot_file = None

    projected_sif_file=list(os.path.splitext(sbgnml_file))
    projected_sif_file[1]="_simplified.sif"
    projected_sif_file="".join(projected_sif_file)    

    # Run extraction 
    extraction = extract_sbgn_edges(sbgnml_file=sbgnml_file, sif_file=sif_file, verbose=verbose)
    logging.info("Extraction complete")

    # Run simplification
    if extraction['edge_count'] > 0: 
        simplify_bipartite(sif_file=sif_file, bipartite_dot_file=bipartite_dot_file, projected_dot_file=projected_dot_file, projected_sif_file=projected_sif_file, convert_dot=convert_dot, verbose=verbose)
    else: 
        sys.exit("ERROR: No edges found. Network cannot be simplified")
    logging.info("Simplification complete")

    if verbose: 
        if extraction['warning_count'] > 0:
            logging.info("DONE. With warnings")
        else: 
            logging.info("DONE. Without warnings")


if __name__ == '__main__':
    # Argument parser.
    description = '''Extract SBGNML Edgelist. See project README for more details.'''
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--sbgn', '-s',
        required = True,
        help = 'Input SBGNML file'
        )
    parser.add_argument('--convert', '-c',
        default = False,
        help = 'Convert Graphviz files to SVG with dot. Requires Graphviz to be installed',
        action='store_true'
        )
    parser.add_argument('--verbose', '-v',
        default = False,
        help = 'Input SBGNML file',
        action='store_true'
        )
    args = parser.parse_args()
    sbgnml_file=args.sbgn
    convert_dot=args.convert   
    verbose=args.verbose
    main(sbgnml_file, convert_dot, verbose)
    #example(sbgnml_file='pamp.sbgn', convert_dot=True, verbose=True)

# parser=argparse.ArgumentParser(
# description="""
# Convert SBGN-encoded pathways to the SIF file format.
# """,
# epilog="""
# sbgn2sif is currently quite lazy. It only requires:
#     * glyphs with IDs (in SBGN, glyphs are nodes)
#     * glyphs with labels (i.e. node names)
#     * arcs with IDs (in SBGN, arcs are edges)
#     * arcs with classes (i.e. edge types)
#     * arcs with valid source glyphs (cf. above)
#     * arcs with valid target glyphs (cf. above)

# If a glyph has more than one label then its name is the list of its labels
# separated with "|".

# For explanations about the SBGN file format see https://sbgn.github.io.

# For explanations about the SIF file format see the readme file of sbgn2sif.
# """,
# formatter_class=argparse.RawDescriptionHelpFormatter
# )
# parser.add_argument("sbgnfile",type=str,metavar="<sbgnfile>",help="a SBGN-encoded pathway",nargs="+")
# args=parser.parse_args()
#
#files = args.sbgnfile