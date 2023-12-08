# tasks.py

from utils import maya_launcher

def task_run_mayapy():
    """Run a simple mayapy script using doit"""
    mayapy = maya_launcher.mayapy(2024)
    script = r"D:\Github\LayoutBatch\preset\test_maya_standalone.py"
    return {
        'actions': [f'"{mayapy}" "{script}"'],
        'verbosity': 2,
    }
