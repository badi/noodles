
from .dependency import Dependencies
from .imports import scan_module
from .requirements import graph_requirements

"""
Graph the interactions and dependencies.
"""


def add_args(parser):
    """Add arguments to the parser.
    This modifies the parser *in-place*.

    :param parser: an argparse parser
    """
    mod = parser.add_argument_group()
    mod.add_argument('-m', '--modules', nargs='+',
                     help='Python modules to analyze')

    req = parser.add_argument_group()
    req.add_argument('-n', '--name', help='Name to give this package')
    req.add_argument('-r', '--requirements',
                     help='Requirements to parse')

    parser.set_defaults(func=main)


def main(opts):

    G = Dependencies()

    # handle modules
    if opts.modules:
        for path in opts.modules:
            mod = scan_module(path)
            G = Dependencies.compose(G, mod)

    # requirements
    if opts.name:
        for root in G.roots:
            G._G.add_edge(opts.name, root)

        req = graph_requirements(opts.name, opts.requirements)
        G = Dependencies.compose(G, req)

    print G.to_agraph()
