import logging
mHSiI=str
mHSiR=isinstance
mHSiQ=False
mHSiN=Exception
mHSiv=None
mHSir=True
mHSiy=bool
import os
import re
import threading
import traceback
from typing import List,Union
import localstack
from localstack import constants
from localstack.services.install import(INSTALL_DIR_STEPFUNCTIONS,INSTALL_PATH_STEPFUNCTIONS_JAR,SFN_PATCH_URL_PREFIX,Installer,InstallerRepository,add_file_to_jar)
from localstack.utils.common import(download,file_exists_not_empty,in_docker,is_command_available,is_debian,now,rm_rf,run,save_file)
from localstack_ext.bootstrap.licensing import api_key_configured,prepare_environment
from localstack_ext.constants import ARTIFACTS_REPO
LOG=logging.getLogger(__name__)
RULE_ENGINE_INSTALL_URL="https://github.com/whummer/serverless-iot-offline"
H2_DOWNLOAD_URL="http://www.h2database.com/h2-2019-10-14.zip"
SSL_CERT_URL="%s/raw/master/local-certs/server.key"%ARTIFACTS_REPO
SSL_CERT_URL_FALLBACK="{api_endpoint}/proxy/localstack.cert.key"
INFRA_DIR=os.path.join(os.path.dirname(localstack.__file__),"infra")
LOCALSTACK_DIR=os.path.dirname(localstack.__file__)
POSTGRES_LIB_FOLDER="/usr/lib/postgresql/11/lib"
SFN_PATCH_CLASS1="cloud/localstack/StepFunctionsStarter$PersistenceAspect.class"
SFN_PATCH_CLASS2="cloud/localstack/StepFunctionsStarter$PersistenceContext.class"
SFN_PATCH_CLASS3="cloud/localstack/StepFunctionsStarter$PersistenceState.class"
SFN_PATCH_CLASS4="cloud/localstack/StepFunctionsStarter.class"
SFN_PATCH_FILE5="META-INF/aop.xml"
MAVEN_REPO="https://repo1.maven.org/maven2"
URL_ASPECTJRT=f"{MAVEN_REPO}/org/aspectj/aspectjrt/1.9.7/aspectjrt-1.9.7.jar"
URL_ASPECTJWEAVER=f"{MAVEN_REPO}/org/aspectj/aspectjweaver/1.9.7/aspectjweaver-1.9.7.jar"
URL_KRYO=f"{MAVEN_REPO}/com/esotericsoftware/kryo/5.2.0/kryo-5.2.0.jar"
URL_OBJENESIS=f"{MAVEN_REPO}/org/objenesis/objenesis/3.2/objenesis-3.2.jar"
URL_MINLOG=f"{MAVEN_REPO}/com/esotericsoftware/minlog/1.3.1/minlog-1.3.1.jar"
URL_REFLECTASM=f"{MAVEN_REPO}/com/esotericsoftware/reflectasm/1.11.9/reflectasm-1.11.9.jar"
JAR_URLS=[URL_ASPECTJRT,URL_ASPECTJWEAVER,URL_KRYO,URL_OBJENESIS,URL_MINLOG,URL_REFLECTASM]
INSTALL_LOCK=threading.RLock()
def install_libs():
 install_iot_rule_engine()
 install_postgres()
 install_timescaledb()
 install_redis()
 install_mqtt()
 install_stepfunctions()
def install_iot_rule_engine():
 target_dir=LOCALSTACK_DIR
 main_file=os.path.join(target_dir,"node_modules","serverless-iot-offline","query.js")
 if not os.path.exists(main_file):
  LOG.info("Installing IoT rule engine. This may take a while.")
  run("cd %s; npm install %s"%(target_dir,RULE_ENGINE_INSTALL_URL))
 return main_file
def install_postgres():
 if not in_docker():
  return
 check_or_install("psql","postgresql-11","RDS")
 check_or_install("pg_config",["postgresql-server-dev-11","libpq-dev"],"RDS")
 if not is_debian():
  return
 plpython_lib=f"{POSTGRES_LIB_FOLDER}/plpython3.so"
 if os.path.exists(plpython_lib):
  return
 install_package("postgresql-plpython3-11","RDS")
def install_timescaledb():
 if not in_docker():
  return
 if os.path.exists(f"{POSTGRES_LIB_FOLDER}/timescaledb.so"):
  return
 check_or_install("gcc",["cmake","gcc","git"],"Timestream")
 ts_dir="/tmp/timescaledb"
 tag="2.0.0-rc4"
 run("cd /tmp; git clone https://github.com/timescale/timescaledb.git")
 run("cd %s; git checkout %s; ./bootstrap -DREGRESS_CHECKS=OFF; cd build; make; make install"%(ts_dir,tag))
 rm_rf("/tmp/timescaledb")
