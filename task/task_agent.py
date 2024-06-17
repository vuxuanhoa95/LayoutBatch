import importlib
import os
import sys

def load_module(modname, fname):
    print("loading module", modname)
    spec = importlib.util.spec_from_file_location(modname, fname)
    module = importlib.util.module_from_spec(spec)
    sys.modules[modname] = module
    spec.loader.exec_module(module)
    return module

def relative_path(path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, path)