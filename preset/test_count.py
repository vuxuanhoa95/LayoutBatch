'''
__PYTHON__
__file__
'''

import time


print('PROGRESSCOUNT:10', flush=True)
for i in range(10):
    print(r'PROGRESS:{}:Exporting:D'.format(i), flush=True)
    time.sleep(0.5)

