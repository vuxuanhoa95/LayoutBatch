import os


def copy_script_to_temp(script_path, temp_dir):
    basename = os.path.basename(script_path)
    temp_file = os.path.join(temp_dir, f'batch.{basename}').replace('\\', '/')
    with open(script_path, mode='rt') as f:
        data = f.read()
    print(temp_file)
    with open(temp_file, mode='wt') as f:
        f.write(data.replace('__file__', f"'{temp_file}'"))

copy_script_to_temp(r"C:\Dev\LayoutBatch\preset\test_export_fbx.py", r"C:\Dev\Temp")
