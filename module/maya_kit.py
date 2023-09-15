import os
import re
import sys

import maya.cmds as cmds
import maya.mel as mel


def export_fbx(output, nodes=None, start_frame=None, end_frame=None, anim=False):
    origRange = get_frame_range()
    if not start_frame or not end_frame:
        start_frame, end_frame = get_frame_range()
    
    set_frame_range(start_frame, end_frame)

    mel.eval("FBXResetExport")
    mel.eval("FBXExportFileVersion -v FBX202000;")
    # mel.eval("FBXExportUpAxis z;")
    # mel.eval("FBXExportInAscii -v 1;")
    mel.eval("FBXExportQuaternion -v resample;")
    mel.eval("FBXExportApplyConstantKeyReducer -v 0;")
    mel.eval('FBXProperty "Export|AdvOptGrp|UnitsGrp|UnitsSelector" -v Centimeters;')
    mel.eval('FBXProperty "Export|AdvOptGrp|UnitsGrp|DynamicScaleConversion" -v true;')
    
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


def cleanup_fbx(file_path):
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

    # clean up display layer
    try:
        cmds.delete(cmds.ls(type='displayLayer'))
    except:
        pass
    print('cleaned: displayLayer')

    # show all nodes
    for i in cmds.ls(type=['transform', 'joint']):
        try:
            cmds.setAttr('{}.visibility'.format(i), 1)
        except:
            pass
    print('cleaned: visibility')

    export_fbx(file_path)


def get_transform_by_shape_type(shape='mesh', fullPath=True):
    shape_transform = []
    for m in cmds.ls(type=shape):
        transforms = cmds.listRelatives(m, parent=True, type='transform', fullPath=fullPath)
        for t in transforms:
            if t not in shape_transform:
                shape_transform.append(t)
    
    return shape_transform


def get_hierachy_by_type(root, shape='joint', fullPath=True, include_root=True):
    root = cmds.ls(root, long=fullPath)
    if not root:
        return []

    root = root[0]
    hierachy = []
    if include_root:
        hierachy.append(root)
    hierachy.extend(cmds.listRelatives(root, ad=True, type=shape, fullPath=fullPath)) 
    return hierachy


def maya_export_skel(maya_file=None, main_skel=False, cleanup=False):
    cmds.loadPlugin("gameFbxExporter.mll")
    if maya_file is None:  # run on current file
        maya_file = cmds.file(q=True, sn=True)
        maya_file_name, _ = os.path.splitext(os.path.basename(maya_file))
        export_dir = cmds.fileDialog2(dialogStyle=2, fileMode=2)
        if not export_dir:
            return
        export_dir = export_dir[0]
    
    else:
        cmds.file(maya_file, o=True, f=True)
        maya_file_name, _ = os.path.splitext(os.path.basename(maya_file))
        export_dir = os.path.join(os.path.dirname(maya_file), "skel.{}".format(maya_file_name))

    if not os.path.isdir(export_dir):
        os.mkdir(export_dir)

    look_in_group = '|Group|Geometry|geo|Skin'  # TODO: check namespace
    pattern = r'(?P<CH>\w+)_(?P<SkinVersion>\w+)_(?P<Rarity>\w+)_(?P<SkinName>\w+)_(?P<PartName>\w+)'
    default_export = ["DeformationSystem"]  # TODO: check namespace
    exported = []

    # export main skeleton
    if main_skel:
        main_skeleton = os.path.join(export_dir, '{}.fbx'.format(maya_file_name))
        export_fbx(main_skeleton, default_export)
        exported.append(main_skeleton)

    # export all skin
    mesh_transform = get_transform_by_shape_type()
    matches = []
    for t in sorted(mesh_transform):
        if t.startswith(look_in_group):
            input_string = t.split('|')[-1]
            match = re.match(pattern, input_string)
            if match:
                matches.append(match.groupdict())

    print('PROGRESSCOUNT:{}\n'.format(len(matches)), flush=True)
    
    for i, match in enumerate(matches):
        export_name = '{}{}{}.fbx'.format(match["PartName"], match["Rarity"], match["SkinName"])
        export_path = os.path.join(export_dir, export_name)
        to_export = default_export.copy()
        to_export.append(t)
        print('PROGRESS:{}:Exporting:{}\n'.format(i, export_path), flush=True)

        export_fbx(export_path, to_export)
        exported.append(export_path)
        print('Exported', export_path)
        # if len(exported) >= 5:
        #     break
    print('Finished exporting. Total file: ', len(exported))

    # clean up fbx
    if cleanup:
        for f in sorted(exported):
            # print('PROGRESS:Cleaning', f)
            cleanup_fbx(f)
            print('cleaned', f)

def maya_export_anim(maya_file=None, cleanup=False):
    cmds.loadPlugin("gameFbxExporter.mll")
    if maya_file is None:  # run on current file
        maya_file = cmds.file(q=True, sn=True)
        maya_file_name, _ = os.path.splitext(os.path.basename(maya_file))
        export_dir = cmds.fileDialog2(dialogStyle=2, fileMode=2)
        if not export_dir:
            return
        export_dir = export_dir[0]
    
    else:
        cmds.file(maya_file, o=True, f=True)
        maya_file_name, _ = os.path.splitext(os.path.basename(maya_file))
        export_dir = os.path.join(os.path.dirname(maya_file), "anim.{}".format(maya_file_name))

    if not os.path.isdir(export_dir):
        os.mkdir(export_dir)

    export_name = maya_file_name.rpartition('_')[0]
    export_path = os.path.join(export_dir, '{}.fbx'.format(export_name))

    default_export = get_hierachy_by_type('Root_M')  # TODO: check namespace

    export_fbx(export_path, default_export, anim=True)

    # clean up fbx
    if cleanup:
        cleanup_fbx(export_path)
