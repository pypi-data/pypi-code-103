#!/usr/bin/python3
""" VERY EXPERIMENTAL :  module for opinied command line processing of OWL ontologies

# Synopsis

    jjtmd2ttl [option] file.t.md ...
      ## convert markdown with yaml metadate in turtle (seealso pandoc)

    jjtable2ttl [option] file.csv ...
      -F '#'            - Fiels separator (def: '::')
      -f ','            - sub field separatos (def: '[;,]')
      -h 'headerLine'   - set a "header line" (def: first line)
         Ex:  jjtable2ttl -F : -h 'Id::uid::gid::name::' /etc/passwd
      ## convert csv  metadate in turtle 

    jjyaml2ttl [option] file.yaml
      FIXME not working yet
      ## multi yaml document

As a module:

    import jjowl
    ... FIXME

# Description
"""

__version__ = "0.2.2"

from jjcli import *
#from unidecode import unidecode
import json
import yaml
#import owlrl
#from   owlrl import convert_graph, RDFXML, TURTLE, JSON, AUTO, RDFA
#import rdflib
#from   rdflib.namespace import RDF, OWL, RDFS, SKOS, FOAF

##=======

## -----------------------------------------------------------------
## === utils importing "pseudo ontology elems"
##   parse tmd   ( meta(yaml) + body(markdown) )
##   tmd → turtle
##   t2iri(s)          """ term 2 IRIref """
##   t2iri_or_lit(s)
##   t2lit(s)
##   docs2ttl(d)       """ python structure to ttl

'''
FIXME:
 type
 a     => s:iri o:iri
 owl:
    inverseOf :            rel → rel
    Class
    Thing
    sameAs
    ObjectProperty : if x 'a' ObjectProperty   s:iri o:iri
    DataProperty : if x 'a' DataProperty   s:iri o:literal
 rdfs:
    label :    s:iri   o:literal
    range
    domain
    subClassOf :           
'''

def md2py(c):
    """ files(markdown with initial yaml metadata) → docs = [ doc ] """
    docs=[]
    for txt in c.slurp():
        doc={}
        ex=match(r'\s*---(.*?)---(.*)',txt,flags=re.S)
        if not ex:
            warn("### Erro: no formato de", c.filename(),)
            continue
        meta,text=(sub(r'\t','    ',ex[1]) , ex[2])
        try:
            doc = yaml.safe_load(meta)
        except Exception as e:
            warn("### Erro: nos metadados de", c.filename(),e)
            continue
        if not isinstance(doc,dict):
            warn("### Erro: nos metadados de", c.filename(),doc)
            continue
        if '-v' in c.opt:
            doc["__file__"]=c.filename()
        if search(r'\S',text):
            doc["__body-format__"]="markdown"
            if "body" in doc:   
                bname = doc.pop("body")
                doc[bname]=text
            else:
                doc["body"]=text

        docs.append(doc)
    return docs

def t2lit(s):
    """ term 2 literal """
    if isinstance(s ,(dict,list,tuple)):
        return f'"""FIXME: {s}"""'
    if isinstance(s ,int):
        return str(s)
    if search(r'[!?()\'+,;/]',str(s)) and not search(r'["\n]', str(s)):
        return f'"{s.strip()}"'
    if search(r'[!?()"\'\n+,;/]',str(s)):
        return f'"""{s.strip()}"""'
    return f'"{s.strip()}"'

def t2iri(s):
    """ term 2 IRIref → IRI or None """
    if isinstance(s ,(dict,list,tuple)):
        warn("???",s)
        return f'"""FIXME: {s}"""'
    if s in {'type','a',} : return f'a'
    if s in {'inverseOf','Class','Thing','sameAs', 'ObjectProperty',
            'DataProperty'} :
        return f'owl:{s}'
    if s in {'range','domain','subClassOf'} :
        return f'rdfs:{s}'
    if search(r'[!?()"\'\n+,;/]',str(s)):
        return None ### f'"""{s.strip()}"""'
    iri = sub(r'\s+|[:]',r'_',str(s).strip())
    iri = sub(r'\.$','',iri)
    return ":"+iri

def t2iri_or_lit(s):
    aux = t2iri(s)
    if aux : return aux
    else : return t2lit(s)

def docs2ttl(d):
    """ docs → turtle triples 
      (s,p,o)  or
      [s,p,o] → :s :p :o.      
           or more exactly dict2ttl({ s : {p : o}})
      [s, dict({pi:oi})] → :s :p1 :o1 ... :s :pi :oi .
           or more exactly dict2ttl({ s : dict(...)})
      list → join( "\n", [dict2ttl(v) v ∈ list] )
      dict → dict2ttl(dict)
#print(docs2ttl([]))
#print(docs2ttl([7,{27: {37,55}}]))
    """
    if isinstance(d,list):
        if len(d)==3 and not isinstance(d[0],(list,dict,tuple)) :
            return dict2ttl({d[0]: {d[1]: d[2]}})
        elif ( len(d)==2 and
               not isinstance(d[0],(list,dict,tuple)) and
               isinstance(d[1],dict) ) :
            return dict2ttl({d[0]: d[1]})
        else:
            return str.join("\n",[docs2ttl(x) for x in d])
    if isinstance(d,dict):
        return dict2ttl(d)
    if isinstance(d,tuple):
        if len(d)==3:
            return dict2ttl({d[0]: {d[1]: d[2]}})
        else:
            warn("????",d)

