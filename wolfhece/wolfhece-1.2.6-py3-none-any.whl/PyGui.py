import wx
from os import path
import wx

if not '_' in globals()['__builtins__']: #Test de la présence de la fonction de traduction i18n "gettext" et définition le cas échéant pour ne pas créer d'erreur d'exécution
    import gettext
    _=gettext.gettext

from .PyDraw import WolfMapViewer,imagetexture
from .PyParams import Wolf_Param
from .PyVertexvectors import Grid
from .RatingCurve import SPWMIGaugingStations,SPWDCENNGaugingStations
from .PyGuiHydrology import GuiHydrology

class GenMapManager(wx.Frame):
    allviews:WolfMapViewer

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

    def add_grid(self):
        mygrid=Grid(1000.)
        self.allviews.add_object('vector',newobj=mygrid,ToCheck=False,id='Grid')

    def add_WMS(self):
        xmin=0
        xmax=0
        ymin=0
        ymax=0
        orthos={'IMAGERIE':{'1971':'ORTHO_1971','1994-2000':'ORTHO_1994_2000',
                        '2006-2007':'ORTHO_2006_2007',
                        '2009-2010':'ORTHO_2009_2010',
                        '2012-2013':'ORTHO_2012_2013',
                        '2015':'ORTHO_2015','2016':'ORTHO_2016','2017':'ORTHO_2017',
                        '2018':'ORTHO_2018','2019':'ORTHO_2019','2020':'ORTHO_2020',
                        '2021':'ORTHO_2021'}}
        for idx,(k,item) in enumerate(orthos.items()):
            for kdx,(m,subitem) in enumerate(item.items()):
                self.allviews.add_object(which='wmsback',
                            newobj=imagetexture('PPNC',m,k,subitem,
                            self.allviews,xmin,xmax,ymin,ymax,-99999,1024),
                            ToCheck=False,id='PPNC '+m)
        self.allviews.add_object(which='wmsback',
                    newobj=imagetexture('PPNC','Orthos France','OI.OrthoimageCoverage.HR','',
                    self.allviews,xmin,xmax,ymin,ymax,-99999,1024,France=True,epsg='EPSG:27563'),
                    ToCheck=False,id='Orthos France')

        forelist={'EAU':{'Aqualim':'RES_LIMNI_DGARNE','Alea':'ALEA_INOND','Lidaxes':'LIDAXES'},
                    'LIMITES':{'Secteurs Statistiques':'LIMITES_QS_STATBEL'},
                    'INSPIRE':{'Limites administratives':'AU_wms'},
                    'PLAN_REGLEMENT':{'Plan Percellaire':'CADMAP_2021_PARCELLES'}}
        
        for idx,(k,item) in enumerate(forelist.items()):
            for kdx,(m,subitem) in enumerate(item.items()):
                self.allviews.add_object(which='wmsfore',
                            newobj=imagetexture('PPNC',m,k,subitem,
                            self.allviews,xmin,xmax,ymin,ymax,-99999,1024),
                            ToCheck=False,id=m)        

class MapManager(GenMapManager):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.allviews=WolfMapViewer(None,'All data')
        self.add_grid()
        self.add_WMS()

class HydrologyModel(GenMapManager):

    mydir:str
    mydircharact:str
    mydirwhole:str
    files_hydrology_array:dict
    files_hydrology_vectors:dict
    mainparams:Wolf_Param
    basinparams:Wolf_Param
    SPWstations:SPWMIGaugingStations
    DCENNstations:SPWDCENNGaugingStations

    def __init__(self,dir:str='', *args, **kw):
        super(HydrologyModel, self).__init__(*args, **kw)

        self.SPWstations=SPWMIGaugingStations()
        self.DCENNstations=SPWDCENNGaugingStations()

        if dir=='':
            idir=wx.DirDialog(None,"Choose Directory")
            if idir.ShowModal() == wx.ID_CANCEL:
                return
            self.mydir =idir.GetPath()
        else:
            self.mydir=path.normpath(dir)
            
        self.mydircharact=self.mydir+'\\Characteristic_maps\\Drainage_basin'
        self.mydirwhole=self.mydir+'\\Whole_basin\\'

        self.allviews=GuiHydrology(self,'Model : '+self.mydir)

        self.files_hydrology_array={'Characteristic_maps':[
            ('.b','Raw elevation [m]'),
            ('corr.b','Corrected elevation [m]'),
            #('diff.b','Corrections (corr-raw) [m]'),
            ('.nap','Mask [-]'),
            ('.sub','SubBasin index [-]'),
            ('.cnv','Accumulation [km²]'),
            ('.time','Total time [s]'),
            ('.coeff','RunOff coeff [-]'),
            ('.slope','Slope [-]'),
            ('.reachs','Reach index [-]'),
            ('.strahler','Strahler index [-]'),
            ('.reachlevel','Reach accumulation [-]'),
            ('.landuse1','Woodlands [m²]'),
            ('.landuse2','Pastures [m²]'),
            ('.landuse3','Cultivated [m²]'),
            ('.landuse4','Pavements [m²]'),
            ('.landuse5','Water [m²]'),
            ('.landuse6','River [m²]'),
            ('.landuse_limited_area','LandUse Verif'),
            ('.principal_landuse_cropped','Principal landuse [-]'),
            ('_encode.sub','Coded index SubB [-]')]}

        self.files_hydrology_vectors={'Characteristic_maps':[('.delimit.vec','Watershed')],
                                'Whole_basin':[('Rain_basin_geom.vec','Rain geom'),
                                                ('Evap_basin_geom.vec','Evapotranspiration geom')]}   

        for curfile in self.files_hydrology_array['Characteristic_maps']:
            curext=curfile[0]
            curidx=curfile[1]
            self.allviews.add_object(which='array',filename=self.mydircharact+curext,id=curidx,ToCheck=False)

        for curfile in self.files_hydrology_vectors['Characteristic_maps']:
            curext=curfile[0]
            curidx=curfile[1]
            self.allviews.add_object(which='vector',filename=self.mydircharact+curext,id=curidx,ToCheck=False)
        for curfile in self.files_hydrology_vectors['Whole_basin']:
            curext=curfile[0]
            curidx=curfile[1]
            if path.exists(self.mydirwhole+curext):
                self.allviews.add_object(which='vector',filename=self.mydirwhole+curext,id=curidx,ToCheck=False)
        
        self.allviews.add_object(which='other',newobj=self.SPWstations,ToCheck=False,id='SPW-MI stations')
        self.allviews.add_object(which='other',newobj=self.DCENNstations,ToCheck=False,id='SPW-DCENN stations')

        self.add_grid()
        self.add_WMS()

        self.allviews.findminmax(True)        
        self.allviews.Autoscale(False)

        #Fichiers de paramètres
        self.mainparams=Wolf_Param(self.allviews,filename=self.mydir+'\\Main_model.param',title="Model parameters")
        self.basinparams=Wolf_Param(self.allviews,filename=self.mydircharact+'.param',title="Basin parameters")
        self.mainparams.Hide()
        self.basinparams.Hide() 



