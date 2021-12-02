#%% Load modules...
import clr, sys, os

foldername = os.path.join(os.path.dirname(os.path.abspath(__file__)),'Resources')
sys.path.append(foldername)
simba_dll_filepath = os.path.join(foldername,'Simba.Data.dll')
clr.AddReference(simba_dll_filepath)

from Simba.Data.Repository import ProjectRepository
from Simba.Data import License, Design, Circuit, DesignExamples, ACSweep
from Simba.Data.Thermal import ThermalData,IV_T,EI_VT
import Simba.Data
Simba.Data.FunctionsAssemblyResolver.RedirectAssembly()
Simba.Data.DoubleArrayPythonEncoder.Register()
Simba.Data.Double2DArrayPythonEncoder.Register()
Simba.Data.EnumPythonEncoder.Register()
Simba.Data.ParameterToPythonEncoder.Register()

Simba.Data.PythonToParameterDecoder.Register()

if os.environ.get('SIMBA_DEPLOYMENT_KEY') is not None:
    License.Activate(os.environ.get('SIMBA_DEPLOYMENT_KEY'))