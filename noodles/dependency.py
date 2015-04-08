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
