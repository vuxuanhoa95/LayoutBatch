import logging
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as api
import maya.OpenMayaUI as OpenMayaUI


logger = logging.getLogger(__name__)


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
