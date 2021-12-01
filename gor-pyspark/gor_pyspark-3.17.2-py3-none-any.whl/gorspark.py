from pyspark.sql import *
from pyspark.sql.functions import *
from pyspark.sql.types import *

import types
from pyspark.mllib.common import _py2java, _java2py

def pydataframe(self,qry,schema):
    sc = spark.sparkContext
    jschema = spark._jvm.org.apache.spark.sql.types.StructType.fromJson(schema.json())
    return _java2py(sc,self.dataframe(qry,jschema))
    
def gor(self,qry):
    sc = spark.sparkContext
    df = _py2java(sc,self)
    ReflectionUtil = spark._jvm.py4j.reflection.ReflectionUtil
    Rowclass = ReflectionUtil.classForName("org.apache.spark.sql.Row")
    ct = spark._jvm.scala.reflect.ClassTag.apply(Rowclass)
    gds = spark._jvm.org.gorpipe.spark.GorDatasetFunctions(df,ct,ct)
    return _java2py(sc,gds.gor(qry,True,sgs))

def createGorSession(self):
    sgs = self._jvm.org.gorpipe.spark.SparkGOR.createSession(self._jsparkSession)
    sgs.pydataframe = types.MethodType(pydataframe,sgs)
    return sgs

def createGorSessionWOptions(self,gorproject,cachedir,config,alias):
    sgs = self._jvm.org.gorpipe.spark.SparkGOR.createSession(self._jsparkSession,gorproject,cachedir,config,alias)
    sgs.pydataframe = types.MethodType(pydataframe,sgs)
    return sgs

setattr(DataFrame, 'gor', gor)
setattr(SparkSession, 'createGorSession', createGorSession)
setattr(SparkSession, 'createGorSessionWOptions', createGorSessionWOptions)