'''
__MAYAPY__
__file__
__INPUTFILE__
'''

import maya.standalone
maya.standalone.initialize()

import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm
import os
import sys
import json

import re

EXPORT_DIR = r"\\vietsap002\projects\HCE\09_Share\Hoa\testmocap"
SELECTION_SETS = ["ControlSet"]
NAMESPACES = []


def select_by_json_set(targets, json_path):
    # get control list from json
    control_list = []
    selection_set = json_path.split('\\')[-2]
    with open(json_path, mode='r') as json_file:
        json_object = json.load(json_file)
        control_list = json_object['objects'].keys()

    # get target namespace
    target_namespaces = []
    for s in targets:
        # get name space from selection
        try:
            ns = s.rpartition(":")[0]
        except:
            pass
        else:
            if ns not in target_namespaces:
                target_namespaces.append(ns)

    # select by namespace
    cmds.select(clear=True)
    for ns in target_namespaces:
        for c in control_list:
            c = pm.NameParser(c).swapNamespace(ns)
            try:
                cmds.select(c, add=True)
            except:
                pass
        
        string_notify = '<hl>{}</hl> <hl>{}</hl> selected from <hl>{}</hl>'.format(ns, len(cmds.ls(sl=True)), selection_set)
        cmds.inViewMessage(amg=string_notify, pos='topLeft', fade=True)

    return cmds.ls(sl=True)


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

def export_anim_source(maya_file, export_dir, cleanup=True):
    cmds.file(maya_file, o=True, f=True)
    maya_file_name, _ = os.path.splitext(os.path.basename(maya_file))

    # try create folder by shot
    # scene_name = os.path.basename(cmds.file(q=True, sn=True))
    result = re.search(r'shot_(?P<shot>.+?)_', maya_file_name)
    if result:
        export_dir = os.path.join(export_dir, result.group('shot'))
    # else:
    #     # export_dir = os.path.join(EXPORT_DIR, maya_file_name)
    #     export_dir = os.path.join(export_dir)
        
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
                export_path = os.path.join(export_dir, "{}__{}.mb".format(ns, result.group('shot')))
            else:
                export_path = os.path.join(export_dir, "{}__{}.mb".format(ns, maya_file_name))
            anim_sources.append((a, export_path.replace("\\", "/")))

    ctrl_set = select_by_json_set(cmds.ls("*:Controls"), r"\\vietsap002\projects\HCE\data\review\libanim\Layout\MasterChief_Full.set\set.json")
    if ctrl_set:
        ns = ctrl_set[0].rpartition(":")[0]
        a = create_anim_source(ctrl_set, anim_source_name="{}".format(ns), custom_namespace=ns)
        trim_anim_source(a, get_frame_range())
        if result:
            export_path = os.path.join(export_dir, "{}__{}.mb".format(ns, result.group('shot')))
        else:
            export_path = os.path.join(export_dir, "{}__{}.mb".format(ns, maya_file_name))
        anim_sources.append((a, export_path.replace("\\", "/")))
    
    # export anim sources
    if anim_sources:
        print(anim_sources)
        if not os.path.isdir(export_dir):
            os.makedirs(export_dir)
            
    for a, e in anim_sources:
        cmds.timeEditorAnimSource(a, e=True, export=e)
        print("exported", e)

    if cleanup:
        for a, e in anim_sources:
            cleanup_file(e)
            print("cleaned:", e)

def cleanup_file(file_path):
    cmds.file(file_path, o=True, f=True, executeScriptNodes=False)

    # clean up namespace
    for i in cmds.namespaceInfo(lon=True):
        if i in ['UI', 'shared']:
            continue
        child_namespace = cmds.namespaceInfo(i, lon=True, r=True)
        namespaces_to_delete = [i]
        if child_namespace:
            namespaces_to_delete = child_namespace[::-1] + namespaces_to_delete

        for ns in namespaces_to_delete:
            try:
                cmds.namespace(rm=ns, mergeNamespaceWithParent=True)
            except:
                pass
    print('cleaned: namespace')

    cmds.file(save=True)
        
if __name__ == "__main__":
    file = sys.argv[1]
    file_name, file_ext = os.path.splitext(os.path.basename(file))
    if file_ext == ".txt":
        files = []
        with open(file, "r") as f:
            for line in f.readlines():
                line = line.strip().strip('"')
                if line.endswith(".ma") or line.endswith(".mb"):
                    files.append(line)

        print('PROGRESSCOUNT:{}\n'.format(len(files)), flush=True)
        for i, f in enumerate(files):
            export_anim_source(f, os.path.join(EXPORT_DIR, file_name))
            print('PROGRESS:{}:Exporting:{}\n'.format(i, f), flush=True)

    elif file_ext in [".ma", ".mb"]:
        export_anim_source(file, os.path.join(EXPORT_DIR, file_name))

