'''
__PYTHON__
__file__
'''

import ffmpeg
import os
import re

def get_digits_at_end(file_name):
    digits_at_end = re.search(r'\d+$', file_name)
    if digits_at_end:
        return digits_at_end.group()
    else:
        return

os.environ["PATH"] += os.pathsep + __TOOLS__
inputfile = __INPUTFILE__
directory = os.path.dirname(inputfile)
basename = os.path.basename(inputfile)
inname, ext = os.path.splitext(inputfile)

digits_at_end = re.search(r'\d+(?=\.\w+$)', basename)
if digits_at_end:
    pattern = re.sub(r'\d+(?=\.\w+$)', f'%0{len(digits_at_end.group())}d', basename)

    outname = 'output.mp4'
    outputfile = os.path.join(directory, outname)

    framerate = 30
    (
        ffmpeg
        .input(f'{directory}/{pattern}', framerate=framerate)
        .output(outname)
        .run()
    )
