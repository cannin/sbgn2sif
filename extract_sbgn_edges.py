# SPDX-License-Identifier: Apache-2.0
# Original work: Copyright 2019 Arnaud Poret
# Modified work: Copyright 2020 Augustin Luna

import os
import re
import xml.etree.ElementTree
import logging

def extract_sbgn_edges(sbgnml_file, sif_file, verbose=True): 
    """ 
    Extract an edgelist from a SBGNML file 

    Args: 
        sbgnml_file (string): Input SBGNML file 
        verbose (boolean): display debugging information (default: True)
    """

    if verbose: 
        logging.basicConfig(level=logging.DEBUG)
    else: 
        logging.basicConfig(level=logging.ERROR)

    #verbose = False
    #sbgnml_file = 'pamp.sbgn'
    namespaces = {'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#', 'ns1': 'http://biomodels.net/biology-qualifiers/'}

    warnings = []
    edges = []
    sbgn = xml.etree.ElementTree.fromstring(re.sub(r"\bxmlns=\".*?\"","",open(sbgnml_file,"rt").read()))

    for map_ in sbgn.findall("map"):
        
        glyphs = {}
        arcs = {}
        annotations = {}

        for glyph in map_.findall("glyph"):
            id_=glyph.get("id")
            class_=glyph.get("class")
            if id_==None:
                warnings.append("glyph with no ID, skipping")
            elif id_ in glyphs.keys():
                warnings.append("glyph "+id_+": duplicated ID, skipping")
            else:
                labels=[]
                for label in glyph.findall("label"):
                    name=label.get("text")

                    # Replace characters that cause problems later
                    name = re.sub('\n', ' ', name)

                    if (name!=None) and (name!="") and (name not in labels):
                        labels.append(name)

                if len(labels)==0:
                    glyphs[id_]={'label': id_, 'class': class_}
                    #warnings.append("glyph "+id_+": missing label, skipping")
                else:
                    glyphs[id_]={'label': "|".join(labels), 'class': class_}

        for glyph in map_.findall("glyph"):
            logging.debug("P: 0")
            id_=glyph.get("id")
            
            if id_ in glyphs.keys():
                logging.debug("P: 0" + id_)
                
                for port in glyph.findall("port"):
                    logging.debug("P: ALL")
                    
                    alias=port.get("id")
                    if alias==None:
                        warnings.append("glyph "+id_+": port with no ID, skipping")
                    elif alias in glyphs.keys():
                        warnings.append("glyph "+id_+": port "+alias+": duplicated ID, skipping")
                    else:
                        logging.debug("P: ELSE")
                        glyphs[alias]={'label': glyphs[id_]['label'], 'class': glyphs[id_]['class']}

                for annotation in glyph.findall("./extension/annotation/rdf:RDF", namespaces):
                    logging.debug("A: ALL")

                    labels = []
                    for li in annotation.findall(".//rdf:li", namespaces):
                        # From: https://docs.python.org/2/library/xml.etree.elementtree.html
                        attribute = '{' + namespaces['rdf'] + '}resource'
                        name=li.attrib[attribute]
                        logging.debug("A: LI"+name)
                        if (name!=None) and (name!="") and (name not in labels):
                            logging.debug("A: IF"+name)
                            labels.append(name)
                        else: 
                            warnings.append("glyph "+id_+": annotation with no rdf:li, skipping")
                    
                    annotations[id_]="|".join(labels)

        for arc in map_.findall("arc"):
            id_=arc.get("id")
            class_=arc.get("class")
            source=arc.get("source")
            target=arc.get("target")
            if id_==None:
                warnings.append("arc with no ID, skipping")
            elif id_ in arcs.keys():
                warnings.append("arc "+id_+": duplicated ID, skipping")
            elif (class_==None) or (class_==""):
                warnings.append("arc "+id_+": missing class, skipping")
            elif source not in glyphs.keys():
                warnings.append("arc "+id_+": invalid source glyph, skipping")
            elif target not in glyphs.keys():
                warnings.append("arc "+id_+": invalid target glyph, skipping")
            else:
                if source.startswith('pr_'):
                    annotation_source = ""
                    annotation_interaction = annotations[source] if source in annotations.keys() else ""
                    annotation_target = annotations[target] if target in annotations.keys() else ""
                elif target.startswith('pr_'):
                    annotation_source = annotations[source] if source in annotations.keys() else ""
                    annotation_interaction = annotations[target] if target in annotations.keys() else ""
                    annotation_target = ""
                else: 
                    annotation_source = annotations[source] if source in annotations.keys() else ""
                    annotation_interaction = ""
                    annotation_target = annotations[target] if target in annotations.keys() else ""

                # TODO missing phenotype
                if glyphs[source]['class'] in ['process', 'omitted process', 'uncertain process', 'association', 'dissociation']:
                    source_type = "process"
                elif glyphs[source]['class'] in ['and', 'or', 'not', 'equivalence']:
                    source_type = "logic"
                else: 
                    source_type = "entity_pool"

                if glyphs[target]['class'] in ['process', 'omitted process', 'uncertain process', 'association', 'dissociation']:
                    target_type = "process"
                elif glyphs[target]['class'] in ['and', 'or', 'not', 'equivalence']:
                    target_type = "logic"
                else: 
                    target_type = "entity_pool"        

                logging.debug("S: " + source_type + " T: " + target_type + "\n")    

                arcs[id_]="\t".join([glyphs[source]['label'], class_, glyphs[target]['label'],\
                  annotation_source, annotation_interaction, annotation_target,\
                  source_type, target_type, glyphs[source]['class'], glyphs[target]['class']])

        for id_ in arcs:
            if arcs[id_] not in edges:
                logging.info(arcs[id_])
                edges.append(arcs[id_])

    if len(warnings)!=0:
        warn_file=list(os.path.splitext(sbgnml_file))
        warn_file[1]="_warnings.txt"
        warn_file="".join(warn_file)

        logging.warning("sbgn2sif: " + sbgnml_file + ": see "+warn_file)

        open(warn_file,"w").write("\n".join(warnings)+"\n")

    if len(edges)==0:
        logging.warning("sbgn2sif: " + sbgnml_file + ": empty after conversion. SIF file will not be created.")
    else:
        open(sif_file,"w").write("PARTICIPANT_A\tINTERACTION_TYPE\tPARTICIPANT_B\tANNOTATION_SOURCE\tANNOTATION_INTERACTION\tANNOTATION_TARGET\tSOURCE_TYPE\tTARGET_TYPE\tSOURCE_CLASS\tTARGET_CLASS\n")
        open(sif_file,"a").write("\n".join(edges)+"\n")

    results = {"warning_count": len(warnings), "edge_count": len(edges), "warnings": warnings, "edges": edges}
    return results

