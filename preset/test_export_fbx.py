import maya.standalone
maya.standalone.initialize()

import maya.cmds as cmds

import os
import re
import sys


script_dir = os.path.dirname(__file__)
if not script_dir in sys.path:
    sys.path.append(script_dir)
    

import maya_kit as mk

cmds.loadPlugin("gameFbxExporter.mll")
cmds.file("C:/Dev/MayaExportFBX/Base_Rig_Latest/Base_Rig_Latest.mb", o=True, f=True, executeScriptNodes=False)

export_dir = 'C:/Dev/MayaExportFBX/Base_Rig_Latest/output'  # cmds.fileDialog2(dialogStyle=2, fileMode=2)
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
            mk.export_fbx(export_path, to_export)
            exported.append(export_path)
            print('Exported', export_path)
        # if len(exported) >=5:
        #     break
print('Finished exporting. Total file: ', len(exported))
for f in sorted(exported):
    mk.cleanup_fbx(f)
    print('cleaned', f)
