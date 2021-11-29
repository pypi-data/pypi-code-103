import pandas as pd, numpy as np,pickle
import plotly.express as px, plotly.graph_objects as go
from dorianUtils.configFilesD import ConfigDashTagUnitTimestamp
from dorianUtils.configFilesD import ConfigDashRealTime
from dorianUtils.configFilesD import ConfigDashSpark
import subprocess as sp, os,re,glob, datetime as dt
from dateutil import parser
import time
pd.options.mode.chained_assignment = None  # default='warn'
class EmptyClass():pass

class SmallPowerMaster():
    def __init__(self):
        self.appDir  = os.path.dirname(os.path.realpath(__file__))
        self.confFolder = self.appDir + '/confFiles/'
        from PIL import Image # new import
        self._loadcolorPalettes()
        self.imgpeintre  = Image.open(self.confFolder + 'peintrepalette.jpeg')
        self.sylfenlogo  = Image.open(self.confFolder +  'logo_sylfen.png')
        self.constantsFile = self.confFolder + 'materialConstants.pkl'
        self._loadConstants()
        listCalculatedTags = ['STK_0'+str(k)+'.ET.SUM' for k in range(1,5)]

    def _loadConstants(self):
        self.cst = EmptyClass()
        if not os.path.exists(self.constantsFile):
            print(self.constantsFile,' converted to .pkl')
            self._dumpConfFiles()
        self.dfConstants=pickle.load(open(self.constantsFile,'rb'))
        for k in self.dfConstants.index:
            setattr(self.cst,k,self.dfConstants.loc[k].value)

    def _loadcolorPalettes(self):
        import pickle
        colPal = pickle.load(open(self.confFolder+'palettes.pkl','rb'))
        colPal['reds']     = colPal['reds'].drop(['Misty rose',])
        colPal['greens']   = colPal['greens'].drop(['Honeydew',])
        colPal['blues']    = colPal['blues'].drop(['Blue (Munsell)','Powder Blue','Duck Blue','Teal blue'])
        colPal['magentas'] = colPal['magentas'].drop(['Pale Purple','English Violet'])
        colPal['cyans']    = colPal['cyans'].drop(['Azure (web)',])
        colPal['yellows']  = colPal['yellows'].drop(['Light Yellow',])
        self.colorPalettes = colPal
        self.colorshades = ['greens','blues','reds','magentas','oranges','yellows','cyans','blacks']
        for c in self.colorshades:
            self.colorPalettes[c]=self.colorPalettes[c].sample(frac=1)

    def _buildColorCode(self):
        dftagColorCode = pd.read_csv(self.confFolder + 'color_codeTags.csv',index_col=0,keep_default_na=False)
        self.unitDefaultColors = {
            'blacks':['%','TOR','RGB','watchdog','ETAT','Courbe','CMD','SN','u.a'],
            'magentas':['V DC'],
            'cyans':['A'],
            'oranges':['W AC','VAR AC','VA AC','kW AC','Kvar AC','KVA AC','kW DC','Wth','W DC'],
            'blues':['mbarg','barg'],
            'reds':['Nl/min','g/min','kg/h','m3/h'],
            'greens':['°C'],
            'yellows':['microS/cm','h']
        }

        from plotly.validators.scatter.marker import SymbolValidator
        raw_symbols = pd.Series(SymbolValidator().values[2::3])
        listLines=pd.Series(["solid", "dot", "dash", "longdash", "dashdot", "longdashdot"])
        d={}
        for k,v in self.unitDefaultColors.items():
            for l in v:d[l]=k
        self.unitDefaultColors=d
        self.allHEXColors=pd.concat([k['hex'] for k in self.colorPalettes.values()])
        self.allHEXColors=self.allHEXColors[~self.allHEXColors.index.duplicated()]

        tag = 'SIS.BAS_N2_PT_02_HM05'
        def assignRandomColor2Tag(tag):
            unitTag=self.getUnitofTag(tag[0]).strip()
            shadeTag=self.unitDefaultColors[unitTag]
            color=self.colorPalettes[shadeTag]['hex'].sample(n=1)
            return color.index[0]

        dftcc_color=dftagColorCode.reset_index()
        # generate random color/symbol/line for tags who are not in color_codeTags.csv
        dfRandomColorsTag = pd.DataFrame([k for k in self.dfPLC.index if k not in list(dftcc_color.TAG)])
        dfRandomColorsTag['colorName'] = dfRandomColorsTag.apply(lambda x: assignRandomColor2Tag(x),axis=1)
        dfRandomColorsTag['symbol'] =pd.DataFrame(raw_symbols.sample(n=len(dfRandomColorsTag),replace=True)).set_index(dfRandomColorsTag.index)
        dfRandomColorsTag['line'] = pd.DataFrame(listLines.sample(n=len(dfRandomColorsTag),replace=True)).set_index(dfRandomColorsTag.index)
        dfRandomColorsTag.columns=dftcc_color.columns
        dftcc_color = pd.concat([dfRandomColorsTag,dftcc_color])
        # dftcc_color['colorHEX'] = dfRandomColorsTag.apply(lambda x: self.allHEXColors.loc[x['colorName']],axis=1)
        self.dftagColorCode=dftcc_color.set_index('TAG')

    def _load_plcfile(self):
        self.plcfile = glob.glob(self.confFolder + '*.xlsm')[0]
        plcfilepkl = self.plcfile[:-5]+'.pkl'
        if not os.path.exists(self.confFolder + 'enumModeHUB.pkl'):
            self._convertplcfilesmallPower()
        self.dfPLC = pickle.load(open(plcfilepkl,'rb'))
        self.enumModeHUB = pickle.load(open(self.confFolder + 'enumModeHUB.pkl','rb'))

    def _convertplcfilesmallPower(self):
        ##############################
        start=time.time()
        #find the plcfile .xlsm
        import glob,pickle
        self.plcfile = glob.glob(self.confFolder + '/*.xlsm')[0]
        # get the enumerations of hub sytem modes
        enumModeHUB = pd.read_excel(plcfile,sheet_name='Enumérations',skiprows=1).iloc[:,1:3].dropna()
        enumModeHUB=enumModeHUB.set_index(enumModeHUB.columns[0]).iloc[:,0]
        enumModeHUB.index=[int(k) for k in enumModeHUB.index]
        for k in range(100):
            if k not in enumModeHUB.index:
                enumModeHUB.loc[k]='undefined'
        enumModeHUB = enumModeHUB.sort_index()
        enumModeHUB=enumModeHUB.to_dict()
        pickle.dump(dictmode,open(self.confFolder + 'enumModeHUB.pkl','wb'))
        print('loading enum xlsm file  in {:.2f} milliseconds'.format((time.time()-start)*1000))
        # PLCFILE
        start=time.time()
        dfPLC=pd.read_excel(plcfile,sheet_name='FichierConf_Jules')
        pickle.dump(dfPLC,open(self.confFolder + plcfile.split('/')[-1][:-5]+'.pkl','wb'))
        print('loading conf jules xlsm file  in {:.2f} milliseconds'.format((time.time()-start)*1000))

    def _dumpConfFiles(self):
        ##### material Constants
        dfConstants=pd.read_excel(self.confFolder + 'materialConstants.xlsx',sheet_name='thermo')
        dfConstants.columns=['description','variableName','value','unit']
        dfConstants = dfConstants.set_index('variableName').dropna()
        # dfConstants = dfConstants[['value','description','unit']]
        pickle.dump(dfConstants,open(self.confFolder + 'materialConstants.pkl','wb'))

    # ==============================================================================
    #                   computation functions/INDICATORS
    # ==============================================================================
    def DF_allPower(self,timeRange=None,whichPower='HE10',**kwargs):
        dfs=[]
        for group in self.powerGroups.index[:-1]:
            listTags = self.getTagsTU(self.powerGroups.loc[group].pattern)
            tagsHE = [k for k in listTags if len(re.findall('\.HE1\d{1}$',k))>0]
            tagsnotHE = [l for l in listTags if l not in tagsHE]
            listTags = tagsnotHE + [k for k in tagsHE if whichPower in k]
            print(listTags)
            df = self.DF_loadTimeRangeTags(timeRange,listTags,**kwargs)
            if not df.empty:
                if 'courant' in group.lower():
                    df=df*self.powerGroups.loc[group].voltage
                df=df.abs()# take absolute value of the power
                df['timestamp'] = df.index
                df=df.melt(id_vars='timestamp',ignore_index=True)
                df['Power group'] = group
                dfs.append(df)

        dfPtotal = self.DF_loadTimeRangeTags(timeRange,self.getTagsTU('SEH0\.JT_01\.'+whichPower),**kwargs)
        # dfPtotal = dfPtotal.ffill().bfill()
        df = pd.concat(dfs,axis=0)
        return df,dfPtotal

    def rendementCondenseur(self,timeRange_Window,fuites=0,nb='01',wholeDF=False,**kwargs):
        '''
        - timeRange_Window : int if realTime==True --> ex : 60*30*2
        [str,str] if not realtime --> ex : ['2021-08-12 9:00','2020-08-13 18:00']'''
        debit_eau = 'SEH1.L219_H2OP_FT_01.HM05'#g/min
        t_entree_condenseur='SEH1.HPB_CND_'+ nb +'_TT_01.HM05'
        t_sortie_condenseur='SEH1.HPB_CND_'+ nb +'_TT_03.HM05'
        listTags = [debit_eau,t_entree_condenseur,t_sortie_condenseur]
        if isinstance(timeRange_Window,list) :
            df   = self.DF_loadTimeRangeTags(timeRange_Window,listTags,**kwargs)
        else :
            df   = self.realtimeTagsDF(listTags,timeWindow=timeRange_Window,**kwargs)
        if not df.empty:
            df = df[listTags]
            df.columns =['debit_eau(g/min)','t_entree_condenseur','t_sortie_condenseur']

            dfTh=pd.DataFrame()
            dfTh['debit eau(g/s)'] = df['debit_eau(g/min)']/60
            dfTh['debit g/s(yc fuites)'] = dfTh['debit eau(g/s)']*(1-fuites)
            dfTh['refroidissement vapeur'] = (dfTh['debit g/s(yc fuites)']*self.cst.Cp_eau_vap*(df['t_entree_condenseur']-100)).apply(lambda x :max(0,x))
            dfTh['condensation'] = dfTh['debit g/s(yc fuites)']*self.cst.Cl_H2O
            dfTh['Refroidissement eau condensée'] = (dfTh['debit g/s(yc fuites)']*self.cst.Cp_eau_liq*(100-df['t_sortie_condenseur'])).apply(lambda x :max(0,x))
            dfTh['thermique azote'] = 3.9/60/22.4*self.cst.Mmol_N2*self.cst.Cp_N2*(df['t_entree_condenseur']-df['t_sortie_condenseur'])*(1-fuites)

            dfTh['total thermique'] = dfTh.sum(axis=1)
            df.columns=[k + ' : ' + l  for k,l in zip(df.columns,listTags)]
            df = pd.concat([df,dfTh],axis=1)
            if wholeDF:return df
            else :return df['total thermique']
        else : return df

    def bilanValo(self,timeRange_Window,nb='01',wholeDF=False,**kwargs):
        '''
        - timeRange_Window : int if realTime==True --> ex : 60*30*2
        [str,str] if not realtime --> ex : ['2021-08-12 9:00','2020-08-13 18:00']'''
        debit_eau = 'SEH1.L408_H2OR_FT_01.HM05'#g/min
        t_entree_valo='SEH1.HPB_CND_'+ nb +'_TT_02.HM05'
        t_sortie_valo='SEH1.HPB_CND_'+ nb +'_TT_04.HM05'
        listTags = [debit_eau,t_entree_valo,t_sortie_valo]
        if isinstance(timeRange_Window,list) :
            df   = self.DF_loadTimeRangeTags(timeRange_Window,listTags,**kwargs)
        else :
            df   = self.realtimeTagsDF(listTags,timeWindow=timeRange_Window,**kwargs)
        if not df.empty:
            df.columns = ['debit_eau(kg/h)','t_entree_valo','t_sortie_valo']

            dfValo = pd.DataFrame()
            dfValo['debit eau(g/s)'] = df['debit_eau(kg/h)']*1000/3600
            dfValo['echange valo'] = dfValo['debit eau(g/s)']*self.cst.Cp_eau_liq*(df['t_sortie_valo']-df['t_entree_valo'])
            df.columns=[k + ' : ' + l  for k,l in zip(df.columns,listTags)]
            df = pd.concat([df,dfValo],axis=1)
            if wholeDF:return df
            else :return df['echange valo']
        else : return df

    def rendement_GV(self,timeRange_Window,activePower=True,wholeDF=False,**kwargs):
        '''
        - activePower : active or apparente power
        - timeRange_Window : int if realTime==True --> ex : 60*30*2
        [str,str] if not realtime --> ex : ['2021-08-12 9:00','2020-08-13 18:00']'''

        debit_eau = self.getTagsTU('L213_H2OPa.*FT')#g/min
        if activePower:p_chauffants = self.getTagsTU('STG_01a.*JTW')
        else: p_chauffants = self.getTagsTU('STG_01a.*JTVA')
        t_entree_GV = self.getTagsTU('L211.*TT')
        t_sortie_GV = self.getTagsTU('L036.*TT')

        listTags = debit_eau+p_chauffants+t_entree_GV + t_sortie_GV
        if isinstance(timeRange_Window,list) :
            df   = self.DF_loadTimeRangeTags(timeRange_Window,listTags,**kwargs)
        else :
            df   = self.realtimeTagsDF(listTags,timeWindow=timeRange_Window,**kwargs)
        if not df.empty:
            df = df[listTags]
            df.columns = ['debit_eau(g/min)','power_gv1','power_gv2','power_gv3','t_entree_GV','t_sortie_GV']

            dfGV = pd.DataFrame()
            dfGV['debit eau(g/s)'] = df['debit_eau(g/min)']/60

            dfGV['power chauffe eau liq']  = (dfGV['debit eau(g/s)']*self.cst.Cp_eau_liq*(100-df['t_entree_GV'])).apply(lambda x :max(0,x))
            dfGV['power vaporisation eau'] = dfGV['debit eau(g/s)']*self.cst.Cl_H2O
            dfGV['power chauffe vapeur']   = (dfGV['debit eau(g/s)']*self.cst.Cp_eau_vap*(df['t_sortie_GV']-100)).apply(lambda x :max(0,x))
            dfGV['power total chauffe']   = dfGV.sum(axis=1)
            dfGV['power elec chauffe'] = df['power_gv1']+df['power_gv2']+df['power_gv3']
            dfGV['rendement GV'] = dfGV['power total chauffe']/dfGV['power elec chauffe']
            gv = dfGV['rendement GV']
            gv[dfGV['power elec chauffe']<20]=np.nan
            dfGV['rendement GV'] = gv*100
            df.columns=[k + ' : ' + l  for k,l in zip(df.columns,listTags)]
            df = pd.concat([df,dfGV],axis=1)
            if wholeDF:return df
            else :return df['rendement GV']
        else : return df

    def pertesThermiquesStack(self,timeRange_Window,fuel='N2',wholeDF=False,activePower=True,**kwargs):
        air_entreeStack = 'SEH1.HTBA_HEX_02_TT_01.HM05'
        air_balayage = 'SEH1.HPB_HEX_02_TT_02.HM05'
        fuel_entreeStack = 'SEH1.HTBF_HEX_01_TT_01.HM05'
        TstackAir = 'SEH1.STB_GFC_02_TT_01.HM05'
        TstackFuel = 'SEH1.STB_GFC_01_TT_01.HM05'
        debitAir = 'SEH01.L138_O2_FT_01.HM05'
        debitFuel = 'SEH1.L032_FUEL_FT_01.HM05'
        if activePower:p_chauffants = self.getTagsTU('STK_HER.*JTW')
        else :p_chauffants = self.getTagsTU('STK_HER.*JTVA')

        # debitFuel = 'SEH1.L034_H2_FT_01.HM05'
        listTags = [air_entreeStack,air_balayage,fuel_entreeStack,TstackAir,TstackFuel,debitAir,debitFuel]+p_chauffants
        if isinstance(timeRange_Window,list) :
            df   = self.DF_loadTimeRangeTags(timeRange_Window,listTags,**kwargs)
        else :
            df   = self.realtimeTagsDF(listTags,timeWindow=timeRange_Window,**kwargs)
        if not df.empty:
            df = df[listTags]
            df.columns = ['air_entreeStack','air_balayage','fuel_entreeStack',
                        'TstackAir','TstackFuel','debitAir(Nl/mn)','debitFuel(Nl/mn)','p_her1','p_her2','p_her3']
            dfPertes = pd.DataFrame()
            cp_fuel,M_fuel = self.dfConstants.loc['Cp_' + fuel,'value'],self.dfConstants.loc['Mmol_' + fuel,'value']
            dfPertes['surchauffe_Air']  = (df['TstackAir']-df['air_entreeStack'])*self.cst.Cp_air*self.cst.Mmol_Air*df['debitAir(Nl/mn)']/22.4/60
            dfPertes['surchauffe_Fuel'] = (df['TstackFuel']-df['fuel_entreeStack'])*cp_fuel*M_fuel*df['debitFuel(Nl/mn)']/22.4/60
            dfPertes['surchauffe_AirBalayage'] = (df['TstackAir']-df['air_entreeStack'])*self.cst.Cp_air*self.cst.Mmol_Air*df['debitAir(Nl/mn)']/22.4/60
            dfPertes['total puissance surchauffe gaz']=dfPertes.sum(axis=1)
            dfPertes['puissance four(W)'] = df['p_her1']+df['p_her2']+df['p_her3']
            dfPertes['pertes stack'] = dfPertes['puissance four(W)']-dfPertes['total puissance surchauffe gaz']

            df.columns=[k + ' : ' + l  for k,l in zip(df.columns,listTags)]
            df = pd.concat([df,dfPertes],axis=1)
            if wholeDF : return df
            else : return df['pertes stack']
        else :
            return df

    def rendement_blower(self,timeRange_Window,wholeDF=True,activePower=True,**kwargs):
        debitAir = self.getTagsTU('138.*FT')
        pressionAmont = self.getTagsTU('131.*PT')
        pressionAval = self.getTagsTU('138.*PT')
        puissanceBlowers = self.getTagsTU('blr.*02.*JT')
        t_aval = self.getTagsTU('l126')
        listTags = debitAir+pressionAmont+pressionAval+t_aval+puissanceBlowers

        if isinstance(timeRange_Window,list) :
            df   = self.DF_loadTimeRangeTags(timeRange_Window,listTags,**kwargs)
        else :
            df   = self.realtimeTagsDF(listTags,timeWindow=timeRange_Window,**kwargs)
        if not df.empty:
            df = df[listTags]
            df.columns = ['debitAir(Nl/min)','pressionAmont2a(mbarg)','pressionAmont2b(mbarg)','pressionAval(mbarg)',
                            'temperature aval','puissance blower 2a','puissance blower 2b']
            dfBlower = pd.DataFrame()
            dfBlower['debit air(Nm3/s)'] = df['debitAir(Nl/min)']/1000/60
            dfBlower['deltaP2a(Pa)'] = (df['pressionAval(mbarg)']-df['pressionAmont2a(mbarg)'])*100
            dfBlower['deltaP2b(Pa)'] = (df['pressionAval(mbarg)']-df['pressionAmont2b(mbarg)'])*100
            dfBlower['deltaP2mean(Pa)'] = (dfBlower['deltaP2a(Pa)']+dfBlower['deltaP2b(Pa)'])/2
            dfBlower['puissance hydraulique(W)'] = dfBlower['debit air(Nm3/s)']*dfBlower['deltaP2mean(Pa)']
            dfBlower['puissance electrique(W)'] = df['puissance blower 2a']+df['puissance blower 2b']
            dfBlower['rendement blower'] = dfBlower['puissance hydraulique(W)']/dfBlower['puissance electrique(W)']*100

            df.columns=[k + ' : ' + l  for k,l in zip(df.columns,listTags)]
            df = pd.concat([df,dfBlower],axis=1)
            if wholeDF : return df
            else : return df['rendement blower']
        else : return df

    def rendement_pumps(self,timeRange_Window,wholeDF=True,activePower=True,**kwargs):
        debit_eau_1  = 'SEH1.L213_H2OPa_FT_01.HM05'
        debit_eau_2  = 'SEH1.L213_H2OPb_FT_01.HM05'
        t_aval       = 'SEH1.L036_FUEL_TT_01.HM05'
        pressionAval = 'SEH1.L036_FUEL_PT_01.HM05'
        puissancePump = 'SEH0.GWPBC_PMP_01_JT_01.HE10'
        puissancePump_var = 'SEH0.GWPBC_PMP_01_JT_01.HE13'
        listTags = [debit_eau_1,debit_eau_2,t_aval,pressionAval,puissancePump,puissancePump_var]

        if isinstance(timeRange_Window,list) :
            df   = self.DF_loadTimeRangeTags(timeRange_Window,listTags,**kwargs)
        else :
            df   = self.realtimeTagsDF(listTags,timeWindow=timeRange_Window,**kwargs)
        if not df.empty:
            df = df[listTags]
            df.columns = ['debit eau1(g/min)','debit eau2(g/min)','temperature aval',
            'pressionAval(mbarg)','puissance pump(W)','puissance pump reactive (VAR)']
            dfPump = pd.DataFrame()
            dfPump['debit eau total(Nm3/s)'] = (df['debit eau1(g/min)']+df['debit eau2(g/min)'])/1000000/60
            dfPump['pression sortie(Pa)'] = (df['pressionAval(mbarg)'])*100
            dfPump['puissance hydraulique(W)'] = dfPump['debit eau total(Nm3/s)']*dfPump['pression sortie(Pa)']
            dfPump['rendement pompe'] = dfPump['puissance hydraulique(W)']/df['puissance pump(W)']*100
            dfPump['cosphiPmp'] = df['puissance pump(W)']/(df['puissance pump(W)']+df['puissance pump reactive (VAR)'])

            df.columns=[k + ' : ' + l  for k,l in zip(df.columns,listTags)]
            df = pd.concat([df,dfPump],axis=1)
            if wholeDF : return df
            else : return df['rendement blower']
        else : return df

    def cosphi(self,timeRange_Window,**kwargs):
        lreactive = self.getTagsTU('HE13')
        lapparente = self.getTagsTU('HE16')
        listTags = self.getTagsTU('HE1')
        if isinstance(timeRange_Window,list):
            df = self.DF_loadTimeRangeTags(timeRange_Window,listTags,**kwargs)
        else:
            df = self.realtimeTagsDF(listTags,timeWindow=timeRange_Window,**kwargs)
        if not df.empty:
            dfcosphi = pd.DataFrame()
            for k in lreactive : dfcosphi['cosphi' + k] = df[k[:-1]+'0']/(df[k[:-1]+'0']+df[k])
            for k in lapparente : dfcosphi['cosphi' + k] = df[k[:-1]+'0']/df[k]
        return dfcosphi

    def getModeHub(self,timeRange_Window,**kwargs):
        modeSystem = 'SEH1.Etat.HP41'
        if isinstance(timeRange_Window,list) :
            dfmodeHUB = self.DF_loadTimeRangeTags(timeRange_Window,[modeSystem],**kwargs)
        else :
            dfmodeHUB   = self.realtimeTagsDF([modeSystem],timeWindow=timeRange_Window,**kwargs)

        dfmodeHUB=dfmodeHUB.astype(int)
        dfmodeHUB.columns=['value']
        dfmodeHUB['mode hub']=dfmodeHUB.applymap(lambda x:self.enumModeHUB[x])
        return dfmodeHUB

    def fuiteAir(self,timeRange_Window,**kwargs):
        airAmont = self.getTagsTU('l138.*FT')[0]
        airAval = self.getTagsTU('l118.*FT')[0]
        Istacks = self.getTagsTU('STK.*IT.*HM05')
        Tfour = self.getTagsTU('STB_TT_02')[0]
        pressionCollecteur = self.getTagsTU('GFC_02.*PT')[0]
        pressionDiffuseur = self.getTagsTU('GFD_02.*PT')[0]

        listTags =[airAmont,airAval]+Istacks+[Tfour]+[pressionCollecteur,pressionDiffuseur]
        if isinstance(timeRange_Window,list) :
            df   = self.DF_loadTimeRangeTags(timeRange_Window,listTags,**kwargs)
            # df   = self.DF_loadTimeRangeTags(timeRange_Window,listTags,rs=rs)
        else :
            df   = self.realtimeTagsDF(listTags,timeWindow=timeRange_Window,**kwargs)

        if df.empty:
            return pd.DataFrame()
        df = df[listTags]

        # sum courant stacks
        Itotal = df[Istacks].sum(axis=1)
        # production O2
        F = self.dfConstants.loc['FAR'].value
        Po2mols = Itotal*25/(4*F) ##25 cells
        Po2Nlmin = Po2mols*22.4*60
        # fuite air
        # QairAval = df[airAval] + Po2Nlmin
        QairAval = df[airAval] - Po2Nlmin
        fuiteAir = df[airAmont]-(QairAval)
        txFuite = fuiteAir/df[airAmont]*100
        coefficientDeFuite = fuiteAir/df[pressionDiffuseur]

        dfmodeHUB=self.getModeHub(timeRange_Window,**kwargs)
        # dfmodeHUB=self.getModeHub(timeRange_Window,rs=rs)

        varUnitsCalculated = {
            'courrant stacks total':{'unit':'A','var':Itotal},
            'production O2(mol/s)':{'unit':'mol/s','var':Po2mols},
            'production O2(Nl/min)':{'unit':'Nl/min','var':Po2Nlmin},
            'flux air aval(aval + production O2)':{'unit':'Nl/min','var':QairAval},
            'fuite air':{'unit':'Nl/min','var':fuiteAir},
            'taux de fuite air':{'unit':'%','var':txFuite},
            'coefficient de fuite':{'unit':'N/min/mbar','var':coefficientDeFuite},
            'mode hub':{'unit':'mode hub','var':dfmodeHUB['value']}
        }

        dfCalculated = pd.concat([pd.DataFrame(s['var']) for s in varUnitsCalculated.values()],axis=1)
        dfCalculated.columns = list(varUnitsCalculated.keys())
        unitGroups={}
        unitGroups.update({k:v['unit'] for k,v in varUnitsCalculated.items()})

        dfFuitesAir=pd.concat([dfCalculated,df])
        unitGroups.update({t:self.getUnitofTag(t) for t in df.columns})

        templateHover1='    <b>%{y:.2f} <br>     %{x|%H:%M:%S}'
        fig = self.utils.multiUnitGraph(dfFuitesAir,unitGroups)
        fig.update_traces(hovertemplate=templateHover1)

        # update mode and hovers
        hovertemlatemode=templateHover1 + '<br>     mode:%{text}'

        fig=fig.update_traces(selector={'name':'mode hub'},hovertemplate=hovertemlatemode,text =dfmodeHUB['mode hub'],line_shape='hv')
        return fig,dfFuitesAir

    def fuitesFuel(self,timeRange_Window,**kwargs):
        '''
        Gonflage :
        - L035 ou L040 fermées et L039 fermée et L027 fermée
        - fuites fuel BF = L303 + L041 (+ Somme i x 25 / 2F)  note : normalement dans ce mode le courant est nul.
        Boucle fermée recirculation à froid (mode pile)
        - L026 et L029 fermées, L027 ouverte, L035 OU L040 fermées
        - fuites fuel BF = L303 + L041 + Somme i x 25 / 2F
        Boucle ouverte (fonctionnement électrolyse ou boucle ouverte pendant les transitions) :
        - (L035 ET L040 ouvertes) ou L026 ouverte ou L029 ouverte
        - fuite ligne fuel BO = L303 + L041 + Somme i x 25 / 2F – L025
        Fonctionnement mode gaz naturel :
        - L027 fermée, L039 ouverte
        - fuites fuel BO = (L032 – L303) x 4 + L303 + L041 + Somme i x 25 / 2F – L025
        En résumé : trois calculs possibles du débit de fuite fuel
        Le même calcul pour les cas 1 et 2 qui sont « fermés »
        Un calcul pour le mode ouvert électrolyse ou boucle ouverte pendant les transitions
        Un calcul pour le mode gaz naturel.
        '''

        vanne26 = self.getTagsTU('l026.*ECV')[0]
        vanne27 = self.getTagsTU('l027.*ECV')[0]
        vanne29 = self.getTagsTU('l029.*ECV')[0]
        vanne35 = self.getTagsTU('l035.*ECV')[0]
        vanne39 = self.getTagsTU('l039.*ECV')[0]
        vanne40 = self.getTagsTU('l040.*ECV')[0]
        vannes = [vanne26,vanne27,vanne29,vanne35,vanne39,vanne40]
        Istacks = self.getTagsTU('STK.*IT.*HM05')

        L025=self.getTagsTU('l025.*FT')[0]
        L032=self.getTagsTU('l032.*FT')[0]
        L041=self.getTagsTU('l041.*FT')[0]
        L303=self.getTagsTU('l303.*FT')[0]
        Tfour = self.getTagsTU('STB_TT_02')
        pressionStacks = self.getTagsTU('GF[CD]_02.*PT')

        debits =[L303,L041,L032,L025]
        listTags = vannes+Istacks+debits+pressionStacks+Tfour

        start = time.time()
        if isinstance(timeRange_Window,list) :
            df   = self.DF_loadTimeRangeTags(timeRange_Window,listTags,**kwargs)
        else :
            df   = self.realtimeTagsDF(listTags,timeWindow=timeRange_Window,**kwargs)
        if df.empty:
            print('no data could be loaded')
            return pd.DataFrame()

        print('loading data in {:.2f} milliseconds'.format((time.time()-start)*1000))
        #############################
        # compute Hydrogen production
        #############################
        start = time.time()

        Itotal = df[Istacks].sum(axis=1)
        F = self.dfConstants.loc['FAR'].value
        PH2mols = Itotal*25/(2*F) ##25 cells
        PH2Nlmin = PH2mols*22.4*60

        print('h2 production computed in {:.2f} milliseconds'.format((time.time()-start)*1000))
        #############################
        # dtermine mode fuel
        #############################
        start = time.time()

        # convert vannes to bool
        for v in vannes:df[v]=df[v].astype(bool)
        dfModes={}
        # Gonflage :
        # L035 ou L040 fermées et L039 fermée et L027 fermée
        dfModes['gonflage'] = (~df[vanne35] | ~df[vanne40]) & (~df[vanne39]) & (~df[vanne27])
        # fuites fuel BF = L303 + L041 (+ Somme i x 25 / 2F)  note : normalement dans ce mode le courant est nul.

        # Boucle fermée recirculation à froid (mode pile):
        # L026 et L029 fermées, L027 ouverte, L035 OU L040 fermées
        dfModes['recircuFroidPile']=(~df[vanne26]) & (~df[vanne29]) & (df[vanne27]) & (~df[vanne35]) | (~df[vanne40])
        # fuites fuel BF = L303 + L041 + Somme i x 25 / 2F
        fuitesFuelBF = df[L303] + df[L041] + PH2Nlmin

        # Boucle ouverte (fonctionnement électrolyse ou boucle ouverte pendant les transitions) :
        # (L035 ET L040 ouvertes) ou L026 ouverte ou L029 ouverte
        dfModes['bo_electrolyse']=(df[vanne35]&df[vanne40]) | (df[vanne26]) | (df[vanne29])
        # - fuites fuel BO = (L032 – L303) x 4 + L303 + L041 + Somme i x 25 / 2F – L025
        fuitesFuelBO = (df[L032] - df[L303])*4 + df[L303] + df[L041] + PH2Nlmin - df[L025]
        # Fonctionnement mode gaz naturel :
        # - L027 fermée, L039 ouverte
        dfModes['gaz_nat']=(~df[vanne27] & df[vanne39])
        # - fuites fuel BO = (L032 – L303) x 4 + L303 + L041 + Somme i x 25 / 2F – L025

        # check wether they are multiple modes or exclusive modes
        dfModeFuel= [v.apply(lambda x: k+'/' if x==True else '') for k,v in dfModes.items()]
        dfModeFuel = pd.concat(dfModeFuel,axis=1).sum(axis=1).apply(lambda x : x[:-1])
        modesFuel = {v:k for k,v in enumerate(dfModeFuel.unique())}
        modeFuelInt = dfModeFuel.apply(lambda x:modesFuel[x])

        #determine if pileBF or pileBO
        pileBF = [k for k in modesFuel.keys() if 'recircuFroidPile' in k or 'gonflage' in k]
        pileBF = dfModeFuel.apply(lambda x: True if x in pileBF else False)
        dfs=pd.concat([fuitesFuelBO,fuitesFuelBF],axis=1)
        dfs.columns=['BO','BF']
        dfs['pileBF'] = pileBF

        #get fuel fuites in either mode
        fuitesFuel =dfs.apply(lambda x: x['BO'] if x['pileBF'] else x['BF'],axis=1)

        # Vérif débitmètres ligne fuel BF = L032 FT – L303 – L025
        verifDebitmetre = df[L032]-df[L303]-df[L025]
        print('compute fuel fuites in {:.2f} milliseconds'.format((time.time()-start)*1000))

        # get mode Hub
        start = time.time()
        dfmodeHUB=self.getModeHub(timeRange_Window,**kwargs)
        print('get mode hub in {:.2f} milliseconds'.format((time.time()-start)*1000))

        # define names and scales
        varUnitsCalculated ={
            'courrant stacks total':{'unit':'A','var':Itotal},
            'production H2(mol/s)':{'unit':'mol/s','var':PH2mols},
            'production H2(Nl/min)':{'unit':'Nl/min','var':PH2Nlmin},
            'fuites fuel BF':{'unit':'Nl/min','var':fuitesFuelBF},
            'fuites fuel BO':{'unit':'Nl/min','var':fuitesFuelBO},
            'fuites fuel':{'unit':'Nl/min','var':fuitesFuel},
            'debit 32 - 303 - 25':{'unit':'Nl/min','var':verifDebitmetre},
            'pile BF':{'unit':'etat Pile BF','var':pileBF.astype(int)},
            'mode_Fuel':{'unit':'etat mode Fuel','var':modeFuelInt},
            'mode hub':{'unit':'mode hub','var':dfmodeHUB['value']}
            }

        dfCalculated = pd.concat([pd.DataFrame(s['var']) for s in varUnitsCalculated.values()],axis=1)
        dfCalculated.columns = list(varUnitsCalculated.keys())
        unitGroups={}
        unitGroups.update({k:v['unit'] for k,v in varUnitsCalculated.items()})
        dfFuitesFuel = dfCalculated

        # add vannes to make figure
        vanneTags=[k for k in df.columns if 'ECV' in k]
        dfvannes = df[vanneTags]
        # dfFuitesFuel=pd.concat([dfCalculated,dfvannes])
        # df = dfvannes
        dfFuitesFuel=pd.concat([dfCalculated,df])
        unitGroups.update({t:self.getUnitofTag(t) for t in df.columns})

        # make figure
        start = time.time()
        templateHover1='    <b>%{y:.2f} <br>     %{x|%H:%M:%S}'
        fig = self.utils.multiUnitGraph(dfFuitesFuel,unitGroups)
        fig.update_traces(hovertemplate=templateHover1)

        start = time.time()
        # update mode and hovers
        hovertemlatemode=templateHover1 + '<br>     mode:%{text}'

        fig.for_each_trace(
            lambda trace: trace.update(line_shape="hv") if trace.name in vanneTags else (),
        )
        fig=fig.update_traces(selector={'name':'mode_Fuel'},hovertemplate=hovertemlatemode,text=dfModeFuel,line_shape='hv')
        fig=fig.update_traces(selector={'name':'mode hub'},hovertemplate=hovertemlatemode,text =dfmodeHUB['mode hub'],line_shape='hv')

        print('figure computed in in {:.2f} milliseconds'.format((time.time()-start)*1000))
        return fig,dfFuitesFuel

    # ==============================================================================
    #                   plot functions
    # ==============================================================================
    def update_lineshape_fig(self,fig,lineshape='default'):
        if lineshape=='default':
            names=fig.name
            vanneTags   = [k for k in names if 'ECV' in k]
            commandTags = [k for k in names if '.HR36' in k]
            boolTags = [k for k in names if self.getUnitofTag(k) in ['ETAT','CMD','Courbe']]
            hvTags=vanneTags+commandTags+boolTags

            fig.for_each_trace(
                lambda trace: trace.update(line_shape="hv") if trace.name in hvTags else (),
            )
        else:
            fig.update_traces(line_shape=lineshape)

    def updateLayoutGraph(self,fig,ms=6):
        fig.update_yaxes(showgrid=False)
        fig.update_traces(marker_size=ms)
        fig.update_layout(height=800)
        fig.update_traces(hovertemplate='    <b>%{y:.2f} <br>     %{x|%H:%M:%S}')

    def updatecolortraces(self,fig):
        for tag in fig.data:
            colName=self.dftagColorCode.loc[tag.name,'colorName']
            colTag=self.allHEXColors.loc[colName]
            # print(tag.name,colName,colTag)
            tag.marker.color = colTag
            tag.line.color = colTag
            tag.marker.symbol = self.dftagColorCode.loc[tag.name,'symbol']
            tag.line.dash = self.dftagColorCode.loc[tag.name,'line']
        return fig

    def updatecolorAxes(self,fig):
        for ax in fig.select_yaxes():
            unit    = ax.title.text.strip()
            axColor = self.unitDefaultColors[unit][:-1]
            ax.title.font.color = axColor
            ax.tickfont.color   = axColor
            ax.gridcolor        = axColor

    def plotGraphPowerArea(self,timeRange,whichPower='HE10',expand='groups',groupnorm='',**kwargs):
        import plotly.express as px
        import plotly.graph_objects as go
        # df,dfPtotal,dicPowerGroups = self.DF_allPower(timeRange,melt=True,**kwargs)
        df,dfPtotal = self.DF_allPower(timeRange,whichPower=whichPower,**kwargs)

        if expand=='tags' :fig=px.area(df,x='timestamp',y='value',color='tag',groupnorm=groupnorm)
        elif expand=='groups' :
            fig=px.area(df,x='timestamp',y='value',color='Power group',groupnorm=groupnorm,line_group='tag')
            fig.update_layout(legend=dict(orientation="h"))
        try:
            traceP = go.Scatter(x=dfPtotal.index,y=dfPtotal.iloc[:,0],name='SEH0.JT_01.'+ whichPower+'(puissance totale)',
                mode='lines+markers',marker=dict(color='blue'))
            fig.add_trace(traceP)
        except:print('total power SEH0.JT_01.'+ whichPower +'IS EMPTY')
        fig.update_layout(yaxis_title='power in W')
        return fig

    def updateLayoutMultiUnitGraph(self,fig,sizeDots=10):
        fig.update_yaxes(showgrid=False)
        fig.update_traces(marker=dict(size=sizeDots))
        fig.update_layout(height=900)
        fig.update_traces(hovertemplate='<b>%{y:.2f}')
        return fig

    def plotMultiUnitGraph(self,timeRange,listTags=[],**kwargs):
        if not listTags : listTags=self.get_randomListTags()
        tagMapping = {t:self.getUnitofTag(t) for t in listTags}
        df  = self.DF_loadTimeRangeTags(timeRange,listTags,**kwargs)
        return self.utils.multiUnitGraph(df,tagMapping)

    def checkCondenseur(self,timeRange_Window,**kwargs):
        df = self.rendementCondenseur(timeRange_Window,wholeDF=True,**kwargs)
        dictGroups={t:v for t,v in zip(df.columns,['g/min','C','C','g/s','g/s','W','W','W','W','W'])}
        fig = self.utils.multiUnitGraph(df,dictGroups)
        fig.update_traces(marker_size=5)
        fig.update_yaxes(showgrid=False)
        fig.update_traces(hovertemplate="%{y:.2f}")
        return fig

    def checkValo(self,timeRange_Window,**kwargs):
        df = self.bilanValo(timeRange_Window,wholeDF=True,**kwargs)
        dictGroups={t:v for t,v in zip(df.columns,['kg/h','C','C','g/s','W'])}
        fig = self.utils.multiUnitGraph(df,dictGroups)
        fig.update_traces(marker_size=5)
        fig.update_yaxes(showgrid=False)
        fig.update_traces(hovertemplate="%{y:.2f}")
        return fig

    def checkRendementGV(self,timeRange_Window,subplot=False,**kwargs):
        df = self.rendement_GV(timeRange_Window,wholeDF=True,**kwargs)

        if subplot:
            dictdictGroups ={}
            dictdictGroups['tags'] = {t:v for t,v in zip(df.columns[:6],['W','W','W','C','C','g/min'])}
            dictdictGroups['calculated'] = {t:v for t,v in zip(df.columns[6:],['C','g/s','W','W','W','W','W','%'])}
            fig=utils.multiUnitGraphSubPlots(df,dictdictGroups)
        else :
            dictGroups={t:v for t,v in zip(df.columns,['g/min','W','W','W','C','C','g/s','W','W','W','W','W','%'])}
            fig = self.utils.multiUnitGraph(df,dictGroups)

        fig.update_traces(marker_size=5)
        fig.update_yaxes(showgrid=False)
        fig.update_traces(hovertemplate="%{y:.2f}")
        return fig

    def checkPertesStack(self,timeRange_Window,**kwargs):
        df = self.pertesThermiquesStack(timeRange_Window,wholeDF=True,**kwargs)
        dictGroups={t:v for t,v in zip(df.columns,['°C','°C','°C','°C','°C','Nl/mn','Nl/mn','W','W','W','W','W','W','W','W','W',])}
        fig = self.utils.multiUnitGraph(df,dictGroups)
        fig.update_traces(marker_size=5)
        fig.update_yaxes(showgrid=False)
        fig.update_traces(hovertemplate="%{y:.2f}")
        return fig

    def checkBlowers(self,timeRange_Window,**kwargs):
        df = self.rendement_blower(timeRange_Window,wholeDF=True,**kwargs)
        dictGroups={t:v for t,v in zip(df.columns,['Nl/mn','mbarg','mbarg','mbarg','°C','W','W','Nm3/s','Pa','Pa','Pa','W','W','%'])}
        fig = self.utils.multiUnitGraph(df,dictGroups)
        fig.update_traces(marker_size=5)
        fig.update_yaxes(showgrid=False)
        fig.update_traces(hovertemplate="%{y:.2f}")
        return fig

    def checkCosphi(self,timeRange_Window,**kwargs):
        df = self.cosphi(timeRange_Window,**kwargs)
        fig = px.scatter(df)
        fig.update_traces(mode='lines+markers',hovertemplate="%{y:.2f}")
        return fig

    def multiUnitGraphShades(self,df):
        tagMapping = {t:self.getUnitofTag(t) for t in df.columns}
        fig = self.utils.multiUnitGraph(df,tagMapping)
        dfGroups = self.utils.getLayoutMultiUnit(tagMapping)[1]
        listCols = dfGroups.color.unique()
        for k1,g in enumerate(listCols):
            colname = self.colorshades[k1]
            shades = self.colorPalettes[colname]['hex']
            names2change = dfGroups[dfGroups.color==g].index
            fig.update_yaxes(selector={'gridcolor':g},
                        title_font_color=colname[:-1],gridcolor=colname[:-1],tickfont_color=colname[:-1])
            shade=0
            for d in fig.data:
                if d.name in names2change:
                    d['marker']['color'] = shades[shade]
                    d['line']['color']   = shades[shade]
                    shade+=1
            fig.update_yaxes(showgrid=False)
            fig.update_xaxes(showgrid=False)

        # fig.add_layout_image(dict(source=self.imgpeintre,xref="paper",yref="paper",x=0.05,y=1,
        #                             sizex=0.9,sizey=1,sizing="stretch",opacity=0.5,layer="below"))
        # fig.update_layout(template="plotly_white")
        fig.add_layout_image(
            dict(
                source=self.sylfenlogo,
                xref="paper", yref="paper",
                x=0., y=1.02,
                sizex=0.12, sizey=0.12,
                xanchor="left", yanchor="bottom"
            )
        )
        return fig

    def multiUnitGraphSP(self,df):
        tagMapping = {t:self.getUnitofTag(t) for t in df.columns}
        # print(tagMapping)
        fig = self.utils.multiUnitGraph(df,tagMapping)
        self.updateLayoutGraph(fig)
        self.updatecolorAxes(fig)
        fig=self.updatecolortraces(fig)
        return fig

