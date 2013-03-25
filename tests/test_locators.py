#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This code is distributed under the two-clause BSD license.
# Copyright (c) 2013 Raphaël Barrois

from __future__ import unicode_literals

import os.path

from pydist import locators

from .compat import mock, make_io, unittest


class ReaderTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        class FakeReader(locators.BaseReader):
            def _file_exists(self, path):
                return path == 'foo-0.1.0/PKG-INFO'

            def _open_pkg_info(self, path):
                return make_io(b'<the_data>')

        cls.FakeReader = FakeReader

    def test_base(self):
        r = locators.BaseReader('/foo')
        self.assertIn('/foo', repr(r))
        self.assertIn('BaseReader', repr(r))

    def test_naive(self):
        r = locators.BaseReader('')
        self.assertIsNone(r.pkg_info('foo', '0.1.0'))

    def test_fake_failure(self):
        r = self.FakeReader('/bar')
        self.assertIsNone(r.pkg_info('fuz', '0.1.0'))

    def test_fake_success(self):
        r = self.FakeReader('/')
        self.assertIsNone(r.pkg_info('foo', '0.2.0'))
        self.assertIsNone(r.pkg_info('fuz', '0.1.0'))

        data = r.pkg_info('foo', '0.1.0')
        self.assertIsNotNone(data)
        self.assertEqual("<the_data>", data.read())


class FSReaderTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            'testdata',
            'reader',
        )

    def test_notfound(self):
        r = locators.FSReader(os.path.join(self.root, 'fs1'))
        self.assertIsNone(r.pkg_info('bar', '0.1.0'))

    def test_found_standard(self):
        """Finding the PKG-INFO file as usual, under $pkg-$version/PKG-INFO."""
        r = locators.FSReader(os.path.join(self.root, 'fs1'))

        data = r.pkg_info('foo', '0.1.0')
        self.assertIsNotNone(data)
        self.assertEqual("fs1\n", data.read())

    def test_found_noversion(self):
        """Finding the PKG-INFO file under $pkg/PKG-INFO."""
        r = locators.FSReader(os.path.join(self.root, 'fs2'))

        data = r.pkg_info('foo', '0.4.3')
        self.assertIsNotNone(data)
        self.assertEqual("fs2\n", data.read())

    def test_found_alt(self):
        """Finding the PKG-INFO file under $pkg/$version/PKG-INFO."""
        r = locators.FSReader(os.path.join(self.root, 'fs3'))

        data = r.pkg_info('foo', '0.1.0')
        self.assertIsNotNone(data)
        self.assertEqual("fs3\n", data.read())

    def test_found_root(self):
        """Finding the PKG-INFO at the root of the directory."""
        r = locators.FSReader(os.path.join(self.root, 'fs4'))

        data = r.pkg_info('bar', '4.3.2')
        self.assertIsNotNone(data)
        self.assertEqual("fs4\n", data.read())


class ZipReaderTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            'testdata',
            'reader',
        )

    def test_notfound(self):
        r = locators.ZipReader(os.path.join(self.root, 'fs1.zip'))
        self.assertIsNone(r.pkg_info('bar', '0.1.0'))

    def test_invalid(self):
        r = locators.ZipReader(os.path.join(self.root, 'fs0.zip'))
        self.assertIsNone(r.pkg_info('foo', '0.1.0'))

    def test_found_standard(self):
        """Finding the PKG-INFO file as usual, under $pkg-$version/PKG-INFO."""
        r = locators.ZipReader(os.path.join(self.root, 'fs1.zip'))

        data = r.pkg_info('foo', '0.1.0')
        self.assertIsNotNone(data)
        self.assertEqual("fs1\n", data.read())

    def test_found_noversion(self):
        """Finding the PKG-INFO file under $pkg/PKG-INFO."""
        r = locators.ZipReader(os.path.join(self.root, 'fs2.zip'))

        data = r.pkg_info('foo', '0.4.3')
        self.assertIsNotNone(data)
        self.assertEqual("fs2\n", data.read())

    def test_found_alt(self):
        """Finding the PKG-INFO file under $pkg/$version/PKG-INFO."""
        r = locators.ZipReader(os.path.join(self.root, 'fs3.zip'))

        data = r.pkg_info('foo', '0.1.0')
        self.assertIsNotNone(data)
        self.assertEqual("fs3\n", data.read())

    def test_found_root(self):
        """Finding the PKG-INFO at the root of the directory."""
        r = locators.ZipReader(os.path.join(self.root, 'fs4.zip'))

        data = r.pkg_info('bar', '4.3.2')
        self.assertIsNotNone(data)
        self.assertEqual("fs4\n", data.read())


