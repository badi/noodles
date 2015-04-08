import copy
import imp
import sys

import types
import unittest


def _find_and_load_single_module(name, path):
    """Find and load a single module using `imp.find_module` and `imp.load_module`

    :param name: name of the module :: str
    :param path: paths to search in :: str or None
    :returns: the module
    :rtype: `module`
    """

    try:
        fileobj, path, descr = imp.find_module(name, path)

        if path is not None:
            return imp.load_module(name, fileobj, path, descr)

    finally:
        try:
            if fileobj is not None:
                fileobj.close()
        except UnboundLocalError:
            pass


def find_module(name, path=None):
    """Try to find the module name. This is a wrapper over the builtin
    imp.find_module but handles hierarchical module names.

    :param name: the name of the module
    :param path: optional path to search in
    :returns: path to the module
    :rtype: str
    """

    names = name.split('.')
    module = imp.new_module('dummy_module')

    for n in names:
        if hasattr(module, n):
            module = getattr(module, n)
        else:
            module = _find_and_load_single_module(n, path)

        if hasattr(module, '__path__'):
            path = module.__path__

    return module


def dummy_module(name):
    """Create an empy module with the given name.

    Note: this does *not* insert the module into `sys.modules`.

    :param name: name of the module
    :returns: the new module
    :rtype: module

    """
    return imp.new_module(name)


def save_sys_modules():

    class stack(object):
        def __init__(self):
            self._modules_backup = None

        def __enter__(self):
            self._modules_backup = copy.copy(sys.modules)

        def __exit__(self, *args, **kws):
            sys.modules = self._modules_backup

    return stack()


class TestImportMagic(unittest.TestCase):
    def setUp(self):
        self.module_name = 'test_module_0000000000000000000000000000000000000'


    def test_find_simple(self):
        "Import a simple existing module"
        mod = find_module('os')
        self.assertIsInstance(mod, types.ModuleType)

    def test_find_hierarchical(self):
        "Import a hierarchical existing module"
        mod = find_module('os.path')
        self.assertIsInstance(mod, types.ModuleType)

    def test_save_sys_modules(self):
        "Do not clobber sys.modules"
        self.assertNotIn(self.module_name, sys.modules)
        with save_sys_modules():
            mod = imp.new_module(self.module_name)
            sys.modules[self.module_name] = mod
            self.assertIn(self.module_name, sys.modules)
        self.assertNotIn(self.module_name, sys.modules)

    def test_dummy_module(self):
        "Creating a dummy module should not clobber `sys.modules`"
        self.assertNotIn(self.module_name, sys.modules)
        mod = dummy_module(self.module_name)
        self.assertIsInstance(mod, types.ModuleType)
        self.assertNotIn(self.module_name, sys.modules)


if __name__ == '__main__':
    unittest.main()
