import os
import uuid


def copy_script_to_temp_dir(script_path, temp_dir, maya_file, module_path):
    basename = os.path.basename(script_path)
    job_id = uuid.uuid4().hex
    temp_file = os.path.join(temp_dir, f'batch.{job_id}.{basename}').replace('\\', '/')
    with open(script_path, mode='rt') as f:
        data = f.read()
    print(temp_file)
    data = convert_script_data(data, temp_file, maya_file, module_path)
    with open(temp_file, mode='wt') as f:
        f.write(data)
    
    return(temp_file)


def convert_script_data(data, mayapy_path, temp_file, maya_file, module_path):

    mapping = {'__MAYAPY__': f'"{mayapy_path}"',
        '__file__': f'"{temp_file}"', 
        '__MAYAFILE__': f'"{maya_file}"',
        '__MODULE__': f'"{module_path}"',
    }
    
    for k, v in mapping.items():
        data = data.replace(k, v.replace('\\', '/'), 1)
    
    return(data)


def parse_script_to_arguments(script_path):
    with open(script_path, mode='r') as f:
        lines = f.readlines()

    breakpoints = 0
    args = []
    for line in lines:
        if line.startswith("'''"):
            breakpoints += 1
            continue

        if 1 <= breakpoints <2:
            arg = eval(line.strip())
            args.append(arg)

        elif breakpoints >= 2:
            break

    return(args)
