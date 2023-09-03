import maya.cmds as cmds
import maya.mel as mel

cmds.file(r'X:\LNY\03_Workflow\Shots\seq-Shot100\Scenefiles\lay\Layout\shot_seq-Shot100_lay_Layout_v0004__hvu_.ma', open=True)

# cams = cmds.ls(type='camera')
# for cam in cams:
#     cmds.setAttr(cam + '.rnd', 0)

for s in sorted(cmds.ls(type='shot')):
    start_frame = cmds.shot(s, q=True, st=True)
    end_frame = cmds.shot(s, q=True, et=True)
    print('shot', s, start_frame, end_frame)

    cam = cmds.shot(s, q=True, cc=True)
    cmds.setAttr(cam + '.rnd', 1)
    print('Active camera', cam)

    mel.eval('setCurrentRenderer "mayaHardware2";')
    mel.eval('catchQuiet(`setAttr ("hardwareRenderingGlobals.renderMode") 4`);')
    mel.eval('colorManagementPrefs -e -outputTransformEnabled true -outputTarget "renderer";')
    mel.eval('colorManagementPrefs -e -outputUseViewTransform -outputTarget "renderer";')

    aPlayBackSliderPython = mel.eval('$tmpVar=$gPlayBackSlider')
    sound_node = cmds.timeControl(aPlayBackSliderPython, query=True, sound=True)
    if sound_node:
        cmds.playblast(startTime=start_frame, endTime=end_frame, format="avi", sequenceTime=True,
            os=True,
            percent=100, viewer=True, forceOverwrite=True, showOrnaments=False,
            filename='D:/temp/test.avi',
            sound=sound_node, wh=(1440,720)
        )
    else:
        cmds.playblast(startTime=start_frame, endTime=end_frame, format="avi",
            sequenceTime=True,
            os=True,
            percent=100, viewer=True, forceOverwrite=True, showOrnaments=False,
            filename='D:/temp/test.avi',
            wh=(1440,720)
        )

    break
