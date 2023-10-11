'''
__PYTHON__
__file__
'''

import ffmpeg
import os

os.environ["PATH"] += os.pathsep + __TOOLS__
inputfile = __INPUTFILE__
inname, ext = os.path.splitext(inputfile)
outname = inname + '.audio.wav'
outputfile = os.path.join(os.path.dirname(inputfile), outname)

(
    ffmpeg
    .input(inputfile)
    .output(outputfile)
    .run()
)
