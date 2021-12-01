from pyspark.sql import *
from pyspark.sql.functions import *
from pyspark.sql.types import *

import types
from pyspark.mllib.common import _py2java, _java2py

def pydataframe(self,qry,schema=None):
    sc = self.spark.sparkContext
    if not schema==None:
        if isinstance(schema, str):
            jschema = self.spark._jvm.org.apache.spark.sql.types.StructType.fromDDL(schema.replace(":",""))
        else:
            jschema = self.spark._jvm.org.apache.spark.sql.types.StructType.fromJson(schema.json())
        return _java2py(sc,self.dataframe(qry,jschema))
    else:
        return _java2py(sc,self.dataframe(qry,None))
    
def gor(self,qry,schema=None):
    global currentGorSession
    spark = currentGorSession.spark
    sc = spark.sparkContext
    df = _py2java(sc,self)
    ReflectionUtil = spark._jvm.py4j.reflection.ReflectionUtil
    Rowclass = ReflectionUtil.classForName("org.apache.spark.sql.Row")
    ct = spark._jvm.scala.reflect.ClassTag.apply(Rowclass)
    gds = spark._jvm.org.gorpipe.spark.GorDatasetFunctions(df,ct,ct)
    if not schema==None:
        if isinstance(schema, str):
            jschema = spark._jvm.org.apache.spark.sql.types.StructType.fromDDL(schema.replace(":",""))
        else:
            jschema = spark._jvm.org.apache.spark.sql.types.StructType.fromJson(schema.json())
        return _java2py(sc,gds.gorschema(qry,jschema,currentGorSession))
    return _java2py(sc,gds.gor(qry,True,currentGorSession))

def createGorSession(self):
    sgs = self._jvm.org.gorpipe.spark.SparkGOR.createSession(self._jsparkSession)
    sgs.pydataframe = types.MethodType(pydataframe,sgs)
    sgs.spark = self
    global currentGorSession
    currentGorSession = sgs
    return sgs

def createGorSessionWOptions(self,gorproject,cachedir,config,alias):
    sgs = self._jvm.org.gorpipe.spark.SparkGOR.createSession(self._jsparkSession,gorproject,cachedir,config,alias)
    sgs.pydataframe = types.MethodType(pydataframe,sgs)
    global currentGorSession
    currentGorSession = sgs
    return sgs

setattr(DataFrame, 'gor', gor)
setattr(SparkSession, 'createGorSession', createGorSession)
setattr(SparkSession, 'createGorSessionWOptions', createGorSessionWOptions)