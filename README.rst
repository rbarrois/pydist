PyDist
======

pydist is a set of tools to help converting Python modules into distribution-ready packages.

It aims to support the following distributions:

- Debian
- Gentoo


Concepts
--------

.. warning:: pydist is still a work in progress. This document is actually only a design doc 

Setup
"""""

A pydist environment can be setup using the following instructions:

.. code-block:: sh

  # Prepare the environment
  $ pydist init

  # Add distribution-specific targets
  $ pydist target debian deb/
  $ pydist target gentoo gentoo/


Once those commands have run, the layout should be::

  ./
  + pydist.conf
  + deb.packages
  + deb/
  | + foo/
  | | + (Debian-specific contents)
  | + bar/
  | | + (Debian-specific contents)
  |
  + gentoo.packages
  + gentoo/
  | + dev-python/
  | | + foo/
  | | | + foo-0.1.1.ebuild
  | | | + foo-0.2.0.ebuild
  | | + bar/
  | | | + bar-0.1.0.ebuild
  | | | + bar-0.1.0-r1.ebuild


Adding a package
""""""""""""""""

.. code-block:: sh

  # From a local file
  $ pydist import ~/foo.tar.gz

  # From an arbitrary URL
  $ pydist import http://downloads.example.com/foo.zipp

  # From a PyPI-like index
  $ pydist import pypi://foo


Building a package
""""""""""""""""""

A package can be build using distribution-native tools; a helper is also provided:

.. code-block:: sh

  # Build all un-built versions
  $ pydist build foo

  # Build specific versions
  $ pydist build foo 0.1.0 0.2.4


Testing packages
""""""""""""""""

Running the packages tests may be useful.

.. code-block:: sh

  # Test only for a specific target
  $ pydist test --target=gentoo foo
