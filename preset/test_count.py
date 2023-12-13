'''
__PYTHON__
__file__
'''

import time


print('PROGRESSCOUNT:10', flush=True)
for i in range(10):
    data = r'PROGRESS:{}:Exporting:Omg'.format(i)
    print(data, flush=True)
    with open("test.txt", "w") as f:
        f.write(data)
        f.write("\n")
    time.sleep(0.5)

