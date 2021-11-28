#!/usr/bin/python
class Var:
      nameA='SH.py'  #nameA!  
      nameB=11.18  #nameB! 
      @classmethod
      def popen(cls,CMD):
          import subprocess,io,re
          # CMD = f"pip install cmd.py==999999"
          # CMD = f"ls -al"

          proc = subprocess.Popen(CMD, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=-1)
          proc.wait()
          stdout = io.TextIOWrapper(proc.stdout, encoding='utf-8').read()
          stderr = io.TextIOWrapper(proc.stderr, encoding='utf-8').read()

          # True if stdout  else False , stdout if stdout  else stderr 
          return  stdout if stdout  else stderr 
      
      @classmethod
      def pipB(cls,name="cmd.py"):
          CMD = f"pip install {name}==999999"
          import re
          ################  錯誤輸出    
          str_stderr = cls.popen(CMD)
          SS=re.sub(".+versions:\s*","[",str_stderr)
          SS=re.sub("\)\nERROR.+\n","]",SS)
          # print("SS..",eval(SS))
          BB = [i.strip() for i in SS[1:-1].split(",")]
          
          print(f"[版本] {cls.nameA}: ",BB)
          ################  return  <list>   
          return BB
         
     

      def __new__(cls,name=None,vvv=None):
        

          if  name!=None and vvv!=None:
              #######################################################
            #   with  open( __file__ , 'r+' ,encoding='utf-8') as f :        
            #         ############################
            #         f.seek(0,0)       ## 規0
            #         R =f.readlines( ) 
            #         R[1]=f"      nameA='{name}'\n"
            #         R[2]=f"      nameB='{vvv}'\n"
            #         ##########################
            #         f.seek(0,0)       ## 規0
            #         f.writelines(R)
                            
              #######################################################
              with  open( __file__ , 'r+' ,encoding='utf-8') as f :        
                    ############################
                

                                    

                    # N="name"
                    NR=["#nameA!","#nameB!"]
                    ######## 禁止i.strip() 刪除 \n 和\tab ############
                    ### R is ########## 本檔案 #######################
                    f.seek(0,0)       ## 規0
                    R =f.readlines( ) 
                    # R=[ i for i in open(__file__).readlines()] 
                    # print(R)

                    ###############
                    # Q=[ (ii,i) for i,b in enumerate(R) for ii in b.strip().split(" ") if len(b.strip().split(" "))!=1  if  ii in ["#nameA!","#nameB!"]   ]
                    Q=[ (i,b) for i,b in enumerate(R) for ii in b.strip().split(" ") if len(b.strip().split(" "))!=1  if  ii in NR   ]
                    # print(Q)

                    if len(Q)==len(NR):
                        # print("**Q",*Q)
                        NR=[ i.strip("#!") for i in NR] ## 清除[#!] ---> ["nameA","nameB"]
                        NG=[ f"'{name}'" , vvv ]
                        def RQQ( i , b ):
                            # print( "!!",i ,b)
                            NRR = NR.pop(0) 
                            NGG = NG.pop(0) 
                            import re
                            # print(Q[0]) ## (2, 'nameA=None  #nameA!')
                            R01 = list(  b  )     ## 字元陣列 ## 

                            N01 = "".join(R01).find( f"{ NRR }")
                            R01.insert(N01,"=")
                            # print( R01  )

                            N01 = "".join(R01).find( f"#{ NRR }!")
                            R01.insert(N01,"=")
                            # print( R01  )

                            ### 修改!.
                            QQA="".join(R01).split("=")
                            QQA.pop(2)
                            QQA.insert(2, f"={ NGG }  ")
                            # print("!!QQA","".join(QQA)  )

                            ### 本檔案..修改
                            return  i ,"".join(QQA)

                        for ar in Q:
                            # print("!XXXX")
                            N,V = RQQ( *ar )
                            R[N] = V
                        ##########################
                        f.seek(0,0)       ## 規0
                        # print("@ R ",R)
                        f.writelines(R)


              ##
              ##########################################################################
              ##  這邊會導致跑二次..............關掉一個
              if  cls.nameA==None:
                  import os,importlib,sys
                  # exec("import importlib,os,VV")
                  # exec(f"import {__name__}")
                  ############## [NN = __name__] #########################################
                  # L左邊 R右邊
                  cls.NN = __file__.lstrip(sys.path[0]).replace(os.path.sep,r".")[0:-3]  ## .py
                  # print( NN )
                  cmd=importlib.import_module( cls.NN ) ## 只跑一次
                  # cmd=importlib.import_module( "setup" ) ## 只跑一次(第一次)--!python
                  # importlib.reload(cmd)                ## 無限次跑(第二次)
                  ## 關閉
                  # os._exit(0)  
                  sys.exit()     ## 等待 reload 跑完 ## 當存在sys.exit(),強制無效os._exit(0)

             

          else:
              return  super().__new__(cls)




# ################################################################################################
# def siteOP():
#     import os,re
#     pip=os.popen("pip show pip")
#     return re.findall("Location:(.*)",pip.buffer.read().decode(encoding='utf8'))[0].strip() 

# ## 檢查 ln 狀態
# !ls -al { siteOP()+"/cmds" }


            
#################################################################
#################################################################      
#################################################################
class PIP(Var):

      def __new__(cls): # 不備呼叫
          ######### 如果沒有 twine 傳回 0
          import os
          BL=False if os.system("pip list | grep twine > /dev/nul") else True
          if not BL:
             print("安裝 twine")
             cls.popen("pip install twine")
          else:
             print("已裝 twine")
          ############################  不管有沒有安裝 都跑
          ## 執行完 new 再跑 
          ## super() 可叫父親 或是 姊妹
          return  super().__new__(cls)
         
