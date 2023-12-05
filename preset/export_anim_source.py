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

import re

EXPORT_DIR = r"\\vietsap002\projects\HCE\09_Share\Hoa\testExport"
SELECTION_SETS = ["ControlSet", "FacialControls"]
NAMESPACES = []


def select_ctrl_set(ns):
    cmds.select(clear=True)
    for s in SELECTION_SETS:
        s = "{}:{}".format(ns, s)
        if cmds.objExists(s):
            cmds.select(s, add=True)
    return cmds.ls(sl=True)


def get_frame_range():
    startframe = cmds.playbackOptions(q=True, minTime=True)
    endframe = cmds.playbackOptions(q=True, maxTime=True)
    for s in cmds.ls(type="shot"):
        if int(cmds.shot(s, q=True, sst=True)) == 1:
            startframe = 1
            endframe = int(cmds.shot(s, q=True, set=True))
    return [startframe, endframe]
    

def create_anim_source(nodes, anim_source_name='AnimSource#', custom_namespace=None):
    kwargs = {
        "type": [
            "animCurveTL",
            "animCurveTA",
            "animCurveTT",
            "animCurveTU"
        ],
        "addRelatedKG": True,
        "recursively": True,
        "includeRoot": True,
        "rsa":  False,
        "aso": True
    }
    if custom_namespace:
        cmds.namespace(set=custom_namespace)
        
    cmds.select(nodes)
    result = cmds.timeEditorAnimSource(anim_source_name, **kwargs)
    
    if custom_namespace:
        cmds.namespace(set=':')
        
    return result
    
def trim_anim_source(anim_source, frame_range):
    if not len(frame_range) == 2:
        return
        
    frame_in, frame_out = frame_range
    start_frame, duration = cmds.timeEditorAnimSource(anim_source, q=True, ct=True)
    start_frame = int(start_frame)
    duration = int(duration)
    end_frame = start_frame + duration
    
    if frame_in == start_frame and frame_out == end_frame:
        cmds.setAttr(anim_source + '.duration', duration+1)
        
    else:
        cmds.setAttr(anim_source + '.start', frame_in)
        cmds.setAttr(anim_source + '.duration', frame_out-frame_in+1)
        anim_curves = cmds.listConnections(anim_source, type='animCurve')
        if anim_curves:
            for a in anim_curves:
                try:
                    cmds.setKeyframe(a, i=True, time=[frame_in, frame_out])
                    cmds.cutKey(a, time=(-999999999, frame_in - 1))
                    cmds.cutKey(a, time=(frame_out + 1, 999999999))
                except:
                    pass
    return anim_source

def export_anim_source(maya_file, cleanup=False):
    cmds.file(maya_file, o=True, f=True)
    maya_file_name, _ = os.path.splitext(os.path.basename(maya_file))

    # try create folder by shot
    # scene_name = os.path.basename(cmds.file(q=True, sn=True))
    result = re.search(r'shot_(?P<shot>.+?)_', maya_file_name)
    if result:
        export_dir = os.path.join(EXPORT_DIR, result.group('shot'))
    else:
        export_dir = os.path.join(EXPORT_DIR, maya_file_name)
        
    # get control set based on namespace
    namespaces = NAMESPACES.copy()
    if not namespaces:
        namespaces = [n for n in cmds.namespaceInfo(lon=True, r=True) if n not in ['UI','shared']]
    
    # populate anim sources
    anim_sources = []
    for ns in namespaces:
        ctrl_set = select_ctrl_set(ns)
        if ctrl_set:
            a = create_anim_source(ctrl_set, anim_source_name="{}".format(ns), custom_namespace=ns)
            trim_anim_source(a, get_frame_range())
            if result:
                export_path = os.path.join(export_dir, "{}_{}.mb".format(ns, result.group('shot')))
            else:
                export_path = os.path.join(export_dir, "{}.mb".format(ns))
            anim_sources.append((a, export_path))
    
    # export anim sources
    if anim_sources:
        print(anim_sources)
        if not os.path.isdir(export_dir):
            os.makedirs(export_dir)
            
    for a, e in anim_sources:
        cmds.timeEditorAnimSource(a, e=True, export=e.replace("\\", "/"))
        print("exported", e)
        
if __name__ == "__main__":
    file = sys.argv[1]
    file_name, file_ext = os.path.splitext(os.path.basename(file))
    if file_ext == ".txt":
        files = []
        with open(file, "r") as f:
            for line in f.readlines():
                line = line.strip()
                if line.endswith(".ma") or line.endswith(".mb"):
                    files.append(line)

        print('PROGRESSCOUNT:{}\n'.format(len(files)), flush=True)
        for i, f in enumerate(files):
            export_anim_source(f)
            print('PROGRESS:{}:Exporting:{}\n'.format(i, f), flush=True)

    elif file_ext in [".ma", ".mb"]:
        export_anim_source(file)

