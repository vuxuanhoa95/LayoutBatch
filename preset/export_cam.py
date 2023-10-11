'''
__MAYAPY__
__file__
'''

import maya.standalone
maya.standalone.initialize()

import maya.cmds as cmds
import maya.mel as mel
import os

# imports the module from the given path
import importlib
module_path = __MODULE__
mk = importlib.machinery.SourceFileLoader("maya_kit", module_path).load_module()

EXPORT_DIR = r"\\vietsap002\projects\SXC\09_Share\Hoa\testExport"

def maya_export_cam(maya_file, cleanup=False):
    cmds.loadPlugin("gameFbxExporter.mll")
    mel.eval('setUpAxis "z";')

    cmds.file(maya_file, o=True, f=True)
    maya_file_name, _ = os.path.splitext(os.path.basename(maya_file))
    export_dir = EXPORT_DIR

    if not os.path.isdir(export_dir):
        os.mkdir(export_dir)

    shot = cmds.ls(type="shot")[0]
    export_name = cmds.shot(shot, q=True, sn=True)
    export_path = os.path.join(export_dir, '{}.fbx'.format(export_name))

    cmds.camera()
    default_export = cmds.ls("*:cam")
    camera, cameraShape = default_export[0], default_export[0]+"Shape"
    cam_trans, cam_shape = cmds.camera()
    cmds.parentConstraint(camera, cam_trans)
    attr = ["focalLength", "horizontalFilmAperture", "verticalFilmAperture", "fStop", "focusDistance"]
    for a in attr:
        cmds.connectAttr("{}.{}".format(cameraShape, a), "{}.{}".format(cam_shape, a), f=True)

    export_nodes = [cam_trans, cam_shape]
    mk.export_fbx(export_path, export_nodes, anim=True)
    
    # clean up fbx
    if cleanup:
        mk.cleanup_fbx(export_path)


file = __INPUTFILE__
if file.endswith(".txt"):
    files = []
    with open(file, "r") as f:
        for line in f.readlines():
            line = line.strip()
            if line.endswith(".ma") or line.endswith(".mb"):
                files.append(line)

    print('PROGRESSCOUNT:{}\n'.format(len(files)), flush=True)
    for i, f in enumerate(files):
        maya_export_cam(f)
        print('PROGRESS:{}:Exporting:{}\n'.format(i, f), flush=True)

elif file.endswith(".ma") or file.endswith(".mb"):
    maya_export_cam(file)
