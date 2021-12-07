#!/usr/bin/python3
""" VERY EXPERIMENTAL :  module for opinied command line processing of OWL ontologies

# Synopsis

    owlcat  a.ttl b.owl c.ttl > all.ttl
      -t                - input in Turtle (def: based on extension)
      -f xml            - define output Format
      -n                - skip inference of new triples (def: infer)
      -o file
      ## concatenate → infer new triples → removeprefix

    owlclass a.ttl      
      -t                - input in Turtle (def: based on extension)
      -r                - keep transitive Redundances
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

    jjyaml2ttl [option] file.t.yaml ...
      ## convert multi-yaml in turtle 

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

__version__ = "0.2.3"

from jjcli import *
from unidecode import unidecode
import json
import yaml
import owlrl
from   owlrl import convert_graph, RDFXML, TURTLE, JSON, AUTO, RDFA
import rdflib
from   rdflib.namespace import RDF, OWL, RDFS, SKOS, FOAF

def OFF_best_name_d(g : rdflib.Graph) -> dict :
   """ FIXME: IRIRef -> str based on RDFS.label, id, ??? """
   bestname={}
   for n in g.all_nodes():
       if islit(n): continue
       if name := g.preferredLabel(n) :
           bestname[s]=name[0].strip()
       else:
           txt = term.n3(g.namespace_manager)
           txt = sub(r'^:', '', txt)
           txt = sub(r'_', ' ', txt)
           bestname[s]=txt.strip()
   return bestname
#   for s,p,o in g.triples((None,RDFS.label,None)):
#   return


def get_invs(g: rdflib.Graph) -> dict :
   """Dictionary of inverse relations (based on inverseOf and SymetricProperty"""
   inv = {OWL.sameAs: OWL.sameAs}
   for s,p,o in g.triples((None,OWL.inverseOf,None)):
       inv[s]=o
       inv[o]=s
   for s,p,o in g.triples((None,RDF.type, OWL.SymmetricProperty)):
       inv[s]=s
   return inv

def reduce_graph(g,fixuri=None,fixlit=None)-> rdflib.Graph:
   def fix(item):
        if islit(item) and fixlit:
            return rdflib.term.Literal(fixlit(str(item)))
        if isinstance(item, rdflib.term.URIRef) and fixuri:
            return rdflib.term.URIRef(fixuri(str(item)))
        return item

   fixed= rdflib.Graph()
   fixed.bind('owl',OWL)
   fixed.bind('rdf',RDF)
   fixed.bind('rdfs',RDFS)
   fixed.bind('skos',SKOS)
   fixed.bind('foaf',FOAF)

   fixed+= [ (fix(s), fix(p), fix(o)) for s,p,o in g]
   return fixed

def concatload(files:list, opt: dict) -> rdflib.Graph :
   ns=opt.get("-s",'http://it/')
   g = rdflib.Graph(base=ns)
   g.bind("",rdflib.Namespace(ns))
   g.bind('owl',OWL)
   g.bind('rdf',RDF)
   g.bind('rdfs',RDFS)
   g.bind('skos',SKOS)
   g.bind('foaf',FOAF)
   for f in files:
      if ".n3" in f or ".ttl" in f or "-t" in opt:
         try:
             # g.parse(f,format='turtle')
             g.parse(f,format='n3')
         except Exception as e:
             warn("#### Error in ", f,e)
      else:
         try:
             g.parse(f) #,format='xml')
         except Exception as e:
             warn("#### Error in ", f,e)
   return g

def concat(files:list, opt: dict) -> rdflib.Graph :
   ns=opt.get("-s",'http://it/')
   g=concatload(files, opt)
   def fixu(t):
      if str(RDF) in t or str(OWL) in t or str(RDFS) in t :
          return t
      else:
          return  sub(r'(http|file).*[#/]',ns,t)

   g2=reduce_graph(g, fixuri=fixu)
   g2.bind("",ns)
   return g2

def termcmp(t):
   return  unidecode(sub(r'.*[#/]','',t).lower())

def islit(t):
   return isinstance(t,rdflib.term.Literal)

#== main entry points

def mcat():           # main for owlcat
   c=clfilter(opt="i:f:no:s:t")
   g=owlproc(c.args,c.opt)
   g.serial()

def mlabel2term():    # main for owllabel
   c=clfilter(opt="f:kpcno:s:t")
   g=owlproc(c.args,c.opt)
   g.rename_label2term()
   g.serial()

def mgrep():          # main for owlgrep
   c=clfilter(opt="f:kpco:s:t")
   pat=c.args.pop(0)
   g=owlproc(c.args,c.opt)
   if v:= match(r'(.+?)::(.+)',pat):
       g.grep2(v[1],v[2])
   else:
       g.grep(pat)

def mexpandpp():       # main for owlexpand
   c=clfilter(opt="kpco:s:t")
   g=owlproc(c.args,c.opt)
   g.pprint()

def mxdxf():           # main for owlxdxf
   c=clfilter(opt="no:s:t")
   g=owlproc(c.args,c.opt)
   g.xdxf()

def mclass():          # main for owlclass
   c=clfilter(opt="no:rs:t")
   g=owlproc(c.args,c.opt)
   g.pptopdown(OWL.Thing)

def mprops():          # main for owlprop
   c=clfilter(opt="no:rs:t")
   g=owlproc(c.args,c.opt)
   g.ppprops()

##=======

class owlproc:
   """ Class for process owl ontologies
      .opt
      .g
      .inv
      .instances : tipo -> indiv
      .subcl   = {}
      .supcl   = {}
      .supcltc = {}

   """
   def __init__(self,ontos,
                     opt={},
                     ):
      self.opt=opt
      if "-s" not in self.opt:    ## default name space
          self.ns='http://it/'
      else:
          self.ns=self.opt["-s"]

      self.g=concat(ontos,opt)
      if "-n" not in self.opt:
          self._infer()
      self.inv=get_invs(self.g)
      self._get_subclass()
      self._instances()

   def serial(self,fmt="turtle"):
      if "-f" in self.opt :
          fmt = self.opt["-f"]
      print(self.g.serialize(format=fmt).decode('utf-8'))

   def _pp(self,term) -> str:
       """ returns a Prety printed a URIRef or Literal """
       return term.n3(self.g.namespace_manager)

   def _instances(self):
      self.instances={}
      for s,p,o in self.g.triples((None,RDF.type, None)):
          self.instances[o]=self.instances.get(o,[]) + [s]

   def _infer(self):
      owlrl.DeductiveClosure(owlrl.OWLRL_Extension_Trimming ).expand(self.g)

   def ppprops(self):
      predbag={}
      predtyp={}
      for s in self.g.subjects(predicate=RDF.type,object=OWL.ObjectProperty): 
          predbag[s]=0
          predtyp[s]="ObjectProperty"
      for s in self.g.subjects(predicate=RDF.type,object=OWL.DataProperty): 
          predbag[s]=0
          predtyp[s]="DataProperty"
      for p in self.g.predicates():
          predbag[p]=predbag.get(p,0)+1 
      for p in predbag.keys():
          for s,o in self.g.subject_objects(p):   ## ↓ p o
              if islit(o):
                 predtyp[p]="DataProperty"
              else:
                 predtyp[p]="ObjectProperty"
              break
      for p,n in sorted(predbag.items()):
          print(f'{self._pp(p)} a {predtyp[p]} . # {n} ')


   def xdxf(self):
      if "-o" in self.opt:
          f = open(self.opt["-o"],"w",encoding="utf-8")
      else:
          f = sys.stdout
      ignore_pred={ RDF.type, RDFS.subPropertyOf , OWL.topObjectProperty,
         OWL.equivalentProperty }

      print(f"""<?xml version="1.0" encoding="UTF-8" ?>
<xdxf lang_from="POR" lang_to="DE" format="logical" revision="033">
    <meta_info>
        <title>Dicionário</title>
        <full_title>Dicionário</full_title>
        <file_ver>001</file_ver>
        <creation_date></creation_date>
    </meta_info>
<lexicon>""",file=f)

      for n in sorted(self.g.all_nodes(), key=termcmp):
          if islit(n): continue
          if n in [OWL.Thing] : continue
          self._term_inf_xdxf(n,f)  ## FIXME
      print("</lexicon>\n</xdxf>",file=f)
      if "-o" in self.opt:
          f.close()

   def grep(self,pat):
       for n in sorted(self.g.all_nodes(), key=termcmp):
           if islit(n): continue
           if n in [OWL.Thing] : continue
           npp = self._pp(n)
           if search( pat, npp, flags=re.I):
               if "-k" in self.opt:
                   print(npp)
               else:
                   self._pterm_inf(n)

   def grep2(self,patc,pati):
       for s,o in self.g.subject_objects(RDF.type):
           opp = self._pp(o)
           if search( patc, opp, flags=re.I):
               spp = self._pp(s)
               if search( pati, spp, flags=re.I):
                   if "-k" in self.opt:
                       print(f'{opp}::{spp}')
                   else:
                       self._pterm_inf(s)

   def _get_subclass(self):
      self.subcl   = {}
      self.supcl   = {}
      self.supcltc = {}
      for s,p,o in self.g.triples((None,RDF.type,None)):
          self.supcl[o]=set()
      for s,p,o in self.g.triples((None,RDFS.subClassOf,None)):
          self.subcl[s]=self.subcl.get(s,set())
          self.supcl[o]=self.supcl.get(o,set())

          self.subcl[o]=self.subcl.get(o,set()) | {s}  ### | subcl.get(s,set())
          self.supcl[s]=self.supcl.get(s,set()) | {o}
      self.subcl[OWL.Thing]=[x for x in self.supcl if not self.supcl[x]]

      for c,up in self.supcl.items():
          if c not in self.supcltc: self.supcltc[c] = up
          for y in up:
              if y not in self.supcltc:
                  self.supcltc[y] = set()
              self.supcltc[c].update(self.supcl[y])
      aux = self.supcltc.items()
      for c,up in aux :
          for y in up:
              self.supcltc[c].update(self.supcltc[y])

   def pptopdown(self,top,vis={},indent=0,max=1000):
       if max <= 0  : return
       if top in vis: return
       vis[top]=1
       print( f'{"  " * indent}{self._pp(top)}' )
       scls=self.subcl.get(top,[])
       if "-r" not in self.opt:
           scls=self._simplify_class(self.subcl.get(top,[]))
       for a in sorted(scls,key=termcmp):
           self.pptopdown(a,vis,indent+2,max-1)

   def _simplify_class(self, cls:list, strat="td") -> list:
       """ FIXME: remove redundant class from a class list"""
       aux = set(cls) - {OWL.Thing, OWL.NamedIndividual}
       for x in aux.copy():
           if strat == "td":
               if self.supcltc.get(x,set()) & aux:
                   aux.remove(x)
           else:    ## "bu"
               aux -= self.supcltc.get(x,set())
       return aux

   def _term_inf_xdxf(self,n,f):
      ignore_pred={ RDF.type, RDFS.subPropertyOf , OWL.topObjectProperty,
         OWL.equivalentProperty }

      print("",file=f)
      print(f'<ar><k>{self._xpp(n)}</k><def>',file=f) ####  AR
      cls = self._simplify_class(self.g.objects(subject=n,predicate=RDF.type),
                                 strat="bu")
      for c in cls:                                     ## class
          print( f"<kref>{self._xpp(c)}</kref>",
                 file=f)
      for p,o in sorted(self.g.predicate_objects(n)):   ## ↓ p o
          if p in ignore_pred: continue
          ppstr=self._pp(p)
          opstr=self._pp(o)
          pstr=self._xpp(p)
          ostr=self._xpp(o)
          if ppstr in {':img','IMG',':jpg',':png'}:
              print(f"   <def><img width='500px' src={opstr}/></def>",
                    file=f)
          elif ppstr in {':pdf',':url'}:
              print(f"   <def><iref href={opstr}>{pstr} ↗</iref></def>",
                    file=f)
          elif islit(o):
              print(f"   <def>{pstr}: {ostr}</def>",
                    file=f)
          else:
              print(f"   <def>{pstr}: <kref>{ostr}</kref></def>",
                    file=f)

      for s,p in sorted(self.g.subject_predicates(n)):   ## s p ↓
          if p in ignore_pred  or p in self.inv: continue
          print(f"   <def><kref>{self._xpp(s)}</kref>  {self._xpp(p)} *</def>",
                file=f)
      if n in self.instances:
          for i in sorted(self.instances[n],key=termcmp):
              print(f" <def><kref>{self._xpp(i)}</kref></def>",
                    file=f)
      print(f'</def></ar>', file=f)                    ####  /AR


   def _xpp(self,term) -> str:
       """ returns a xdxf Prety printed URIRef """
       txt = self._pp(term)
       txt = sub(r'\\"','"',txt)
       if islit(term):
           if '"""' in txt  or "'''" in txt:
               return "<deftext>"+ sub(r'[<>&]','=',txt).strip("""'" """) + "</deftext>"
           elif match(r'(.+)\.(jpe?g|png|pdf|svg)$', txt):
               return txt.strip("""'" """)
           else:
               return "<c>"+sub(r'[<>&]','=',txt).strip("""'" """) + "</c>"
       else:
           txt = sub(r'^:', '', txt)
           txt = sub(r'_', ' ', txt)
           return sub(r'[<>&]','=',txt)

   def rename_label2term(self) -> rdflib.Graph :
       newname = {}

       for s,o in self.g.subject_objects(RDFS.label):
           base = sub(r'(.*[#/]).*',r'\1',str(s))
           newid = sub(r' ','_', str(o).strip())
           newname[str(s)] = base + newid

       for s,o in self.g.subject_objects(SKOS.prefLabel):
           base = sub(r'(.*[#/]).*',r'\1',str(s))
           newid = sub(r' ','_', str(o).strip())
           newname[str(s)] = base + newid

       def rename(t):
          if str(RDF) in t or str(OWL) in t or str(RDFS) in t or str(SKOS) in t:
              return t
          else:
              taux = newname.get(t,t)
              return sub(r'(http|file).*[#/]',self.ns,taux)
       g2=reduce_graph(self.g, fixuri=rename)
       g2.bind("",self.ns)
       self.g = g2

   def _pterm_inf(self,n):
       ignore_pred={ RDF.type, RDFS.subPropertyOf , OWL.topObjectProperty,
          OWL.equivalentProperty }

       print("====")
       print(self._pp(n))
       cls = self._simplify_class(self.g.objects(subject=n,predicate=RDF.type),
                                  strat="bu")
       for c in cls:
           print("   ", self._pp(c))
       for p,o in sorted(self.g.predicate_objects(n)):   ## ↓ p o
           if p in ignore_pred: continue
           print( "       ", self._pp(p), self._pp(o))
       for s,p in sorted(self.g.subject_predicates(n)):   ## s p ↓
           if p in ignore_pred: continue
           if p in self.inv: continue
           print( "       ", self._pp(s), self._pp(p), "*")

   def pprint(self):
       for n in sorted(self.g.all_nodes(), key=termcmp):
           if islit(n): continue
           if n in [OWL.Thing] : continue
           self._pterm_inf(n)
