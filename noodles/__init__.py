
try:
    from version import version
except ImportError:
    import sys
    sys.stderr.write('Unable to import version\n')
    version = 'UNKNOWN'


from . import main
from . import imports
from . import requirements


