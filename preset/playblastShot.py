import maya.cmds as cmds
import maya.mel as mel

for s in sorted(cmds.ls(type='shot')):
    start_frame = cmds.shot(s, q=True, st=True)
    print('start frame', start_frame, s)

    end_frame = cmds.shot(s, q=True, et=True)
    cam = cmds.shot(s, q=True, cc=True)
    cmds.setAttr(cam + '.rnd', 1)
    print('Active camera', cam)

    mel.eval('setCurrentRenderer "mayaHardware2";')
    mel.eval('catchQuiet(`setAttr ("hardwareRenderingGlobals.renderMode") 4`);')
    mel.eval('colorManagementPrefs -e -outputTransformEnabled true -outputTarget "renderer";')
    mel.eval('colorManagementPrefs -e -outputUseViewTransform -outputTarget "renderer";')

    aPlayBackSliderPython = mel.eval('$tmpVar=$gPlayBackSlider')
    sound_node = cmds.timeControl(aPlayBackSliderPython, query=True, sound=True)

    cmds.playblast(startTime=start_frame, endTime=end_frame, format="qt", compression="H.264", sequenceTime=True,
                   csd=True,
                   percent=100, viewer=True, forceOverwrite=True, offScreen=True, showOrnaments=True,
                   filename='D:/temp/test.mov',
                   sound=sound_node, wh=[1280, 720])

    break
