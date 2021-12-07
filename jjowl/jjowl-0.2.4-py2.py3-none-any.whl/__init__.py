#!/usr/bin/python3
""" VERY EXPERIMENTAL :  module for opinied command line processing of OWL ontologies

# Synopsis

    owlcat  a.ttl b.owl c.ttl > all.ttl
      -t                - input in turtle (def: based on extension)
      -f xml            - define output format
      -n                - skip inference of new triples (def: infer)
      -o file
      ## concatenate → infer new triples → removeprefix

    owlclass a.ttl      
      -t                - input in turtle (def: based on extension)
      -r                - keep transitive redundances
      ## show class taxonomy

    owlgrep pattern a.ttl
      -t                - input in turtle (def: based on extension)
      -k                - just the IRI (default: term and adjacents)
       pattern :
         intanceRE
         classRE::instanceRE
      ## grep indivituals, class, or class:indi; ouput their triples

    owllabel2term a.ttl > new.ttl   
      -s nameSpace                  - default http://it/
      ## rename IRIRef from rfds:label

    owlexpandpp a.ttl   - expand and pretty print
      -t                - input in turtle (def: based on extension)
      ##

    owlxdxf  a.ttl      
      -t                - input in turtle (def: based on extension)
      -o out.xdxf       - redirects output (default stdout)
      ## Build a XDXF linked dictionary (seealso goldendict)

    jjtmd2ttl [option] file.t.md ...
      ## convert markdown with yaml metadate in turtle (seealso pandoc)

    jjtable2ttl [option] file.csv ...
      -F '#'            - Fiels separator (def: '::')
      -f ','            - sub field separatos (def: '[;,]')
      -h 'headerLine'   - set a "header line" (def: first line)
         Ex:   table2ttl -F : -h 'Id::uid::gid::name::' /etc/passwd
      ## convert csv  metadate in turtle 

As a module:

    import jjowl
    ... FIXME

# Description
"""

from .jjowl import *
from .ont_convert import *

__version__ = "0.2.4"
