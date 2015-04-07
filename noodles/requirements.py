import tempfile
import textwrap
import unittest


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


class TestRequirements(unittest.TestCase):

    def test_parse_requirements_file(self):
        """Check ensure that a requirements file can be parsed.

        :returns:
        :rtype:

        """

        expected = [
            'hello',
            'world==42'
        ]
        content = '\n'.join(expected) + textwrap.dedent("""
        # a comment
        """)
        tmp = _create_requirements_file(content)
        actual = list(parse_requirements_file(tmp.name))

        for a in actual:
            self.assertIn(a, expected)

        for e in expected:
            self.assertIn(e, actual)


if __name__ == '__main__':
    unittest.main()
