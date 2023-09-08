'''
__MAYAPY__
__file__
'''

import maya.standalone
maya.standalone.initialize()

import os
import re
import sys

import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as api
import maya.OpenMayaUI as OpenMayaUI

# imports the module from the given path
import importlib
mk = importlib.machinery.SourceFileLoader("maya_kit", __MODULE__).load_module()

cmds.loadPlugin("gameFbxExporter.mll")
maya_file = __MAYAFILE__
cmds.file(maya_file, o=True, f=True, executeScriptNodes=False)

maya_file_name, _ = os.path.splitext(os.path.basename(maya_file))
export_dir = os.path.join(os.path.dirname(maya_file), f"output.{maya_file_name}")  # cmds.fileDialog2(dialogStyle=2, fileMode=2)
if not os.path.isdir(export_dir):
    os.mkdir(export_dir)

look_in_group = '|Group|Geometry|geo|Skin'  # TODO: check namespace
pattern = r'(?P<CH>\w+)_(?P<SkinVersion>\w+)_(?P<Rarity>\w+)_(?P<SkinName>\w+)_(?P<PartName>\w+)'
default_export = ["DeformationSystem"]  # TODO: check namespace
mesh_transform = mk.get_transform_by_shape_type()
exported = []
for t in sorted(mesh_transform):
    if t.startswith(look_in_group):
        input_string = t.split('|')[-1]
        match = re.match(pattern, input_string)
        if match:
            match = match.groupdict()
            export_name = '{}{}{}.fbx'.format(match["PartName"], match["Rarity"], match["SkinName"])
            export_path = os.path.join(export_dir, export_name)
            to_export = default_export.copy()
            to_export.append(t)
            print('PROGRESS:Exporting', export_path)
            mk.export_fbx(export_path, to_export)
            exported.append(export_path)
            print('Exported', export_path)
        # if len(exported) >=5:
        #     break
print('Finished exporting. Total file: ', len(exported))
for f in sorted(exported):
    print('PROGRESS:Cleaning', f)
    mk.cleanup_fbx(f)
    print('cleaned', f)


