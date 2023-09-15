'''
__PYTHON__
__file__
'''

import ffmpeg
import os

os.environ["PATH"] += os.pathsep + __TOOLS__
inputfile = __INPUTFILE__
inname, ext = os.path.splitext(inputfile)
outname = inname + '.output' + ext
outputfile = os.path.join(os.path.dirname(inputfile), outname)
stream = ffmpeg.input(inputfile)
stream = ffmpeg.hflip(stream)
stream = ffmpeg.output(stream, outputfile)
ffmpeg.run(stream)
