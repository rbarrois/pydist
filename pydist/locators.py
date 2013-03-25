# -*- coding: utf-8 -*-
# This code is distributed under the two-clause BSD license.
# Copyright (c) 2013 Raphaël Barrois


from __future__ import unicode_literals

import codecs
import logging
import os.path
import zipfile
import tarfile

from distlib.compat import pathname2url, urlunparse
from distlib import locators
from distlib import metadata

PKG_INFO_NAME = 'PKG-INFO'


logger = logging.getLogger(__name__)


class BaseReader(object):
    def __init__(self, filename, **kwargs):
        self.filename = filename
        logger.debug("Opening %s with %r", filename, self)
        super(BaseReader, self).__init__(**kwargs)

    def _file_exists(self, path):
        """Tests whether a given inner path exists.

        Should be overridden in subclasses."""
        return False

    def _open_pkg_info(self, path):  # pragma: no cover
        """Opens the PKG-INFO file.

        Should be overridden in subclasses.

        Returns:
            file-like object.
        """
        raise NotImplementedError()

    def _make_paths(self, package, version):
        """Prepare a list of candidate paths for PKG-INFO."""
        return [
            PKG_INFO_NAME,
            os.path.join(package, PKG_INFO_NAME),
            os.path.join(package, version, PKG_INFO_NAME),
            os.path.join('%s-%s' % (package, version), PKG_INFO_NAME),
        ]

    def _decode(self, fileobj):
        reader = codecs.getreader('utf-8')
        return reader(fileobj)

    def pkg_info(self, package, version):
        """Retrieve the contents of the PKG-INFO file."""
        for path in self._make_paths(package, version):
            if self._file_exists(path):
                logger.debug("PKG-INFO found at %s in %s", path, self.filename)
                return self._decode(self._open_pkg_info(path))

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.filename)


class FSReader(BaseReader):

    def _path(self, path):
        return os.path.join(self.filename, path)

    def _file_exists(self, path):
        return os.path.exists(self._path(path))

    def _open_pkg_info(self, path):
        return open(self._path(path), 'rb')


class ZipReader(BaseReader):
    def __init__(self, filename, **kwargs):
        super(ZipReader, self).__init__(filename, **kwargs)
        try:
            self.zfile = zipfile.ZipFile(self.filename, 'r')
        except zipfile.BadZipfile:
            self.zfile = None

    def _file_exists(self, path):
        if self.zfile is None:
            return False

        try:
            self.zfile.getinfo(path)
        except KeyError:
            return False
        return True

    def _open_pkg_info(self, path):
        if self.zfile is None:
            return None

        return self.zfile.open(path, 'r')


class TarReader(BaseReader):
    def __init__(self, filename, **kwargs):
        super(TarReader, self).__init__(filename, **kwargs)
        try:
            self.tarfile = tarfile.open(self.filename, encoding='utf-8')
        except tarfile.ReadError:
            self.tarfile = None

    def _file_exists(self, path):
        if self.tarfile is None:
            return None

        try:
            info = self.tarfile.getmember(path)
        except KeyError:
            return False
        return info.isfile()

    def _open_pkg_info(self, path):
        if self.tarfile is None:
            return None

        return self.tarfile.extractfile(path)


class DiggingDirectoryLocator(locators.DirectoryLocator):
    """A specialized DirectoryLocator that inspects the file's PKG-INFO."""

    readers = {
        '.zip': ZipReader,
        '.tar.gz': TarReader,
        '.tar.bz2': TarReader,
        '.tar': TarReader,
        '.tgz': TarReader,
        '.tbz': TarReader,
    }

    def _get_reader(self, filename):
        for ext, reader_class in self.readers.items():
            if filename.endswith(ext):
                return reader_class(filename)
        return FSReader(filename)

    def _extract_filename(self, distribution):
        url = distribution.download_url
        if url.startswith('file://'):
            url = url[len('file://'):]
        return url

    def _fill_pkg_info(self, distribution):
        filename = self._extract_filename(distribution)
        reader = self._get_reader(filename)
        pkg_info = reader.pkg_info(distribution.name, distribution.version)
        if pkg_info is not None:
            try:
                md = distribution.metadata
                md.read_file(pkg_info)
                logger.debug("Found metadata %r(%r) for %s in %s",
                        md, vars(md), filename, pkg_info)
            finally:
                pkg_info.close()

    def _get_project(self, name):
        result = super(DiggingDirectoryLocator, self)._get_project(name)
        for version, dist in result.items():
            self._fill_pkg_info(dist)
        return result
