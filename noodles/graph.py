
from . import imports

"""
Graph the interactions and dependencies.
"""


def main(opts):

    module_paths = opts.path

    G = imports.Dependencies()

    for path in module_paths:
        G1 = imports.scan_module(path)
        G = imports.Dependencies.compose(G, G1)
    print G.to_agraph()