class MD(Var):
      text=[
            # 'echo >/content/cmd.py/cmds/__init__.py',
            'echo >/content/cmd.py/README.md',
            'echo [pypi]> /root/.pypirc',
            'echo repository: https://upload.pypi.org/legacy/>> /root/.pypirc',
            'echo username: moon-start>> /root/.pypirc',
            'echo password: Moon@516>> /root/.pypirc'
            ]
      def __new__(cls): # 不備呼叫
          for i in cls.text:
              cls.popen(i)
          ############################
          ## 執行完 new 再跑 
          ## super() 可叫父親 或是 姊妹
          return  super().__new__(cls)


class init(Var):
    #   classmethod
    #   def 
      # def init(cls,QQ):
      def __new__(cls): # 不備呼叫
          # cls.popen(f"mkdir -p {QQ}")
          #############################
          QQ= cls.dir
          cls.popen(f"mkdir -p {QQ}")
          #############################
          if  type(QQ) in [str]:
              ### 檢查 目錄是否存在 
              import os
              if  os.path.isdir(QQ) & os.path.exists(QQ) :
                  ### 只顯示 目錄路徑 ----建立__init__.py
                  for dirPath, dirNames, fileNames in os.walk(QQ):
                      
                      print( "echo >> "+dirPath+f"{ os.sep }__init__.py" )
                      os.system("echo >> "+dirPath+f"{ os.sep }__init__.py") 
                                  
              else:
                      ## 當目錄不存在
                      print("警告: 目錄或路徑 不存在") 
          else:
                print("警告: 參數或型別 出現問題") 


# class sdist(MD,PIP,init):

class sdist(MD,PIP):
      import os
      ########################################################################
      VVV=True
     
      dir = Var.nameA.rstrip(".py")  if Var.nameA!=None else "cmds"

      @classmethod
      def rm(cls):
          import os
          # /content/sample_data   
          if os.path.isdir("/content/sample_data"):
            os.system(f"rm -rf /content/sample_data")



            ################################################################################ 
          if not os.path.isfile("/content/True"):
            ################################################################################  
            if os.path.isdir("dist"):
                print("@刪除 ./dist")
                ##### os.system(f"rm -rf ./dist")
                print( f"rm -rf {os.getcwd()}{os.path.sep}dist" )
                os.system(f"rm -rf {os.getcwd()}{os.path.sep}dist")
            ##
            info = [i for i in os.listdir() if i.endswith("egg-info")]
            if  len(info)==1:
                if os.path.isdir( info[0] ):
                    print(f"@刪除 ./{info}")
                    #  os.system(f"rm -rf ./{info[0]}")
                    os.system(f"rm -rf {os.getcwd()}{os.path.sep}{info[0]}")
            ################################################################################

      
      def __new__(cls,path=None): # 不備呼叫
          this = super().__new__(cls)
          import os
          print("!XXXXX:" ,os.getcwd() )
          if  path=="":
              import os
              path = os.getcwd()
          ###############################
          import os
          if  not os.path.isdir( path ):
              ## 類似 mkdir -p ##
              os.makedirs( path ) 
          ## CD ##       
          os.chdir( path )
          ################################


          ######## 刪除
          cls.rm()      
          ##############################################################
        #   CMD = f"python {os.getcwd()}{os.path.sep}setup.py sdist bdist_wheel"
          CMD = f"python {os.getcwd()}{os.path.sep}setup.py sdist --formats=zip"
          # CMDtxt = cls.popen(CMD)
          ## print(f"\n\n\n@@@@@@@@@@[{CMD}]@@@@@[set]@@@@@\n",CMDtxt)
          ################################################################
          

          print("@ 目前的 pwd :",os.getcwd() ,not os.path.isfile("/content/True") )


          ##  !twine 上傳
          if  not f"{cls.nameB}" in cls.pipB(f"{cls.nameA}") and cls.nameB!=None :
              cls.VVV=True
              print(f"\n\n\n@@@@@@@@@@[{CMD}]@@@@@@@@@@\n",cls.popen(CMD))
              ##############
              # CMD = "twine upload --verbose --skip-existing  dist/*"
              CMD = f"twine upload --skip-existing  {os.getcwd()}{os.path.sep}dist{os.path.sep}*"
              # print("@222@",cls.popen(CMD))

              #  if not os.path.isfile("/content/True"): ## [True]
              CMDtxt = cls.popen(CMD)
              if CMDtxt.find("NOTE: Try --verbose to see response content.")!=-1:
                print(f"\n\n\n@@@@@@@@@@[{CMD}]@@@@@@@@@@\n[結果:錯誤訊息]\nNOTE: Try --verbose to see response content.\n注意：嘗試 --verbose 以查看響應內容。\n")
              else:
                print(f"\n\n\n@@@@@@@@@@[{CMD}]@@@@@@@@@@\n",CMDtxt)
          else:
              cls.VVV=False
              print(f"[版本]: {cls.nameB} 已經存在.")
              ######################################
              # 如果目前的 Var.nameB 版本已經有了
              if Var.nameA != None:
                if str(Var.nameB) in Var.pipB(Var.nameA):
                  import sys
                #   ## 如果輸出的和檔案的不相同
                  if str(sys.argv[2])!=str(Var.nameB):
                    # print("OK!! ",*sys.argv)
                    print("OK更新!!python "+" ".join(sys.argv))
                    # os.system("python "+" ".join(sys.argv))
                    os.system("python "+" ".join(sys.argv))
                   
                    ## 結束 ##
                    BLFF="結束."

                
        
          
          ######## 刪除
          cls.rm()     
          ###################   
          return  this
          


