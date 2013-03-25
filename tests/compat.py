

import sys

is_python2 = (sys.version_info[0] == 2)

try:
    import unittest2 as unittest
except ImportError:
    import unittest

if sys.version_info[0:2] < (3, 3):
    import mock
else:
    from unittest import mock

if is_python2:
    import StringIO
    def make_io(s):
        return StringIO.StringIO(s)
else:
    import io
    def make_io(b):
        return io.BytesIO(b)
