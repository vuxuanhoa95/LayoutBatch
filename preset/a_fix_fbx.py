'''
__MAYAPY__
__file__
__INPUTFILE__
'''

import maya.standalone
maya.standalone.initialize()

import maya.cmds as cmds
import maya.mel as mel
import os
import sys

# imports the module from the given path
import importlib
module_path = __MODULE__
mk = importlib.machinery.SourceFileLoader("maya_kit", module_path).load_module()


def export_fbx(output, nodes=None, start_frame=None, end_frame=None, anim=False):
    origRange = get_frame_range()
    if not start_frame or not end_frame:
        start_frame, end_frame = get_frame_range()
    
    set_frame_range(start_frame, end_frame)

    mel.eval("FBXResetExport")

    # format options
    mel.eval("FBXExportFileVersion -v FBX201800;")
    mel.eval("FBXExportUpAxis z;")
    # mel.eval("FBXExportInAscii -v 1;")
    # mel.eval('FBXProperty "Export|AdvOptGrp|UnitsGrp|UnitsSelector" -v Centimeters;')
    # mel.eval('FBXProperty "Export|AdvOptGrp|UnitsGrp|DynamicScaleConversion" -v 1;')

    # modeling options
    mel.eval("FBXExportSmoothingGroups -v 1;")
    mel.eval("FBXExportSkins -v 1")
    mel.eval("FBXExportShapes -v 1")
    
    # other options
    mel.eval("FBXExportConstraints -v 0;")
    mel.eval("FBXExportEmbeddedTextures -v 0;")
    mel.eval("FBXExportCameras -v 1;")
    mel.eval("FBXExportInputConnections -v 0;")

    if anim:
        mel.eval('FBXProperty "Export|IncludeGrp|Animation" -v 1;')
        mel.eval("FBXExportBakeComplexAnimation -v 1;")
        mel.eval("FBXExportBakeComplexStart -v {};".format(start_frame))
        mel.eval("FBXExportBakeComplexEnd -v {};".format(end_frame))
        mel.eval("FBXExportBakeResampleAnimation -v 1;")
        mel.eval("FBXExportBakeComplexStep -v 1;")
        mel.eval("FBXExportQuaternion -v resample;")
        mel.eval("FBXExportApplyConstantKeyReducer -v 0;")

    if nodes is None:
        mel.eval('FBXExport -f "{}"'.format(output).replace("\\", "\\\\"))

    else:
        cmds.select(nodes)
        mel.eval('FBXExport -f "{}" -s'.format(output).replace("\\", "\\\\"))

    set_frame_range(origRange[0], origRange[1])
    
def set_frame_range(startFrame, endFrame):
    cmds.playbackOptions(
        animationStartTime=startFrame,
        animationEndTime=endFrame,
        minTime=startFrame,
        maxTime=endFrame,
    )
    cmds.currentTime(startFrame, edit=True)


def get_frame_range():
    startframe = cmds.playbackOptions(q=True, minTime=True)
    endframe = cmds.playbackOptions(q=True, maxTime=True)
    return [startframe, endframe]

def reset_bone(bone):
    cmds.setAttr(f"{bone}.translate", 0, 0, 0, type="double3")
    cmds.setAttr(f"{bone}.rotate", 0, 0, 0, type="double3")
    cmds.setAttr(f"{bone}.scale", 1, 1, 1, type="double3")
    cmds.setAttr(f"{bone}.jointOrient", 0, 0, 0, type="double3")
    cmds.setAttr(f"{bone}.segmentScaleCompensate", 0)

def fix_fbx(maya_file):
    cmds.loadPlugin("gameFbxExporter.mll")
    print("Fixing", maya_file)
    mel.eval('setUpAxis "z";')
    cmds.file(maya_file, o=True, f=True)

    root = cmds.ls("*:root") or cmds.ls("*root")
    root = root[0]
    map = {}
    for j in cmds.ls(type="joint"):
        loc = cmds.spaceLocator(n=f"{j}_loc")[0]
        cmds.parentConstraint(j, loc)
        map[j] = loc

    cmds.select(list(map.values()), r=True)
    mel.eval("BakeSimulation;")
    cmds.delete(all=True, constraints=True)

    reset_bone(root)
    for j, loc in map.items():
        if j != root:
            reset_bone(j)
            cmds.parentConstraint(loc, j)
        else:
            cmds.parentConstraint(loc, j, mo=True)
            
    export_fbx(maya_file, cmds.ls(type="joint"), anim=True)

if __name__ == "__main__":
    file = sys.argv[1]
    if file.endswith(".txt"):
        files = []
        with open(file, "r") as f:
            for line in f.readlines():
                line = line.strip()
                line = line.strip('"')
                if line.endswith(".ma") or line.endswith(".mb") or line.endswith(".fbx"):
                    files.append(line)

        print('PROGRESSCOUNT:{}\n'.format(len(files)), flush=True)
        for i, f in enumerate(files):
            fix_fbx(f)
            print('PROGRESS:{}:Exporting:{}\n'.format(i, f), flush=True)

    elif file.endswith(".ma") or file.endswith(".mb"):
        fix_fbx(file)
