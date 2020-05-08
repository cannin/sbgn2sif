# SPDX-License-Identifier: Apache-2.0
# Copyright 2020 Augustin Luna

import networkx as nx
import pydot
import logging
import json
import csv 
import re 
import os

def simplify_bipartite(sif_file, bipartite_dot_file, projected_dot_file, projected_sif_file, convert_dot=False, verbose=True): 
    """ 
    Simplify a bipartite SIF file. SIF file must be tab-delimited and have the columns: 
    PARTICIPANT_A
    INTERACTION_TYPE
    PARTICIPANT_B
    ANNOTATION_SOURCE
    ANNOTATION_INTERACTION
    ANNOTATION_TARGET
    SOURCE_TYPE
    TARGET_TYPE

    Args: 
        sif_file (string): Input SIF file  
        bipartite_dot_file (string): Output bipartite Graphviz DOT file 
        projected_dot_file (string): Output bipartite projection Graphviz DOT file 
        projected_sif_file (string): Output bipartite projection SIF file
        verbose (boolean): display debugging information (default: True)    
    """

    # sif_file = 'pamp.sif'
    # bipartite_dot_file = 'j0.dot'
    # projected_dot_file = 'j1.dot'
    # projected_sif_file = "pamp.simp.tsv.txt"

    if verbose: 
        logging.basicConfig(level=logging.DEBUG)
    else: 
        logging.basicConfig(level=logging.INFO)

    fontsize = 4
    g_entity_pool = nx.DiGraph()
    g_process = nx.DiGraph()

    with open(sif_file) as f:
        reader = csv.DictReader(f, delimiter='\t')

        column_names = reader.fieldnames

        if verbose: 
            logging.debug("Columns: " + "|".join(column_names))

        existing_nodes = set()

        for row in reader:
            pa = row['PARTICIPANT_A']
            it = row['INTERACTION_TYPE']
            pb = row['PARTICIPANT_B']
            ns = row['ANNOTATION_SOURCE']
            ai = row['ANNOTATION_INTERACTION']
            at = row['ANNOTATION_TARGET']
            st = row['SOURCE_TYPE']
            tt = row['TARGET_TYPE']
            sc = row['SOURCE_CLASS']
            tc = row['TARGET_CLASS']

            if verbose: 
                logging.debug("Interaction Info: PA: " + pa + " PB: " + pb + " SC: " + sc + " TC: " + tc + "\n")

            if st == "logic" or tt == "logic":
                continue

            if sc == "source and sink" or tc == "source and sink":
                continue

            # Replace characters to make compatible with DOT format
            pa = re.sub(r'[:,\\]', '_', pa)
            pb = re.sub(r'[:,\\]', '_', pb)
            ns = re.sub(r'[:,\\]', '_', ns) 
            ai = re.sub(r'[:,\\]', '_', ai) 
            at = re.sub(r'[:,\\]', '_', at) 

            bipartite_pa = 0 if st == "entity_pool" else 1
            bipartite_pb = 0 if tt == "entity_pool" else 1

            shape_pa = 'circle' if st == "entity_pool" else 'square'
            shape_pb = 'circle' if tt == "entity_pool" else 'square'

            if st == "process" or tt == "process":
                g_process.add_node(pa, label = pa, cls = sc, annotation = ns, bipartite = bipartite_pa, shape = shape_pa, fontsize = fontsize)
                g_process.add_node(pb, label = pb, cls = tc, annotation = at, bipartite = bipartite_pb, shape = shape_pb, fontsize = fontsize)
                g_process.add_edge(pa, pb, interaction_type=it, annotation=ai)
            else: 
                g_entity_pool.add_node(pa, label = pa, cls = sc, annotation = ns, bipartite = bipartite_pa, shape = shape_pa, fontsize = fontsize)
                g_entity_pool.add_node(pb, label = pb, cls = tc, annotation = at, bipartite = bipartite_pb, shape = shape_pb, fontsize = fontsize)
                g_entity_pool.add_edge(pa, pb, interaction_type=it, annotation=ai)

    top_nodes = {n for n, d in g_process.nodes(data=True) if d['bipartite']==0}
    #bottom_nodes = bottom_nodes = set(g) - top_nodes
    #g_process_projected = nx.bipartite.projected_graph(g_process, top_nodes)

    if convert_dot: 
        nx.drawing.nx_pydot.write_dot(g_process, bipartite_dot_file)

        bipartite_svg_file=list(os.path.splitext(bipartite_dot_file))
        bipartite_svg_file[1]=".svg"
        bipartite_svg_file="".join(bipartite_svg_file)

        (graph,) = pydot.graph_from_dot_file(bipartite_dot_file)
        graph.write_svg(bipartite_svg_file)

    if verbose: 
        attr = nx.get_node_attributes(g_entity_pool, 'cls')
        logging.debug("Subgraph: Entity Pool: " + str(attr))
        attr = nx.get_node_attributes(g_process, 'cls')
        logging.debug("Subgraph: Process: " + str(attr))

    g_process_projected = nx.DiGraph()
    nodes = top_nodes
    g_process_projected.graph.update(g_process.graph)
    g_process_projected.add_nodes_from((n, g_process.nodes[n]) for n in nodes)
    for u in nodes:
        nbrs = set(nbr for nbr in g_process[u])
        nbrs2 = set(v for nbr in g_process[u] for v in g_process[nbr] if v != u)

        for nbr in nbrs: 
            for nbr2 in nbrs2:
                if g_process.has_edge(u, nbr) and g_process.has_edge(nbr, nbr2):
                    #g_process_projected.add_edges_from((u, n) for n in nbrs2)
                    #attr = {}
                    attr1 = g_process.get_edge_data(u, nbr)
                    attr2 = g_process.get_edge_data(nbr, nbr2)

                    interaction_type1 = attr1['interaction_type']
                    interaction_type2 = attr2['interaction_type']

                    if verbose: 
                        logging.debug("Edge: Attr: " + str(attr1))
                        logging.debug("Edge: Attr2: " + str(attr2))

                    if interaction_type1 == 'consumption' and interaction_type2 == 'production':
                        #attr['annotation'] = attr['annotation']
                        #attr['interaction_type'] = attr['interaction_type']
                        g_process_projected.add_edge(u, nbr2, **attr2)
                    else: 
                        g_process_projected.add_edge(u, nbr2, **attr1)

    g = nx.compose(g_entity_pool, g_process_projected)
    #g = g_process_projected
    #g1 = g_entity_pool

    nx.bipartite.is_bipartite(g)

    if convert_dot: 
        nx.drawing.nx_pydot.write_dot(g, projected_dot_file)

        projected_svg_file=list(os.path.splitext(projected_dot_file))
        projected_svg_file[1]=".svg"
        projected_svg_file="".join(projected_svg_file)

        (graph,) = pydot.graph_from_dot_file(projected_dot_file)
        graph.write_svg(projected_svg_file)

    nodes_dict = dict(g.nodes(data=True))

    with open(projected_sif_file, 'w') as f:
        header = "PARTICIPANT_A\tINTERACTION_TYPE\tPARTICIPANT_B\tANNOTATION_SOURCE\tANNOTATION_INTERACTION\tANNOTATION_TARGET\tSOURCE_CLASS\tTARGET_CLASS\n"
        f.write(header)

        for (u,v,a) in g.edges(data=True):
            pa = nodes_dict[u]['label']
            it = a['interaction_type']
            pb = nodes_dict[v]['label']
            ns = nodes_dict[u]['annotation']
            ai = a['annotation']
            at = nodes_dict[v]['annotation']
            sc = nodes_dict[u]['cls']
            tc = nodes_dict[v]['cls']

            line = pa + "\t" +\
                   it + "\t" +\
                   pb + "\t" +\
                   ns + "\t" +\
                   ai + "\t" +\
                   at + "\t" +\
                   sc + "\t" +\
                   tc + "\n"
            f.write(line)
