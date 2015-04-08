
from . import imports

"""
Display the interactions and dependencies.
"""


if __name__ == '__main__':
    import sys
    module_paths = sys.argv[1:]

    G = imports.Dependencies()

    for path in module_paths:
        G1 = imports.scan_module(path)
        G = imports.Dependencies.compose(G, G1)
    print G.to_agraph()
