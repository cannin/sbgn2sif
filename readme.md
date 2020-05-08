# Convert SBGNML to SIF 

* SBGNML: 
  * https://sbgn.github.io
  * http://co.mbine.org/specifications/sbgnml.version-0.3.release-1
* SIF: Check "Output" section

# Installation 

* Pipenv: https://github.com/pypa/pipenv

```
pipenv install
```

or 

```
pip3 install -r requirements.txt 
```

# Example with Conversion to SVG and Verbose Output

```
pipenv run python main.py -s pamp.sbgn -c -v
```

# Output

## SIF: Simple Interaction Format: Tabular Format 

```
PARTICIPANT_A INTERACTION_TYPE PARTICIPANT_B ANNOTATION_SOURCE ANNOTATION_INTERACTION ANNOTATION_TARGET SOURCE_CLASS TARGET_CLASS
TP53 stimulation MDM2 HGNC:X PUBMED:Y HGNC:Y macromolecule macromolecule
```

## Graphviz DOT/SVG

An simplified graphical representation showing connections between SBGN glyphs 

## Intermediate Versus Projected/Simplified Outputs 

* Intermediate output includes: entity pool, logic, and process glyphs. 
* Simplified output removes logic and process 
  * Process nodes are removed using [bipartite network projection](https://en.wikipedia.org/wiki/Bipartite_network_projection). The graph represented by SBGNML is 
    * Decomposed into bipartite and non-bipartite subgraphs
    * Bipartite network projection is used on the bipartite subgraph 
    * The non-bipartite and projected subgraphs are integrated
 * Logic nodes and connections are removed (TODO)
 * Interactions between complex members are not represented (TODO)

# Contributors 

* Original work: Copyright 2019 [Arnaud Poret](https://github.com/arnaudporet)
* Modified work: Copyright 2020 [Augustin Luna](https://github.com/cannin)

# License 

* SPDX-License-Identifier: Apache-2.0