def install_redis():
 check_or_install("redis-server","redis-server","ElastiCache")
 return "redis-server"
def install_mqtt():
 check_or_install("mosquitto","mosquitto","IoT")
 return "mosquitto"
def install_stepfunctions():
 classes=[SFN_PATCH_CLASS1,SFN_PATCH_CLASS2,SFN_PATCH_CLASS3,SFN_PATCH_CLASS4,SFN_PATCH_FILE5]
 sfn_jar_path=INSTALL_PATH_STEPFUNCTIONS_JAR
 for patch_class in classes:
  patch_url=f"{SFN_PATCH_URL_PREFIX}/{patch_class}"
  add_file_to_jar(patch_class,patch_url,target_jar=sfn_jar_path)
 manifest_file=os.path.join(INSTALL_DIR_STEPFUNCTIONS,"META-INF","MANIFEST.MF")
 if not os.path.exists(manifest_file):
  content=run(["unzip","-p",sfn_jar_path,"META-INF/MANIFEST.MF"])
  content=re.sub("Main-Class: .+","Main-Class: cloud.localstack.StepFunctionsStarter",content)
  classpath=" ".join([os.path.basename(jar)for jar in JAR_URLS])
  content=re.sub(r"Class-Path: \. ",f"Class-Path: {classpath} . ",content)
  save_file(manifest_file,content)
  run(["zip",sfn_jar_path,"META-INF/MANIFEST.MF"],cwd=INSTALL_DIR_STEPFUNCTIONS)
 for jar_url in JAR_URLS:
  target=os.path.join(INSTALL_DIR_STEPFUNCTIONS,os.path.basename(jar_url))
  if not file_exists_not_empty(target):
   download(jar_url,target)
def install_package(packages:Union[List[mHSiI],mHSiI],api_name:mHSiI):
 if not(is_debian()and in_docker()):
  LOG.warning("Unable to install dependencies for %s API. Please install packages %s (or equivalent) on your system manually!",api_name,packages)
  return
 if mHSiR(packages,mHSiI):
  packages=packages.split()
 LOG.info("Downloading dependencies for %s API. This may take a while."%api_name)
 with INSTALL_LOCK:
  run(["apt-get","update"],shell=mHSiQ)
  run(["apt-get","install","-y","--no-install-recommends"]+packages,shell=mHSiQ)
def check_or_install(command:mHSiI,packages:Union[List[mHSiI],mHSiI],api:mHSiI):
 if not is_command_available(command):
  install_package(packages,api)
def setup_ssl_cert():
 from localstack.services import generic_proxy
 target_file=generic_proxy.get_cert_pem_file_path()
 cache_duration_secs=6*60*60
 if os.path.exists(target_file):
  mod_time=os.path.getmtime(target_file)
  if mod_time>(now()-cache_duration_secs):
   return
 timeout_gh=3
 timeout_proxy=5
 try:
  return download_github_artifact(SSL_CERT_URL,target_file,timeout=timeout_gh)
 except mHSiN:
  url=SSL_CERT_URL_FALLBACK.format(api_endpoint=constants.API_ENDPOINT)
  try:
   return download(url,target_file,timeout=timeout_proxy)
  except mHSiN as e:
   LOG.info("Unable to download local test SSL certificate from %s to %s (using self-signed cert as fallback): %s",url,target_file,e)
   raise
def download_github_artifact(url:mHSiI,target_file:mHSiI,timeout:int=mHSiv):
 def do_download(url,print_error=mHSiQ):
  try:
   download(url,target_file,timeout=timeout)
   return mHSir
  except mHSiN as e:
   if print_error:
    LOG.info("Unable to download Github artifact from from %s to %s: %s %s"%(url,target_file,e,traceback.format_exc()))
 result=do_download(url)
 if not result:
  url=url.replace("https://github.com","https://cdn.jsdelivr.net/gh")
  url=url.replace("/raw/master/","@master/")
  do_download(url,mHSir)
def install_azure():
 from localstack_ext.services.azure import api_specs
 api_specs.download_api_specs()
class ExtInstallerRepository(InstallerRepository):
 name="ext"
 def should_load(self)->mHSiy:
  return api_key_configured()
 def load(self,*args,**kwargs):
  LOG.debug("Preparing Pro environment for LocalStack Package Manager.")
  with prepare_environment():
   LOG.debug("Pro environment has successfully been prepared.")
 def get_installer(self)->List[Installer]:
  return[("iot-rule-engine",install_iot_rule_engine),("postgres",install_postgres),("timescaledb",install_timescaledb),("redis",install_redis),("mqtt",install_mqtt),("azure",install_azure),("stepfunctions",install_stepfunctions)]
# Created by pyminifier (https://github.com/liftoff/pyminifier)
