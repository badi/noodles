
from . import imports

"""
Graph the interactions and dependencies.
"""


def add_args(parser):
    """Add arguments to the parser.
    This modifies the parser *in-place*.

    :param parser: an argparse parser
    """
    parser.add_argument('path', nargs='+', help='Python modules to analyze')
    parser.set_defaults(func=main)


def main(opts):

    module_paths = opts.path

    G = imports.Dependencies()

    for path in module_paths:
        G1 = imports.scan_module(path)
        G = imports.Dependencies.compose(G, G1)
    print G.to_agraph()
