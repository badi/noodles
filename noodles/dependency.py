import networkx as nx
import unittest


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


class NodeLabels:
    MODULE = 'module'
    ATTRIBUTE = 'attr'


class Dependencies(object):
    def __init__(self):
        self._G = nx.DiGraph()

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

    def add_module(self, name, builtin=True):
        c = Color.MODULE_INTERN if builtin else Color.MODULE_EXTERN
        self._add_node(name, color=c)

    def add_submodule(self, root, module, builtin=True):
        self.add_module(module, builtin=builtin)
        self._G.add_edge(root, module,
                         color=Color.IMPORT)

    def add_attribute(self, name):
        self._add_node(name, label=NodeLabels.ATTRIBUTE, color=Color.ATTRIBUTE)

    def add_subattribute(self, root, attr):
        self.add_attribute(root)
        self.add_attribute(attr)
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


class TestDependencies(unittest.TestCase):
    def setUp(self):
        self.G = Dependencies()
        self.r = 'test_root'
        self.child_template = 'test_node_{}'
        self.counter = 0

    def new_child(self):
        name = self.child_template.format(self.counter)
        self.counter += 1
        return name

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
        name = self.r
        self.G.add_root(name)
        self.is_root(name)

    def test_add_module(self):
        name = self.c
        self.G.add_module(name)
        self.is_module(name)

    def test_add_submodule(self):
        root = self.r
        child = self.c
        self.G.add_submodule(root, child)
        self.is_node(root)
        self.is_module(child)
        self.is_edge(root, child)
        self.edge_color(root, child, Color.IMPORT)

    def test_add_attribute(self):
        name = self.c
        self.G.add_attribute(name)
        self.is_node(name)
        self.is_attribute(name)

    def test_add_subattribute(self):
        root = self.r
        child = self.c
        self.G.add_subattribute(root, child)
        self.is_node(root)
        self.is_attribute(child)
        self.is_edge(root, child)
        self.edge_color(root, child, Color.ATTRIBUTE)