class ConfigFilesSmallPower(ConfigDashTagUnitTimestamp,SmallPowerMaster):
    # ==========================================================================
    #                       INIT FUNCTIONS
    # ==========================================================================

    def __init__(self,folderPkl=None):
        import socket
        if not folderPkl and socket.gethostname()=='dorianSylfenAsus':
            folderPkl='/home/dorian/data/sylfenData/smallPower_pkl/'
        SmallPowerMaster.__init__(self)
        ConfigDashTagUnitTimestamp.__init__(self,folderPkl,self.confFolder)
        SmallPowerMaster._load_plcfile(self)
        self.dfPLC= self.dfPLC[self.dfPLC['DATASCIENTISM']]
        self.dfPLC= self.dfPLC.set_index('TAG')
        self.legendTags = pd.read_csv(self.confFolder + 'tagLegend.csv')
        self.powerGroups = pd.read_csv(self.confFolder +'powerGroups.csv',index_col=0)
        self._buildColorCode()

    def getListTagsPower(self):
        return self.utils.flattenList([self.getTagsTU(self.powerGroups.loc[k].pattern) for k in self.powerGroups.index])

    def _categorizeTagsPerUnit(self,df):
        dfPLC1 = self.dfPLC[self.dfPLC.TAG.isin(df.columns)]
        unitGroups={}
        for u in dfPLC1.UNITE.unique():
            unitGroups[u]=list(dfPLC1[dfPLC1.UNITE==u].TAG)
        return unitGroups

    def calculatedTags(self,tags,**kwargs):
        dfs=[]
        for tag in tags:
            if re('STK_0[1-4].ET.SUM',tag):
                listTags = self.getTagsTU(tag[:-3]+'HM05')
                df = self.DF_loadTimeRangeTags(listTags=listTags,**kwargs)
                df = df.sum(axis=1)
                df.columns=[tag]
                dfs.append(df)
        return dfs

