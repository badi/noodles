import ast
import operator
import tempfile
import textwrap
import unittest

from .dependency import Dependencies


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
