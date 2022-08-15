import maya.cmds as cmds
import pymel.core as pm

for s in cmds.ls(type='shot'):
    cam = pm.PyNode(pm.shot(s, q=True, cc=True))
    start_frame = pm.shot(s, q=True, st=True)
    end_frame = pm.shot(s, q=True, et=True)
    ns = cam.namespace()
    shk = ns+'shk'
    if pm.objExists(shk):
        shk = pm.PyNode(shk)
        attrs = ['tx','ty','tz','rx','ry','rz']
        for a in attrs:
            shk.attr(a).unlock()

        cmds.refresh(suspend=True)
        pm.bakeResults(shk, attribute=attrs, simulation=True, time = (start_frame, end_frame), sampleBy=1, oversamplingRate=1, 
            disableImplicitControl = True, preserveOutsideKeys = False, sparseAnimCurveBake=False, 
            removeBakedAttributeFromLayer = True, removeBakedAnimFromLayer = True, bakeOnOverrideLayer=False,
            minimizeRotation = False, controlPoints = False, shape = True)
        cmds.refresh(suspend=False)

cmds.file(save=True)