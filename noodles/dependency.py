import copy
import sys
import unittest
import networkx as nx

from . import import_magic


class EdgeLabels:
    IMPORT = 'import'


class Color:
    # FIXME: until a programatic way of determining if a module is
    # provided with Python proper of is an externally installed
    # package, these two will be identical
    MODULE_INTERN = 'black'
    MODULE_EXTERN = 'black'
    MODULE = MODULE_INTERN

    ATTRIBUTE = 'black'
    ROOT = 'blue'
    IMPORT = 'blue'

    LIBRARY = 'purple'


class NodeLabels:
    MODULE = 'module'
    ATTRIBUTE = 'attr'


class Alias(object):
    """This handles import rename.  For example, `os.path` and `path` are
    the same module in the following, even though they have different
    names:

    >>> import os
    >>> from os import path
    >>> os.path == path
    True
    """

    def __init__(self):

        # this maps entities (modules, functions, etc) to a string
        # >>> import os
        # >>> from os import path
        # ...
        # >>> _map[os.path]
        # 'path'
        # >>> _map[path]
        # 'path'
        self._map = dict()

    def lookup(self, module_name):
        if module_name in sys.modules:
            module = sys.modules[module_name]
        else:
            module = import_magic.find_module(module_name)

        if module in self._map:
            return self._map[module]
        else:
            self._map[module] = module_name
            return module_name


# FIXME: test suite for Alias class

class Dependencies(object):
    def __init__(self):
        self._G = nx.DiGraph()
        self._roots = set()
        self._aliases = Alias()

    @property
    def roots(self):
        return self._roots

    @property
    def node(self):
        return self._G.node

    @property
    def edge(self):
        return self._G.edge

    def nodes(self):
        return self._G.nodes()

    def edges(self):
        return self._G.edges()

    def out_edges(self, *args, **kws):
        return self._G.out_edges(*args, **kws)

    def _add_node(self, name, **kws):
        """Add a node only if it does not already exist

        :param name: the node name
        :param kws: key word arguments to label the node

        """
        if name not in self._G.nodes():
            self._G.add_node(name, **kws)

    def add_root(self, name):
        self._add_node(name, color=Color.ROOT)
        self._roots.add(name)

    def add_module(self, name, builtin=True):
        c = Color.MODULE_INTERN if builtin else Color.MODULE_EXTERN
        realname = self._aliases.lookup(name)
        self._add_node(realname, color=c)

    def add_submodule(self, root, module, builtin=True):
        self.add_module(module, builtin=builtin)
        self._G.add_edge(root, module,
                         color=Color.IMPORT)

    def add_attribute(self, name):
        self._add_node(name, color=Color.ATTRIBUTE)

    def add_subattribute(self, root, attr):
        self.add_attribute(root)
        self.add_attribute(attr)
        self._G.add_edge(root, attr,
                         color=Color.ATTRIBUTE)

    def add_library(self, name):
        self._G.add_node(name, color=Color.LIBRARY)

    def add_sublibrary(self, parent, lib):
        self._G.add_node(parent)
        self.add_library(lib)
        self._G.add_edge(parent, lib)

    @classmethod
    def compose(cls, D0, D1):
        G = nx.compose(D0._G, D1._G)
        D = cls()
        D._G = G
        D._roots = D0._roots.union(D1._roots)
        return D

    def to_agraph(self):
        return nx.to_agraph(self._G)


class TestDependencies(unittest.TestCase):
    def setUp(self):
        # for some reason these **must** be imported otherwise really
        # bizzare error errors occur.
        #
        # This is what happens. Running
        # $ nosetests --all-modules noodles
        # will cause 'KeyError's saying that these are missing.
        import email, xmlrpclib

        self.G = Dependencies()
        self._root_name = 'test_root'
        self.child_template = 'test_node_{}'
        self.counter = 0
        self.modules_backup = copy.copy(sys.modules)

    def tearDown(self):
        sys.modules = self.modules_backup

    def new_child(self):
        name = self.child_template.format(self.counter)
        self.counter += 1

        module = import_magic.dummy_module(name)
        sys.modules[name] = module

        return name

    @property
    def r(self):
        "make sure the root module is importable"
        if self._root_name not in sys.modules:
            mod = import_magic.dummy_module(self._root_name)
            sys.modules[self._root_name] = mod
        return self._root_name

    @property
    def c(self):
        "child name"
        return self.new_child()

    def node_color(self, name, color):
        self.assertEqual(self.G.node[name]['color'], color)

    def edge_color(self, s, t, c):
        self.assertEqual(self.G.edge[s][t]['color'], c)

    def is_node(self, name):
        self.assertIn(name, self.G.nodes())

    def is_root(self, name):
        self.is_node(name)
        self.node_color(name, Color.ROOT)

    def is_module(self, name):
        self.is_node(name)
        self.node_color(name, Color.MODULE)

    def is_attribute(self, name):
        self.is_node(name)
        self.node_color(name, Color.ATTRIBUTE)

    def is_edge(self, s, t):
        self.assertIn((s, t), self.G.edges())

    def test_add_root(self):
        "Adding a root node"
        name = self.r
        self.G.add_root(name)
        self.is_root(name)

    def test_add_module(self):
        "An added module should be a node"
        name = self.c
        self.G.add_module(name)
        self.is_module(name)

    def test_add_submodule(self):
        "An added submodule should be a node"
        root = self.r
        child = self.c
        self.G.add_submodule(root, child)
        self.is_node(root)
        self.is_module(child)
        self.is_edge(root, child)
        self.edge_color(root, child, Color.IMPORT)

    def test_add_attribute(self):
        "An imported attribute should be a node"
        name = self.c
        self.G.add_attribute(name)
        self.is_node(name)
        self.is_attribute(name)

    def test_add_subattribute(self):
        "Importing a an attribute should create an edge"
        root = self.r
        child = self.c
        self.G.add_subattribute(root, child)
        self.is_node(root)
        self.is_attribute(child)
        self.is_edge(root, child)
        self.edge_color(root, child, Color.ATTRIBUTE)

    def test_add_library(self):
        "Adding a library should create a node"
        name = self.r
        self.G.add_library(name)
        self.is_node(name)
        self.node_color(name, Color.LIBRARY)

    def test_add_sublibrary(self):
        "Adding a sublibrary should create an edge"
        parent = self.r
        lib = self.c
        self.G.add_sublibrary(parent, lib)
        self.is_node(parent)
        self.is_node(lib)
        self.node_color(lib, Color.LIBRARY)


if __name__ == '__main__':
    unittest.main()
