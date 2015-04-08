"""
This module deals with parsing requirments.

2015-04-07 Parse requrements.txt

"""

import tempfile
import textwrap
import unittest

from .dependency import Dependencies


def parse_requirements_file(path):
    """Parse the requirements.txt

    :param path: the path to the requirements file
    :returns: the requirements
    :rtype: iterable of strings

    """

    from pip.req import parse_requirements as pip_parse_reqs

    for req in pip_parse_reqs(path):
        yield str(req.req)


def _create_requirements_file(content):
    """Create a requirements file

    :tests:

    Important: the returned file will be deleted as soon as it is
    closed or garbage collected.

    :param content: the desired content of the file :: str
    :returns: the temporary file
    :rtype: tempfile.NamedTemporaryFile

    """
    tmp = tempfile.NamedTemporaryFile(mode='w')
    tmp.write(content)
    tmp.seek(0)
    return tmp


def graph_requirements(root_name, path):
    """Graph the import dependencies of a package

    :param root_name: the name of the package
    :param path: path to the requirements file
    :returns: dependency graph
    :rtype: `noodles.dependency.Dependencies`

    """
    G = Dependencies()
    G.add_root(root_name)

    for r in parse_requirements_file(path):
        G.add_sublibrary(root_name, r)

    return G


class TestRequirements(unittest.TestCase):

    def setUp(self):
        self.expected = [
            'hello',
            'world==42'
        ]
        self.content = '\n'.join(self.expected) + textwrap.dedent("""
        # a comment
        """)

        self.tmp = _create_requirements_file(self.content)

    def test_parse_requirements_file(self):
        "Ensure that a requirements file can be parsed."

        actual = list(parse_requirements_file(self.tmp.name))

        for a in actual:
            self.assertIn(a, self.expected)

        for e in self.expected:
            self.assertIn(e, actual)

        self.tmp.seek(0)

    def test_graph_requirements(self):
        "Ensure that requirements can be added to a dependency graph"
        root_name = 'test_root'

        G = graph_requirements(root_name, self.tmp.name)
        self.tmp.seek(0)

        self.assertIn(root_name, G.nodes())
        for e in self.expected:
            self.assertIn(e, G.nodes())
            self.assertIn((root_name, e), G.edges())

if __name__ == '__main__':
    unittest.main()