def dict2ttl(d:dict):
    """ dict doc → turtle triples 
  #  { "@id" : "João", "parente" : [ "D", "M"] }
  #  { "Manel": { "parente" : [ "D", "M"] },
  #    "Joana": { "a": "pessoa"}
  #  }
  #  { "Manel": { "parente" : { "D", "M"} }},
  #  { "ont": [ (2,3,4),(3,4,{4,5,6})]  },
"""
    r=""
    rd= d.copy()
    ### { @id : vi, ...dict-tail } → {vi : ...dict-tail }
    if   "id" in d:          s = rd.pop("id");    rd= {s:rd}
    elif "ID" in d:          s = rd.pop("ID");    rd= {s:rd}
    elif "@id" in d:         s = rd.pop("@id");   rd= {s:rd}
    elif "name" in d:        s = rd.pop("name");  rd= {s:rd}
    elif "@name" in d:       s = rd.pop("@name"); rd= {s:rd}

    for s,dd in rd.items():
        if match(r'@?ont(ology|ologia)?$',s,flags=re.I):
            r += docs2ttl(dd)
            continue

        if not isinstance(dd,dict):
            warn("Error: expecting a dictionary, got a ",rd)
            dd = {"__DEBUG__": dd}

        for p,o in dd.items():
            if match(r'@?ont(ology|ologia)?$',p,flags=re.I):
                r += docs2ttl(o)
            elif isinstance(o,(list,set)):
                for oo in o:
                    r += f'{t2iri(s)} {t2iri(p)} {t2iri_or_lit(oo)} .\n'
            elif isinstance(o,dict):
                for oo,oov in o.items():
                    r += f'{t2iri(s)} {t2iri(p)} {t2iri_or_lit(oo)} .\n'
                r += dict2ttl(o)
            else:
                r += f'{t2iri(s)} {t2iri(p)} {t2iri_or_lit(o)} .\n'
    return r

def main_tmd2ttl():            ## main -- tmd2ttl
    c=clfilter(opt="do:")     ## option values in c.opt dictionary
    ds = md2py(c)
    print(docs2ttl(ds))

#=== parse table

def parse_head(h: str, opt ):
    fs  = opt.get('-F','::')
    fs2 = ':'
    idclass,*ftits = split(fr'\s*{fs}\s*',h.strip())
    for i,f in enumerate(ftits):
        a = match(fr'(.+){fs2}(.+)',f)
        if a :
            ftits[i]={"rel": a[1],"class": a[2]}
        else:
            ftits[i]={"rel":f}
    return (idclass,ftits)

def parse_tup(t:str,idclass,ftits,opt ):
    fs  = opt.get('-F','::')
    fs2 = opt.get('-f','[;,|]')
    ont=[]
    id,*fieds = split(fr'\s*{fs}\s*',t.strip())
    doc={"@id": id, "type":idclass}
    for i,f in enumerate(fieds):
        if not search(r'\S',f): 
            continue
        if i >= len(ftits):
            warn('To many fielts ',id,fields)
            continue
        else:
            finf=ftits[i]
        if not search(r'\S',finf["rel"]): 
            continue
        a = [ x for x in split(fr'\s*{fs2}\s*',f) if search(r'\S',x) ]
        doc[finf["rel"]]= a
        if "class" in finf :
            for campo in a :
               ont.append( (campo, "type", finf["class"]))
    if ont:
        doc["ont"]=ont
    return doc

def table2py(c):
    """ files(headerline + CSV(fs="::",fs2="[;,|]") → docs = [ doc ] """
    head = c.opt.get("-h")  ## ex: table2tt -h 'Person :: pai:Person :: f'
    docs =[]
    for txt in c.slurp():
        if head:
            tups = [x for x in split(r'\s*\n\s*',txt) if match(r'\w',x)]
        else:
            head,*tups = [x for x in split(r'\s*\n\s*',txt) if match(r'\w',x)]
        idclass,ftits= parse_head(head,c.opt)
        for line in tups:
            doc=parse_tup(line,idclass,ftits,c.opt)
            if '-v' in c.opt:
                doc["__file__"]=c.filename()
            docs.append(doc)
    return docs

def main_table2ttl():
    c = clfilter(opt="h:do:F:f:v")     ## option values in c.opt dictionary
    ds = table2py(c)
    print(docs2ttl(ds))

## jjyaml2ttl

def yamls2py(c):
    """ files( ("---" yaml)+ ) → docs = [ doc ] """
    docs =[]
    for txt in c.slurp():
        txt= sub(r'\t','    ',txt) 
        try:
            elems = yaml.safe_load_all(txt)
        except Exception as e:
            warn("### Erro yaml de", c.filename(),e)
            continue
        if not elems:
            continue
        for doc in elems: 
            if not doc:
                continue
            if not isinstance(doc,dict):
                warn("### Erro invalid format:", c.filename(),doc)
                continue
            docs.append(doc)
    return docs

def main_yaml2ttl():
    c = clfilter(opt="do:F:f:")     ## option values in c.opt dictionary
    ds = yamls2py(c)
    print(docs2ttl(ds))

