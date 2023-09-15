'''
__MAYAPY__
__file__
'''

import maya.standalone
maya.standalone.initialize()

# imports the module from the given path
import importlib
module_path = __MODULE__
mk = importlib.machinery.SourceFileLoader("maya_kit", module_path).load_module()
mk.maya_export_skel(__INPUTFILE__)