class ConfigFilesSmallPowerSpark(ConfigDashSpark,SmallPowerMaster):
    def __init__(self,sparkData,sparkConfFile,confFile=None):
        SmallPowerMaster.__init__(self)
        ConfigDashSpark.__init__(sparkData,sparkConfFile,confFile=confFile)
        self.usefulTags = pd.read_csv(self.appDir+'/confFiles/predefinedCategories.csv',index_col=0)
        self.dfPLC = self.__buildPLC()

    def __buildPLC(self):
        return self.dfPLC[self.dfPLC.DATASCIENTISM==True]

class AnalysisPerModule(ConfigFilesSmallPower):
    def __init__(self,folderPkl):
        ConfigFilesSmallPower.__init__(self,folderPkl)
        self.modules = self._loadModules()
        self.listModules = list(self.modules.keys())

    def _buildEauProcess(self):
        eauProcess={}
        eauProcess['pompes']=['PMP_04','PMP_05']
        eauProcess['TNK01'] = ['L219','L221','L200','L205','GWPBC_TNK_01']
        eauProcess['pompe purge'] = ['GWPBC_PMP_01','L202','L210']
        eauProcess['toStack'] = ['L036','L020','GFD_01']
        return eauProcess

    def _buildGV(self):
        GV = {}
        GV['temperatures GV1a'] = ['STG_01a_TT']
        GV['commande GV1a'] = ['STG_01a_HER']
        GV['commande GV1b'] = ['STG_01b_HER']
        GV['ligne gv1a'] = ['L211','L213_H2OPa']
        GV['ligne gv1b'] = ['L211','L213_H2OPb']
        GV['temperatures GV1b'] = ['STG_01b_TT']
        return GV

    def _buildValo(self):
        Valo = {}
        Valo['amont-retour'] = ['GWPBC_PMP_02','L400','L416','L413']
        Valo['echangeur 1'] = ['HPB_HEX_01','L402','L114','L117']
        Valo['condenseur 1'] = ['HPB_CND_01','L408','L404','L021','L022']
        Valo['echangeur 2'] = ['HPB_HEX_02','L404','L115','L116']
        Valo['condenseur 2'] = ['HPB_CND_02','L406','L046','L045']
        Valo['batiment'] = ['GWPBC-HEX-01','L414','L415']
        return Valo

    def _buildGroupeFroid(self):
        groupFroid = {}
        groupFroid['groupe froid'] = ['HPB_CND_03','L417','L418','L056','L057']
        return groupFroid

    def _buildBalayage(self):
        Balayage = {}
        Balayage['echangeur'] = ['HTBA_HEX_01','L133','L134','L135','HPB_RD_01']
        Balayage['stack'] = ['STB_TT_01','STB_TT_02']
        Balayage['blowers'] = ['GWPBH_BLR','L136']
        Balayage['explosimetre'] = ['SFTB_AT_01']
        return Balayage

    def _buildStackBox(self):
        stackBox = {}
        stackBox['chauffants enceinte'] = ['SEH1.STB_HER']
        stackBox['chauffants stacks'] = ['SEH1.STB_STK_0[1-4]_HER']
        stackBox['stack 1'] = ['STB_STK_01']
        stackBox['stack 2'] = ['STB_STK_02']
        stackBox['stack 3'] = ['STB_STK_03']
        stackBox['stack 4'] = ['STB_STK_04']
        stackBox['debits'] = ['STB_GFD','STB_FUEL','STB_GFC','STB_GDC']
        return stackBox

    def _loadModules(self):
        modules = {}
        modules['eau process']=self._buildEauProcess()
        modules['GV']=self._buildGV()
        modules['groupe froid']=self._buildGroupeFroid()
        modules['valo']=self._buildValo()
        modules['balayage']=self._buildBalayage()
        modules['stackbox']=self._buildStackBox()
        return modules

    def _categorizeTagsPerUnit(self,module):
        '''module : {'eauProcess','groupe froid','GV','valo'...} given by self.listModules'''
        mod=self.modules[module]
        ll = self.utils.flattenList([self.listTagsModule(mod,g)[1] for g in mod])
        dfPLC1 = self.dfPLC[self.dfPLC.TAG.isin(ll)]
        unitGroups={}
        for u in dfPLC1.UNITE.unique():
            unitGroups[u]=list(dfPLC1[dfPLC1.UNITE==u].TAG)
        return unitGroups

    # ==========================================================================
    #                     Global module functions
    # ==========================================================================

    def listTagsModule(self,module,group):
        groupList=module[group]
        lplc=pd.concat([self.getTagsTU(pat,ds=False,cols='tdu') for pat in groupList])
        lds=self.utils.flattenList([self.getTagsTU(pat,ds=True) for pat in groupList])
        return lplc,lds

    def listTagsAllModules(self,module,groups=[]):
        mod=self.modules[module]
        LPLC = {g:self.listTagsModule(mod,g)[0] for g in mod}
        LDS = {g:self.listTagsModule(mod,g)[1] for g in mod}
        return LPLC,LDS

    def getDictGroupUnit(self,module,groupsOfModule):
        dictdictGroups = {}
        allgroupsofModule = self.listTagsAllModules(module)[1]
        if not groupsOfModule:groupsOfModule=list(allgroupsofModule.keys())
        groupsOfModule={g:allgroupsofModule[g] for g in groupsOfModule}
        for group,listTags in groupsOfModule.items():
            dictdictGroups[group] = {t:self.utils.detectUnit(self.getUnitofTag(t)) + ' in ' + self.getUnitofTag(t) for t in listTags}

        listTags=self.utils.flattenList([v for v in groupsOfModule.values()])
        return dictdictGroups,listTags
    # ==========================================================================
    #                           GRAPH FUNCTIONS
    # ==========================================================================
    def figureModule(self,module,timeRange,groupsOfModule=None,axisSpace=0.04,hspace=0.02,vspace=0.1,colmap='jet',**kwargs):
        '''
        module : name of the module
        groupsOfModule : list of names of subgroups from the module
        '''
        dictdictGroups,listTags=self.getDictGroupUnit(module,groupsOfModule)
        df  = self.DF_loadTimeRangeTags(timeRange,listTags,**kwargs)
        fig = self.utils.multiUnitGraphSubPlots(df,dictdictGroups,
                        axisSpace=axisSpace,horizontal_spacing=hspace,vertical_spacing=vspace,colormap='jet',
                        subplot_titles=groupsOfModule)
        return fig

    def figureModuleUnits(self,module,timeRange,listUnits=[],grid=None,**kwargs):
        from plotly.subplots import make_subplots
        unitGroups=self._categorizeTagsPerUnit(module)
        if not listUnits: listUnits = list(unitGroups.keys())
        if not grid:grid=self.utils.optimalGrid(len(listUnits))
        fig = make_subplots(rows=grid[0], cols=grid[1],
                                vertical_spacing=0.01,horizontal_spacing=0.1,shared_xaxes=True)
        rows,cols=self.utils.rowsColsFromGrid(len(listUnits),grid)
        for k,r,c in zip(listUnits,rows,cols):
            print(k)
            listTags = unitGroups[k]
            df = self.DF_loadTimeRangeTags(timeRange,listTags,**kwargs)
            df=df.ffill().bfill()
            for l in df.columns:
                fig.add_scatter(y=df[l],x=df.index, mode="lines",
                                name=l, row=r, col=c)
            fig.update_yaxes(title_text=self.utils.detectUnit(k) + ' ( '+ k + ' ) ', row=r, col=c)
            # fig.update_yaxes(color='#FF0000')

        fig.update_xaxes(matches='x')
        fig.update_traces(hovertemplate='<b>%{y:.2f}',)
        fig.update_layout(title={"text": module})
        return fig

    def updateFigureModule(self,fig,module,groupsOfModule,hg,hs,vs,axSP,lgd=False):
        self.utils.printListArgs(module,groupsOfModule,hg,hs,vs,axSP)
        dictdictGroups = self.getDictGroupUnit(module,groupsOfModule)[0]
        figLayout = self.utils.getLayoutMultiUnitSubPlots(dictdictGroups,axisSpace=axSP,
                                                        horizontal_spacing=hs,vertical_spacing=vs)
        fig.layout = figLayout[0].layout
        fig.update_traces(marker=dict(size=5))
        fig.update_traces(hovertemplate='<b>%{y:.2f}')
        fig.update_yaxes(showgrid=False)
        fig.update_layout(height=hg)
        fig.update_layout(showlegend=lgd)
        fig.update_xaxes(matches='x')

        return fig

    def plotQuick(self,df,duration='short',title='',form='df'):
        df=df.ffill().bfill()
        if form=='step': plt.step(x=df.index,y=df.iloc[:,0],)
        if form=='multi': mpl.multiYmpl(df)
        if form=='df': df.plot(colormap='jet')
        datenums=md.date2num(df.index)
        if duration=='short': xfmt = md.DateFormatter('%H:%M')
        else: xfmt = md.DateFormatter('%b-%d')
        ax=plt.gca()
        plt.xticks( rotation=25 )
        # ax.xaxis.set_major_formatter(xfmt)
        # ax.set_ylabel('timestamp')
        mpl.plt.title(title)