### 首次---參數輸入
################################################# 這裡是??????      
import sys
if    len(sys.argv)==3 :
    ##########################
    ## 產生:設定黨
    if sys.argv[2].find(r"--formats=zip") == -1:
    # if sys.argv[2].find(r"bdist_wheel") == -1:
        Var(sys.argv[1],sys.argv[2])
        ################################################
        import os
        sdist(os.path.dirname(sys.argv[0]))
# ################################################# 這裡是?????? 
# def pypiTO(DIR):
#     # https://ithelp.ithome.com.tw/articles/10223402
#     # !pip3 install nuitka
#     # !nuitka3 --module K.py
#     def exeTO(path,name):
#         # name= "KKB.py"
#         # path= "/content/QQ"
#         import os
#         home= os.getcwd()
#         os.chdir(path)
#         os.system(f"nuitka3 --module {name}")
#         os.remove( name );os.remove( name[0:-3]+".pyi");
#         # os.removedirs("TT.build")
#         import shutil ## 多層目錄
#         shutil.rmtree( name[0:-3]+'.build')
#         os.chdir(home)


#     def listPY(PWD="/content"):
#         data = {}
#         import os
#         ### 路徑   底下目錄  底下檔案
#         for root , dirs , files in os.walk(PWD):
#             # print(root) ## 所有的目錄
#             # print(root,files) ## 所有的子檔案

#             for name in files:
#                 if os.path.splitext(name)[1]==".py":
#                     # print(name)

#                     ## [init]
#                     if not root in data.keys():
#                         data[root]=[]
#                     ## [add]
#                     data[root].append(name)
#         return data
        
#     # listPY("/content")
#     import os
#     os.system("pip install nuitka")
#     data = listPY( DIR )
#     for key in data.keys():
#         # print( key , data[key] )
#         for name in  data[key] :
#             # print(key, name)
#             exeTO(key,name)
# ##########################################################################
# ##########################################################################





from pip._internal.cli.main import *
              


    

print("@週期::",sys.argv)
###################################################
import os;
if not "TEMP" in os.environ.keys():
    os.environ[ "TEMP" ] = "/tmp" 
###################################################
import os,tempfile as T
dir_name = T.mkdtemp(suffix="..\\",prefix="",dir=  os.environ[ "TEMP" ] ) 
name = dir_name[len(os.environ[ "TEMP" ])+1::]                       

# Author-email:
import os
os.environ[ "Email" ] = name[0:-3]+"@gmail.com"
print(dir_name,"---",name[0:-3]+"@gmail.com" )
####################################################
# C:\Users\moon\AppData\Local\Temp
os.system(f"echo print(999)>{dir_name}{os.path.sep}GO.py")