class TarReaderTestCase(unittest.TestCase):
    ext = 'tar'

    @classmethod
    def setUpClass(cls):
        cls.root = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            'testdata',
            'reader',
        )

    def test_notfound(self):
        r = locators.TarReader(os.path.join(self.root, 'fs1.%s' % self.ext))
        self.assertIsNone(r.pkg_info('bar', '0.1.0'))

    def test_invalid(self):
        r = locators.TarReader(os.path.join(self.root, 'fs0.%s' % self.ext))
        self.assertIsNone(r.pkg_info('foo', '0.1.0'))

    def test_found_standard(self):
        """Finding the PKG-INFO file as usual, under $pkg-$version/PKG-INFO."""
        r = locators.TarReader(os.path.join(self.root, 'fs1.%s' % self.ext))

        data = r.pkg_info('foo', '0.1.0')
        self.assertIsNotNone(data)
        self.assertEqual("fs1\n", data.read())

    def test_found_noversion(self):
        """Finding the PKG-INFO file under $pkg/PKG-INFO."""
        r = locators.TarReader(os.path.join(self.root, 'fs2.%s' % self.ext))

        data = r.pkg_info('foo', '0.4.3')
        self.assertIsNotNone(data)
        self.assertEqual("fs2\n", data.read())

    def test_found_alt(self):
        """Finding the PKG-INFO file under $pkg/$version/PKG-INFO."""
        r = locators.TarReader(os.path.join(self.root, 'fs3.%s' % self.ext))

        data = r.pkg_info('foo', '0.1.0')
        self.assertIsNotNone(data)
        self.assertEqual("fs3\n", data.read())

    def test_found_root(self):
        """Finding the PKG-INFO at the root of the directory."""
        r = locators.TarReader(os.path.join(self.root, 'fs4.%s' % self.ext))

        data = r.pkg_info('bar', '4.3.2')
        self.assertIsNotNone(data)
        self.assertEqual("fs4\n", data.read())


class TarGzReaderTestCase(TarReaderTestCase):
    ext = 'tar.gz'


class TGZReaderTestCase(TarReaderTestCase):
    ext = 'tgz'


class TarBz2ReaderTestCase(TarReaderTestCase):
    ext = 'tar.bz2'


class TBZReaderTestCase(TarReaderTestCase):
    ext = 'tbz'


class TarGzReaderTestCase(TarReaderTestCase):
    ext = 'tar.gz'


class TGZReaderTestCase(TarReaderTestCase):
    ext = 'tgz'


class DiggingDirectoryLocatorTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            'testdata',
            'locator',
        )

    def test_no_file(self):
        root = self.root.replace('locator', 'locator-empty')
        l = locators.DiggingDirectoryLocator(root)
        self.assertEqual(set(), l.get_distribution_names())

    def test_unknown_project(self):
        l = locators.DiggingDirectoryLocator(self.root)
        self.assertEqual({}, l.get_project('bar'))

    def test_known_project_no_pkg_info(self):
        l = locators.DiggingDirectoryLocator(self.root)
        dists = l.get_project('baz')
        self.assertIn('0.2.0', dists)

        dist = dists['0.2.0']
        self.assertEqual("UNKNOWN", dist.metadata['author'])

    def test_known_project_pkg_info(self):
        l = locators.DiggingDirectoryLocator(self.root)
        dists = l.get_project('foo')
        self.assertIn('0.2.0', dists)

        dist = dists['0.2.0']
        self.assertEqual("Raphaël Barrois", dist.metadata['author'])
        self.assertEqual("Some random test package", dist.metadata['summary'])
        self.assertEqual("BSD", dist.metadata['license'])
        self.assertEqual(
            ["pydist", "foo", "test"],
            dist.metadata['keywords'],
        )


if __name__ == '__main__':
    unittest.main()
