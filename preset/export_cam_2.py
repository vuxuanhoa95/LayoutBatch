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

EXPORT_DIR = r"\\vietsap002\projects\SXC\09_Share\Hoa\testExport"

def maya_export_cam(maya_file, cleanup=False):
    cmds.loadPlugin("gameFbxExporter.mll")
    mel.eval('setUpAxis "z";')

    cmds.file(maya_file, o=True, f=True)
    maya_file_name, _ = os.path.splitext(os.path.basename(maya_file))

    shot = cmds.ls(type="shot")[0]
    export_name = cmds.shot(shot, q=True, sn=True)

    export_dir = os.path.join(EXPORT_DIR, export_name)
    if not os.path.isdir(export_dir):
        os.mkdir(export_dir)

    export_path = os.path.join(export_dir, '{}.fbx'.format(export_name))

    # cmds.camera()
    # default_export = cmds.ls("*:cam")
    # camera, cameraShape = default_export[0], default_export[0]+"Shape"
    # cam_trans, cam_shape = cmds.camera()
    # cmds.parentConstraint(camera, cam_trans)
    # attr = ["focalLength", "horizontalFilmAperture", "verticalFilmAperture", "fStop", "focusDistance"]
    # for a in attr:
    #     cmds.connectAttr("{}.{}".format(cameraShape, a), "{}.{}".format(cam_shape, a), f=True)

    # export_nodes = [cam_trans, cam_shape]
    # print(export_nodes, export_path)
    
    # mk.export_fbx(export_path, export_nodes, anim=True)
    # export_paths = []
    # export_paths.append(export_path)

    export_paths = []
    export_nodes = cmds.ls("book_wendigo*:book_jnt", "*edside*able*:root_jnt", "*:cam")
    for i in export_nodes:
        try:
            cmds.parent(i, w=True)
        except:
            pass
        if i.endswith('cam'):
            n = 'AS_cam_{}.fbx'.format(shot)
        else:
            n = 'AS_{}_{}.fbx'.format(i.partition(":")[0], shot).replace('_rig', '')
        p = os.path.join(export_dir, n)
        print(i, p)
        mk.export_fbx(p, [i], anim=True)
        export_paths.append(p)
    
    # clean up fbx
    if cleanup:
        for p in export_paths:
            mk.cleanup_fbx(p)

if __name__ == "__main__":
    file = sys.argv[1]
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
        maya_export_cam(file, cleanup=False)
