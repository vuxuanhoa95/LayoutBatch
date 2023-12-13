import time
import maya.standalone
maya.standalone.initialize()

import maya.cmds as cmds
import maya.mel as mel
import os
import sys


print('PROGRESSCOUNT:10', flush=True)

for i in range(60):
    data = r'PROGRESS:{}:Exporting:Omg'.format(i)
    print(data, flush=True)
    with open("test.txt", "w") as f:
        f.write(data)
        f.write("\n")
    time.sleep(0.5)
    