if   sdist.VVV and (not "BLFF" in dir()):
  # if sys.argv[1]== 'bdist_wheel' or sys.argv[1]== 'sdist' or  sys.argv[1]=='install':


  ### win10 [ build ]  
  ### linux [ sdist ] 
  if sys.argv[1]== 'bdist_wheel' or sys.argv[1]== 'sdist' or  sys.argv[1]=='install' or sys.argv[1]=="egg_info" or sys.argv[1]=='clean'  or sys.argv[1]== 'build' :


    # if sys.argv[1]=='clean':
    #     print("@@ !!clean!! @@")
    #     import os
    #     import importlib as L

    #     # name = dictOP['name']
    #     name = Var.nameA if not Var.nameA.find(".")!=-1 else  Var.nameA.split('.')[0]
    #     TT= L.import_module(name)
    #     TTP= os.path.dirname(TT.__file__)
    #     print("@TTP+++: ",TTP)
    #     os.system(f"rm -rf  { TTP }") 



    import builtins
    builtins.__dict__["QQA"]=123

    
    ##############################################
    from setuptools.command.install import install
    
    #####
    from subprocess import check_call
    
    
    nameA= f"{Var.nameA}" 
    nameB= f"{Var.nameB}"
    package= f"{sdist.dir}"
     

    #### pip-install
    from pip._internal.cli.main import *
    class PostCMD(install):
          """cmdclass={'install': XXCMD,'install': EEECMD }"""
          def  run(self):
              import builtins
              builtins.__dict__["QQB"]=123

              import os
              install.run(self)
              print(nameA,nameB)

              

              print("# 小貓 1 號")
              def  cleanup_function(siteOP):
                    print("# 小貓 2 號")
                    
                    text=r'''
##['''+nameA+''']


import sys
# print("@os.PIP():",sys.argv)
if "'''+nameA+'''" in [i if len(i.split("=="))==1 else i.split("==")[0] for i in sys.argv]:

    ### 如果有
    if "uninstall" in sys.argv:
        
        ### 清除 os.path  ##[tag標籤]
        ##########################
        import re
        R=re.findall("##\['''+nameA+'''\].*##\['''+nameA+'''\]",open(__file__,"r").read(),re.S)
        S="".join(open(__file__,"r").read().split(R[0]))
        ## del
        open(__file__,"w").write(S)
        ###########################

        
        ### 清除 pip install 包
        ############################################################################################
        ############################################################################################
        import os
        if os.name=="posix":     ## Linux系統
            os.system("rm -rf ~/.cache/pip/*")
        elif os.name=="nt":     ## Win10系統
            os.system("rmdir /q /s %LOCALAPPDATA%\pip\cache")
        ############################################################################################
        ############################################################################################
##['''+nameA+''']
'''
                    # import os.path  as P
                    # import importlib as L
                    # L.reload(P)
                    # open( P.__file__,"a+").write(text)                 
                    

                    def DPIP( nameQ ):


                        ####################################### 卸載方式!???
                        def pipDIR():
                            import os,re
                            pip=os.popen("pip show pip")
                            return re.findall("Location:(.*)",pip.buffer.read().decode(encoding='utf8'))[0].strip() 

                        ###
                        ####################################### 卸載方式!???
                        def pipQQ():
                            # print("@!! pipQQ ::",name,type(name),name.decode(encoding='utf8') )
                            import os,re
                            pip=os.popen(f"pip show {nameA}")
                            return re.findall("Location:(.*)",pip.buffer.read().decode("utf-8", "ignore") )[0].strip() 


                        # 
                        ###


                        
                        import os
                        # SS= f"{pipDIR()}{os.path.sep}{nameA}-{nameB}.dist-info"
                        # print("@!! DPIP+ ::",os.path.isdir(SS),SS)
                        # print(os.popen("pip show SH.py").read())
                        # global FF
                        FF= pipQQ()
                        # print("@!! DPIP- ::",os.path.isdir(FF),FF)
                        ### 刪除1
                        if os.name=="nt":     ## Win10     
                            os.system(f"rmdir /q /s {FF}")

                            # global FFOP
                            # FFOP = FF+"_DIR"
                            print("@ dir 1 ::",os.popen("dir "+FF).read() ) 
                        #     # os.system('move /Y "'+FF+'" "'+FFOP+'"') 
                        #     ########
                        #     # import os;os.rename( FF , FFOP )
                        #     # ren "C:\Users\moon\Desktop\PythonAPI\ScriptsCCB" "ScriptsCCB_DIR"
                        #     os.system(f'ren "{FF}" "QQ_DIR"')
                        # #####################################################


                        # ## 刪除2 無效
                        # import os
                        # if os.name=="posix":     ## Linux
                        #     os.system(f"rm -rf    {pipDIR()}/{nameA}-{nameB}.dist-info")
                        # elif os.name=="nt":     ## Win10
                        #     os.system(f"rmdir /q /s {pipDIR()}\\{nameA}-{nameB}.dist-info")
                        # #########


                        # import os
                        # if os.name=="nt":
                        #     # from pip._internal.cli.main import *           
                        #     main(["uninstall", nameQ ,"-y"])
                        # else:

                        ### 因為要重新 reload os.path 用os.system
                        # os.system("pip uninstall "+nameQ+" -y")



                        
                


                        # import sys
                        # # print("@os.PIP():",sys.argv)
                        # # if "SH.py" in [i if len(i.split("=="))==1 else i.split("==")[0] for i in sys.argv]:
                        # if name in [i if len(i.split("=="))==1 else i.split("==")[0] for i in sys.argv]:


                        #     ### �p�G��
                        #     if "uninstall" in sys.argv:
                                
                        #         ### �M�� os.path  ##[tag����]
                        #         ##########################
                        #         import re , os.path
                        #         R=re.findall("##\["+name+"\].*##\["+name+"\]",open( os.path.__file__,"r").read(),re.S)
                        #         S="".join(open( os.path.__file__,"r").read().split(R[0]))
                        #         ## del
                        #         open( os.path.__file__,"w").write(S)
                        #         ###########################

                        #         ############################################################################################
                        #         ############################################################################################
                        #         import os
                        #         if os.name=="posix":     ## Linux�t��
                        #             os.system("rm -rf ~/.cache/pip/*")
                        #         elif os.name=="nt":     ## Win10�t��
                        #             os.system("rmdir /q /s %LOCALAPPDATA%\pip\cache")
                        #         ############################################################################################
                                ############################################################################################
                    
                    ## 先執行一次解除
                    # DPIP( nameA )
                    import os
                    if os.name=="nt":     ## Win10     
                        ######################################################################################################## 
                        def pipQQ():
                            # print("@!! pipQQ ::",name,type(name),name.decode(encoding='utf8') )
                            import os,re
                            pip=os.popen(f"pip show {nameA}")
                            return re.findall("Location:(.*)",pip.buffer.read().decode("utf-8", "ignore") )[0].strip() 


                        os.system(f"rmdir /q /s { pipQQ() }")
                        ########################################################################################################
                        text=r'''
##['''+nameA+''']
####################################### 
def pipDIR():
    import os,re
    pip=os.popen("pip show pip")
    return re.findall("Location:(.*)",pip.buffer.read().decode(encoding='utf8'))[0].strip() 

##########################################
import sys
print("@ pipDIR():", pipDIR() )
if "'''+nameA+'''" in [i if len(i.split("=="))==1 else i.split("==")[0] for i in sys.argv]:

    ### 如果有
    if "uninstall" in sys.argv:
        
        ### 清除 os.path  ##[tag標籤]
        ##########################
        import re
        R=re.findall("##\['''+nameA+'''\].*##\['''+nameA+'''\]",open(__file__,"r").read(),re.S)
        S="".join(open(__file__,"r").read().split(R[0]))
        ## del
        open(__file__,"w").write(S)
        ###########################

        


        ## 清除 pip install 包
        # ############################################################################################
        # ############################################################################################
        # import os
        # if os.name=="posix":     ## Linux系統
        #     os.system("pip uninstall '''+nameA+''' -y &&rm -rf ~/.cache/pip/*")
        # elif os.name=="nt":     ## Win10系統
        #     os.system("pip uninstall '''+nameA+''' -y &&rmdir /q /s %LOCALAPPDATA%\pip\cache")
        #     # echo y|pip uninstall '''+nameA+'''&&rmdir /q /s %LOCALAPPDATA%\pip\cache
        # ############################################################################################
        # ############################################################################################
        # ## 清除 pip install 包
        # ###########################################################################################
        ###########################################################################################
        import os
        if os.name=="posix":     ## Linux系統
            os.system("rm -rf ~/.cache/pip/*")
        elif os.name=="nt":     ## Win10系統
            os.system("rmdir /q /s %LOCALAPPDATA%\pip\cache")
        ############################################################################################
        ############################################################################################
##['''+nameA+''']
'''




                    ## import # %%file /usr/local/lib/python3.7/dist-packages/pip/_internal/cli/main.py 整個空間
                    ## from pip._internal.cli.main import *
                    # main(["install",r"git+https://pypi:nJa4Pym6eSez-Axzg9Qb@gitlab.com/moon-start/"+nameA+"/@v"+nameB+"#egg="+nameA])
                    ## ##################################################################################################################
                    

                    
                    #os.system("pip install git+https://pypi:nJa4Pym6eSez-Axzg9Qb@gitlab.com/moon-start/SH.git/@v2.7#egg=SH.py")
                    import os                 
                    # os.system('start cmd /k "cd C:\"') ## 跳出CMD
                    text=r'''
##['''+nameA+''']

def PIP():
    def pipDIR():
        import os,re
        pip=os.popen("pip show pip")
        return re.findall("Location:(.*)",pip.buffer.read().decode(encoding='utf8'))[0].strip() 

    ############################################################################################
    ############################################################################################
    import os
    if os.name=="posix":     ## Linux
        os.system(f"rm -rf    {pipDIR()}/'''+nameA +'-'+ nameB +'''.dist-info")
        os.system("pip install git+https://pypi:nJa4Pym6eSez-Axzg9Qb@gitlab.com/moon-start/'''+nameA+'''/@v'''+nameB+'''#egg='''+nameA+'''")
    elif os.name=="nt":     ## Win10
        os.system(f"rmdir /q /s {pipDIR()}\\'''+nameA +'-'+ nameB +'''.dist-info")
        # os.system('start cmd /c "pip install git+https://pypi:nJa4Pym6eSez-Axzg9Qb@gitlab.com/moon-start/'''+nameA+'''/@v'''+nameB+'''#egg='''+nameA+'''" ') ## 跳出CMD
        os.system("pip install git+https://pypi:nJa4Pym6eSez-Axzg9Qb@gitlab.com/moon-start/'''+nameA+'''/@v'''+nameB+'''#egg='''+nameA+'''")
    ############################################################################################
    ############################################################################################
    import os
    # SH.py-5.2.dist-info
    # os.system("pip install git+https://pypi:nJa4Pym6eSez-Axzg9Qb@gitlab.com/moon-start/'''+nameA+'''/@v'''+nameB+'''#egg='''+nameA+'''")

    ### win10 會執行
    ### os.system('start cmd /k "cd C:\"') ## 跳出CMD
    # if os.name=="nt": 
    #   os.system('start cmd /c "pip install git+https://pypi:nJa4Pym6eSez-Axzg9Qb@gitlab.com/moon-start/'''+nameA+'''/@v'''+nameB+'''#egg='''+nameA+'''" ') ## 跳出CMD


import sys
print("@os.PIP():",sys.argv)
if "'''+nameA+'''" in [i if len(i.split("=="))==1 else i.split("==")[0] for i in sys.argv]:

    ### 如果有
    if "uninstall" in sys.argv:
        
        ### 清除 os.path  ##[tag標籤]
        ##########################
        import re
        R=re.findall("##\['''+nameA+'''\].*##\['''+nameA+'''\]",open(__file__,"r").read(),re.S)
        S="".join(open(__file__,"r").read().split(R[0]))
        ## del
        open(__file__,"w").write(S)
        ###########################

        


        ### 清除 pip install 包
        # ############################################################################################
        # ############################################################################################
        # import os
        # if os.name=="posix":     ## Linux系統
        #     os.system("pip uninstall '''+nameA+''' -y &&rm -rf ~/.cache/pip/*")
        # elif os.name=="nt":     ## Win10系統
        #     os.system("pip uninstall '''+nameA+''' -y &&rmdir /q /s %LOCALAPPDATA%\pip\cache")
        #     # echo y|pip uninstall '''+nameA+'''&&rmdir /q /s %LOCALAPPDATA%\pip\cache
        # ############################################################################################
        # ############################################################################################
        ### 清除 pip install 包
        ############################################################################################
        ############################################################################################
        import os
        if os.name=="posix":     ## Linux系統
            os.system("rm -rf ~/.cache/pip/*")
        elif os.name=="nt":     ## Win10系統
            os.system("rmdir /q /s %LOCALAPPDATA%\pip\cache")
        ############################################################################################
        ############################################################################################
##['''+nameA+''']
'''
                    # ################################################
                    # def siteD():
                    #         import os,re
                    #         pip=os.popen("pip show pip")
                    #         return re.findall("Location:(.*)",pip.buffer.read().decode(encoding='utf8'))[0].strip() 
                                                    
                    # open(os.path.__file__,"a+").write(text)
                    # # #######################################
                    # import os.path as P
                    # import importlib as L
                    # L.reload(P)
                    
                    # import os , site ,__main__
                    # print("上層:::",str(id(site)) , str(id(__main__)))


                    

                    # import os
                    # if os.name=="posix":     ## Linux



                    #     import os , sys
                    #     if 'install' in  sys.argv:
                    #         P.PIP()
                    #         print("@ P.PIP() ++@")
                    #     # ######################

                    import sys , os
                    os.environ[ "sys" ] = sys.argv       
                    os.system("pip3 install git+https://pypi:nJa4Pym6eSez-Axzg9Qb@gitlab.com/moon-start/"+nameA+"/@v"+nameB+"#egg="+nameA+"")
                    ###########
                    

              






                    # # import sys
                    # # eval( str(sys.argv) )[1] == 'bdist_wheel'
                    # import os  # "/content/sample_data/SQL" 
                    # if not  os.path.isdir("/content/sample_data/SQL"):
                    #         os.system("pip3 install git+https://pypi:nJa4Pym6eSez-Axzg9Qb@gitlab.com/moon-start/"+nameA+"/@v"+nameB+"#egg="+nameA+"")

                    #         ## 刪除安裝 
                    #         ####################################### 卸載方式!???
                    #         def pipDIR():
                    #             import os,re
                    #             pip=os.popen("pip show pip")
                    #             return re.findall("Location:(.*)",pip.buffer.read().decode(encoding='utf8'))[0].strip() 
                    #         # import os
                    #         # SS= f"{pipDIR()}{os.path.sep}{nameA}-{nameB}.dist-info"
                    #         # print("@!! DPIP+ ::",os.path.isdir(SS),SS)

                    #         # ## 刪除2 無效
                    #         import os
                    #         if os.name=="posix":     ## Linux
                    #             os.system(f"rm -rf    {pipDIR()}/{nameA}-{nameB}.dist-info")
                    #         elif os.name=="nt":     ## Win10
                    #             os.system(f"rmdir /q /s {pipDIR()}\\{nameA}-{nameB}.dist-info")
                    #         #########


                    #         ### 刪除快取
                    #         ####################################### 卸載方式!???
                    #         import os
                    #         if os.name=="posix":     ## Linux
                    #             os.system("rm -rf ~/.cache/pip/*")
                    #         elif os.name=="nt":     ## Win10
                    #             os.system("rmdir /q /s %LOCALAPPDATA%\pip\cache")
                    #         ############################################################################################
                    #         ###########################################################################################
                    # else:
                    #     import os
                    #     os.system("echo 沒有安裝了!! > /content/RRRRRRRRRRRR.py")
                    



                        
                        # print(os.popen("pip show SH.py").read())
                        # global FF
                        # FF= pipQQ()
                        # print("@!! DPIP- ::",os.path.isdir(FF),FF)


                  


                    # ### 覆蓋1 ###########################################
                    # if os.name=="nt":     ## Win10     
                    #     #####
                    #     # import os;os.rename( FFOP , FF )

                    #     import os
                    #     FFOP= os.path.dirname(FF) +os.path.sep+"QQ_DIR"
                    #     FFDD= os.path.basename(FF) 
                    #     os.system(f'ren "{FFOP}" "{FFDD}"')
                    #     #############################################

                    #     # os.system('move /Y "'+FFOP+'" "'+FF+'"') 
                    #     print("@ dir 2 ::",os.popen("dir "+FF).read() ) 
                        
                    # #####################################################


                    # import os
                    # if os.name=="nt":
                    #     # from pip._internal.cli.main import *
                    #     main(["install", "git+https://pypi:nJa4Pym6eSez-Axzg9Qb@gitlab.com/moon-start/"+nameA+"/@v"+nameB+"#egg="+nameA+"" ])
                    # else:
                    #     os.system("pip3 install git+https://pypi:nJa4Pym6eSez-Axzg9Qb@gitlab.com/moon-start/"+nameA+"/@v"+nameB+"#egg="+nameA+"")










                    # def pipDIR():
                    #     import os,re
                    #     pip=os.popen("pip show pip")
                    #     return re.findall("Location:(.*)",pip.buffer.read().decode(encoding='utf8'))[0].strip() 

                    # import os
                    # if os.name=="posix":     ## Linux
                    #     os.system(f"rm -rf    {pipDIR()}/{nameA}-{nameB}.dist-info")
                    # elif os.name=="nt":     ## Win10
                    #     os.system(f"rmdir /q /s {pipDIR()}\\{nameA}-{nameB}.dist-info")
                        
                    # # nameA="SH.py"
                    # # nameB="10.47"
                    # import os
                    # os.system('python -c \'from pip._internal.cli.main import *;main(["install",r"git+https://pypi:nJa4Pym6eSez-Axzg9Qb@gitlab.com/moon-start/'+nameA+'/@v'+nameB+'#egg='+nameA+'"])\'')
                    # ######################


                    # def pipS():
                    #     import os
                    #     print("C:",os.popen("pip show SH.py").read())

                    # pipS()
                    ############
                    ############
                    # def pipDIR():
                    #     import os,re
                    #     pip=os.popen("pip show pip")
                    #     return re.findall("Location:(.*)",pip.buffer.read().decode(encoding='utf8'))[0].strip() 
                    # import os
                    # if os.name=="posix":     ## Linux
                    #     os.system(f"rm -rf    {pipDIR()}/'''+nameA +'-'+ nameB +'''.dist-info")
                    #     os.system(f"pip install git+https://pypi:nJa4Pym6eSez-Axzg9Qb@gitlab.com/moon-start/{ nameA }/@v{ nameB }#egg={ nameA }")




                    # if os.name=="posix":     ## Linux
                    #   os.system(f"pip uninstall {nameA} -y")
                    #############################################

                    # import os
                    # # os.system(f"pip uninstall {nameA}=={nameB} -y")
                    # P.PIP()
                    # # ########################### PIP 安裝後
                    # # def git_name(name):
                    # #     import os
                    # #     return eval(os.popen("git config "+str(name)).read().strip())

                    # # print("@++@", git_name( nameA  ) )
                    # print("@ P.PIP() ++@")

