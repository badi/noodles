
"""
Main entry point for CLI interface
"""

import argparse

from . import graph

from .version import version


def getopts():
    args = argparse.ArgumentParser()

    # global parameters
    args.add_argument('--version', action='version', version=version)

    parsers = args.add_subparsers(help='Graph dependencies')

    graphP = parsers.add_parser('graph')
    graph.add_args(graphP)

    return args.parse_args()


def main():
    opts = getopts()
    opts.func(opts)
