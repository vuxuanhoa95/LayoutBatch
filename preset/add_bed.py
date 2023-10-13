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
import re


if __name__ == "__main__":
    filename = sys.argv[1]

    mel.eval('setUpAxis "z";')
    cmds.file(filename, o=True, f=True)

    BED = r"d:\projects\Bate\Projects\Bates\SourceAssets\PostProcessCinematic\rig\prankroombed_rig.mb"
    namespace = os.path.splitext(os.path.basename(BED))[0]
    cmds.file(BED, reference=True, namespace=namespace)

    cmds.setAttr(f'{namespace}:bed_root_ctrl.translate', 377.3821334838867, -1369.6637166341145, 0.9339981231689478, type='double3')
    cmds.setAttr(f'{namespace}:bed_root_ctrl.rotate', 0.0, 0.0, -90.0, type='double3')
    cmds.setAttr('GYM_sam_room*:Extra|GYM_sam_room:prankroombed_VTS_UP_001_bed_002:SM_prankroombed_VTS_UP_001_bed_002.visibility', 0)

    # filename = cmds.file(q=True, sceneName=True)
    match = re.search(r'_v(?P<version>\d+)_(?P<comment>[^_]*)_(?P<user>[^_]*)', filename)
    if match:
        version = str(int(match.group('version')) + 1).zfill(4)
        comment = 'add-bed'
        user = 'hvu'
        newname = re.sub(r'_v(?P<version>\d+)_(?P<comment>[^_]*)_(?P<user>[^_]*)', '_v{}_{}_{}'.format(version, comment, user), filename)

    else:
        newname = f'{os.path.splitext(filename)[0]}.addbed.ma'
        
    print(newname)
    cmds.file(rename=newname)
    cmds.file(save=True, type='mayaAscii')