class ConfigFilesSmallPower_RealTime(ConfigDashRealTime,SmallPowerMaster):
    # ==========================================================================
    #                       INIT FUNCTIONS
    # ==========================================================================

    def __init__(self,connParameters=None):
        if not connParameters : connParameters ={
            'host'     : "localhost",
            'port'     : "5432",
            'dbname'   : "template1",
            'user'     : "marcPotron",
            'password' : "test"
        }
        SmallPowerMaster.__init__(self)
        ConfigDashRealTime.__init__(self,self.confFolder,connParameters)
        SmallPowerMaster._load_plcfile(self)
        self.dfPLC= self.dfPLC[self.dfPLC['DATASCIENTISM']]
        self.dfPLC= self.dfPLC.set_index('TAG')
        self.legendTags = pd.read_csv(self.confFolder + 'tagLegend.csv')
        self.powerGroups = pd.read_csv(self.confFolder +'powerGroups.csv',index_col=0)
        self._buildColorCode()


    def calculatedTags(self,tags,**kwargs):
        dfs=[]
        for tag in tags:
            if len(re.findall('STK_0[1-4].ET.SUM',tag))>0:
                listTags = self.getTagsTU(tag[:-4]+'.*HM05')
                df = self.realtimeTagsDF(tags=listTags,**kwargs)
                # df = self.realtimeTagsDF(tags=listTags,timeWindow=tw)
                dfs.append(pd.DataFrame(df.sum(axis=1),columns=[tag]))
        df = pd.concat(dfs)
        return df