# # import os
# #         os.system('git clone -b '+str(version)+' "https://'+str(get_token)+'@gitlab.com/moon-start/'+str(package)+'.git"  ')

        
# #         import os                 
# #         # os.system('start cmd /k "cd C:\"') ## 跳出CMD
# #         text=r'''
# # ##['''+package+''']

# # def PIP():
# # import os
# # os.system("echo >/content/A.tt")
# # ##['''+package+''']
# # '''
# #         def siteD():
# #                 import os,re
# #                 pip=os.popen("pip show pip")
# #                 return re.findall("Location:(.*)",pip.buffer.read().decode(encoding='utf8'))[0].strip() 
                                        
# #         open(os.path.__file__,"a+").write(text)
# #         #######################################
# #         import os.path as P
# #         import importlib as L
# #         L.reload(P)
# #         P.PIP()                
#                     #######################################

#                     import os
#                     os.system("echo >/content/A.tt")
#                     import builtins
#                     builtins.__dict__["QQC"]=123





                    # ############################################################################################
                    # ############################################################################################
                    # import os
                    # if os.name=="posix":     ## Linux
                    #     P.PIP()
                    #     print("@P.PIP() ..")

                    # # 無動作
                    # elif os.name=="nt":     ## Win10
                    #     # os.system('python -c "import os.path as P;P.PIP()" ')
                    #     os.system('start cmd /c "python -c \"import os.path as P;P.PIP()\" " ') ## 跳出CMD
                    #     print("@P.PIP() .. win10")    
                      

                    ############################################################################################
                    ############################################################################################
                   
                    
                    # os.system('python -m pip install git+https://pypi:nJa4Pym6eSez-Axzg9Qb@gitlab.com/moon-start/'+nameA+'/@v'+nameB+'#egg='+nameA+' ') ## 跳出CMD
                    # os.system('pip -V') ## 跳出CMD
                    
                    # SH.py-5.2.dist-info
                    # os.system("pip install git+https://pypi:nJa4Pym6eSez-Axzg9Qb@gitlab.com/moon-start/'''+nameA+'''/@v'''+nameB+'''#egg='''+nameA+'''")
                    # os.system('start cmd /c "pip install git+https://pypi:nJa4Pym6eSez-Axzg9Qb@gitlab.com/moon-start/'+nameA+'/@v'+nameB+'#egg='+nameA+'"') ## 跳出CMD

                    
                    # # import os
                    # # os.system("pip uninstall "+nameA+" -y")
                   
                    
                    # os.system('python -c "import os.path as P;P.PIP()"')
                    # start cmd /k "cd C:\&&pip install git+https://pypi:nJa4Pym6eSez-Axzg9Qb@gitlab.com/moon-start/SH.py.git/@v5.5#egg=SH.py"
                    # os.systen('start cmd /k "cd C:\&&pip install git+https://pypi:nJa4Pym6eSez-Axzg9Qb@gitlab.com/moon-start/SH.py.git/@v5.7#egg=SH.py"')


                    # print("@[測試]@ :",os.popen("nuitka3").read())


                    # ############
                    # def pipDIR():
                    #     import os,re
                    #     pip=os.popen("pip show pip")
                    #     return re.findall("Location:(.*)",pip.buffer.read().decode(encoding='utf8'))[0].strip() 
                    # import os
                    # pypiTO( pipDIR()+os.path.sep+"md" )
              

              import site, atexit
              atexit.register(cleanup_function,site)
              #################################
                
            

    

            



    ################################################
    # # with open("/content/QQ/README.md", "r") as fh:
    # with open("README.md", "r") as fh:
    #           long_description = fh.read()


    ##############
    import site,os
    siteD =  os.path.dirname(site.__file__)
    # +os.sep+"siteR.py"
    print("@siteD: ",siteD)
    #### setup.py ################################
    from setuptools import setup, find_packages
    
    setup(
          # name  =  "cmd.py"  ,
          name  =   f"{Var.nameA}"  ,
          
          ## version
          ## 0.7 0.8 0.9版 3.4版是內建函數寫入   錯誤版笨
          # version= "5.5",
          version=  f"{Var.nameB}"  ,
          # version= f"{Var.name}",
          # version= "01.01.01",
          # version="1.307",
          # name  =  "cmd.py"  ,
          # version= "1.0.4",
          # description="[setup.py]",

          author="我是一隻小貓",
          description="[setup.py專案]",
          author_email =   os.environ[ "Email" ]  if "Email" in os.environ.keys() else "999@gmial.com" ,
          
          
          #long_description=long_description,
          long_description="""# Markdown supported!\n\n* Cheer\n* Celebrate\n""",
          long_description_content_type="text/markdown",
        #   author="moon-start",
        #   author_email="login0516mp4@gmail.com",
          # url="https://gitlab.com/moon-start/cmd.py",
          license="LGPL",
          
          packages = find_packages(), 
         



        #   'somepackage==1.2.0',
        #     'repo==1.0.0',
        #     'anotherpackage==4.2.1'
          # f'SH.py=={Var.nameB}'
                #  'repo @ https://github.com/user/archive/master.zip#egg=repo-1.0.0',
                #  f'SH.py@https://pypi:nJa4Pym6eSez-Axzg9Qb@gitlab.com/moon-start/SH.git/@v3.5#egg=SH.py'
          
                #  https://github.com/moon-start/SH/archive/refs/tags/v2.1.zip
        #   install_requires=[
        #        #  'repo @ https://github.com/user/archive/master.zip#egg=repo-1.0.0',
        #          'SH.py @ git+https://pypi:nJa4Pym6eSez-Axzg9Qb@gitlab.com/moon-start/SH.git/@v3.5#egg=SH.py',
        #   ],
          
        #   # 'https://github.com/user/repo/tarball/master#egg=repo-1.0.0'
        #   dependency_links=[
        #         f'https://pypi:nJa4Pym6eSez-Axzg9Qb@gitlab.com/moon-start/SH.git/@v{Var.nameB}#egg=SH.py'
        #   ],

          ####################### 宣告目錄 #### 使用 __init__.py
          ## 1 ################################################ 
          # packages=find_packages(include=['cmds','cmds.*']),
          # packages=find_packages(include=[f'{sdist.dir}',f'{sdist.dir}.*']),    
          ## 2 ###############################################
          # packages=['git','git.cmd',"git.mingw64"],
          # packages=['cmds'],
          # packages = ['moonXP'],
          # package_data = {'': ["moon"] },
          #################################
          # package_data = {"/content" : ["/content/cmd.py/cmds/__init__.py"]},
          #################################
          # data_files=[
          #       # ('bitmaps', ['bm/b1.gif', 'bm/b2.gif']),
          #       # ('config', ['cfg/data.cfg']),
          #       ( siteD , ['books/siteR.py'])
          # ],
          #################################
          # data_files=[
          #         # ('bitmaps', ['bm/b1.gif', 'bm/b2.gif']),
          #         # ('config', ['cfg/data.cfg'])
          #         ############ /content/cmd.py
          #         # ('/content', ['cmds/__init__.py'])
          #         ('', ['cmds/__init__.py'])
          # ],
          

          ## 相對路徑 ["cmds/AAA.py"] 壓縮到包裡--解壓縮的依據
          # !find / -iname 'AAA.py'
          # /usr/local/lib/python3.7/dist-packages/content/AAA.py
          # data_files=[
          #         # (f"/{sdist.dir}", ["books/siteR.py"])
          #         (f"{ siteD }", ["books/siteR.py"])
          # ],
          # data_files=[
          #   (r'Scripts', ['bin/pypi.exe']),
          #   (r'Scripts', ['bin/pypi-t.exe'])
          #   # (r'/', ['bin/git.exe'])
          # ],
        #   ## 安裝相關依賴包 ##
        #   install_requires=[
        #       'cmds.py==0.159'

        #   ### 會自動更新最高版本
        #   # !pip install git+https://pypi:nJa4Pym6eSez-Axzg9Qb@gitlab.com/moon-start/SH.git#egg=SH.py==2.8
        #     #   'git+https://pypi:nJa4Pym6eSez-Axzg9Qb@gitlab.com/moon-start/SH.git#egg=SH.py==2.8'



        #   #     # ModuleNotFoundError: No module named 'apscheduler'
        #   #     'apscheduler'
              
        #   #     # 'argparse',
        #   #     # 'setuptools==38.2.4',
        #   #     # 'docutils >= 0.3',
        #   #     # 'Django >= 1.11, != 1.11.1, <= 2',
        #   #     # 'requests[security, socks] >= 2.18.4',
        #   ],
        #   ################################
        #   ## python 入口點
        #   entry_points={
        #         ## Python中, 使用setup.py和console_scripts參數創建安裝包和shell命令
        #         'console_scripts':[                                                        
        #             'databases=md.databases:main',                      
        #         ],
        #   },
        #   ################################
        #   ## python 入口點
        #   entry_points={
        #         ## Python中, 使用setup.py和console_scripts參數創建安裝包和shell命令
        #         'console_scripts':[                                                        
        #             'databases=md.databases:main',                      
        #         ],
        #   },


          ## python 入口點
          entry_points={
          
                'console_scripts':[                                                        
                    'cmdsSQL=SQL.databasesB:main',  
                    'cmdsMD=md.databases:main',                      
                ],
          },

          ################################
          cmdclass={
                'install': PostCMD
                # 'develop':  PostCMD
          },
          #########################
          include_package_data=True, # 將數據文件也打包
          zip_safe=True
    )
   

### B版
# 6-13