'''
__MAYAPY__
__file__
__INPUTFILE__
'''

import maya.standalone
maya.standalone.initialize()

import sys
import os
import maya.cmds as cmds

# Function to perform the playblast
def create_playblast(maya_file, width=1280, height=720, format='avi', compression='none'):
    output_file = os.path.splitext(maya_file)[0] + '.avi'
    cmds.file(maya_file, o=True, f=True)

    cams = cmds.ls(type='camera')
    for cam in cams:
        try:
            cmds.setAttr(cam + '.rnd', 0)
        except:
            pass
    
    shots = cmds.ls(type='shot')
    if shots:
        cam = cmds.shot(shots[0], q=True, cc=True)
        if cmds.objectType(cam) == 'camera':
            cmds.setAttr(cam + '.rnd', 1)
        else:
            cam = cmds.listRelatives(cam, c=True, type='camera')[0]
            cmds.setAttr(cam + '.rnd', 1)
    else:
        cam = cmds.ls("*:camShape", type='camera')
        if cam:
            cam = cam[0]
            cmds.setAttr(cam + '.rnd', 1)
        else:
            return

    # Set the playback range
    # cmds.playbackOptions(minTime=start_frame, maxTime=end_frame)
    
    # Set the render settings
    # cmds.setAttr('defaultRenderGlobals.imageFormat', 8)  # 8 is for AVI, you can change based on format
    
    # Perform the playblast
    cmds.playblast(
        filename=output_file,
        format=format,
        forceOverwrite=True,
        clearCache=True,
        viewer=False,
        showOrnaments=True,
        fp=4,  # Play every frame
        percent=100,
        compression=compression,
        quality=100,  # Adjust the quality as needed
        widthHeight=(width, height)
    )

# Define parameters

start_frame = 1
end_frame = 100

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
            create_playblast(f)
            print('PROGRESS:{}:Exporting:{}\n'.format(i, f), flush=True)

    elif file.endswith(".ma") or file.endswith(".mb"):
        create_playblast(file)