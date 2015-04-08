import ast
import inspect
import operator
import tempfile
import textwrap
import unittest

import networkx as nx


class EdgeLabels:
    IMPORT = 'import'


class Color:
    # FIXME: until a programatic way of determining if a module is
    # provided with Python proper of is an externally installed
    # package, these two will be identical
    MODULE_INTERN = 'black'
    MODULE_EXTERN = 'black'

    ATTRIBUTE = 'black'
    ROOT = 'blue'
    IMPORT = 'blue'


class NodeLabels:
    MODULE = 'module'
    ATTRIBUTE = 'attr'


class Dependencies(object):
    def __init__(self):
        self._G = nx.DiGraph()

    def nodes(self):
        return self._G.nodes()

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

    def add_module(self, name, builtin=True):
        c = Color.MODULE_INTERN if builtin else Color.MODULE_EXTERN
        self._add_node(name, color=c)

    def add_submodule(self, root, module, builtin=True):
        self.add_module(module, builtin=builtin)
        self._G.add_edge(root, module,
                         color=Color.IMPORT)

    def add_attribute(self, name):
        self._add_node(name, label=NodeLabels.ATTRIBUTE)

    def add_subattribute(self, root, attr):
        self.add_attribute(root)
        self._G.add_edge(root, attr,
                         color=Color.ATTRIBUTE)

    @classmethod
    def compose(cls, D0, D1):
        G = nx.compose(D0._G, D1._G)
        D = cls()
        D._G = G
        return D

    def to_agraph(self):
        return nx.to_agraph(self._G)


def parse_module_imports(root_name, module):
    """Parse a python module for all 'import' statements and extract the

    :param root_name: the name of the module being scanned
    :param module: the source of a python module
    :returns: all modules imported
    :rtype: `nx.DiGraph`

    """
    D = Dependencies()
    D.add_root(root_name)

    tree = ast.parse(module)
    for node in ast.walk(tree):

        if type(node) is ast.Import:
            for child in node.names:
                name = child.name
                D.add_submodule(root_name, name)

        elif type(node) is ast.ImportFrom:
            D.add_submodule(root_name, node.module)
            for name in node.names:
                D.add_subattribute(node.module, name.name)

        else:
            continue

    return D


def scan_module(path):
    """Scan a python module and generate a graph if imports.

    :param path: path to the module
    :returns: graph of imports
    :rtype: (name :: str, graph ::`nx.DiGraph`)

    """

    with open(path) as fd:
        source = fd.read()

    return parse_module_imports(path, source)


class TestImports(unittest.TestCase):

    def setUp(self):
        # IMPORTANT:
        # make sure to update both `nodes` and `source` when adding/removing

        self.module_name = 'test_imports'

        self.nodes = {'os': None,
                      'tempfile': ['NamedTemporaryFile', 'mkstemp']}

        self.source = textwrap.dedent("""\
        import os
        from tempfile import NamedTemporaryFile, mkstemp
        """)

    def test_parse_module_imports(self, G=None, name=None):

        module_name = self.module_name

        if G is None:
            G = parse_module_imports(self.module_name, self.source)

        if name is not None:
            module_name = name

        # ensure we have a graph
        self.assertIsInstance(G, Dependencies)

        # ensure that the nodes are picked up
        self.assertIn(module_name, G.nodes())
        for n in self.nodes.keys():
            self.assertIn(n, G.nodes())

        # ensure that there is an edge between nodes
        edges = G.out_edges(module_name)
        neighbors = map(operator.itemgetter(1), edges)
        for n in self.nodes.keys():
            self.assertIn(n, neighbors)

        # ensure that the

    def test_scan_module(self):
        tmp = tempfile.NamedTemporaryFile()
        tmp.write(self.source)
        tmp.seek(0)

        G = scan_module(tmp.name)
        self.test_parse_module_imports(G=G, name=tmp.name)


if __name__ == '__main__':
    unittest.main()
