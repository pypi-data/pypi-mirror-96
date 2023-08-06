#
#  This is the gexml setuptools script.
#  Originally developed by Ryan Kelly, 2009.
#
#  This script is placed in the public domain.
#

import sys

setup_kwds = {}


#  Use setuptools is available, so we have `python setup.py test`.
#  We also need it for 2to3 integration on python3.
#  Otherwise, fall back to plain old distutils.
try:
    from setuptools import setup
except ImportError:
    if sys.version_info > (3,):
        raise RuntimeError("python3 support requires setuptools")
    from distutils.core import setup
else:
    setup_kwds["test_suite"] = "gexml.test"
    if sys.version_info > (3,):
        setup_kwds["use_2to3"] = False


#  Extract the docstring and version declaration from the module.
#  To avoid errors due to missing dependencies or bad python versions,
#  we explicitly read the file contents up to the end of the version
#  declaration, then exec it ourselves.
info = {}
src = open("gexml/__init__.py")
lines = []

for ln in src:
    lines.append(ln)
    if "__version__" in ln:
        for ln in src:
            if "__version__" not in ln:
                break
            lines.append(ln)
        break
exec("".join(lines),info)


NAME = "gexml"
VERSION = info["__version__"]
DESCRIPTION = "A dead-simple Object-XML mapper for Python"
LONG_DESC = info["__doc__"]
AUTHOR = "Greg Albrecht"
AUTHOR_EMAIL = "oss@undef.net"
URL = "https://github.com/ampledata/gexml"
LICENSE = "MIT"
KEYWORDS = "xml"
CLASSIFIERS = [
    "Programming Language :: Python",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 2.5",
    "Programming Language :: Python :: 2.6",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.2",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.6",
    "License :: OSI Approved",
    "License :: OSI Approved :: MIT License",
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "Topic :: Text Processing",
    "Topic :: Text Processing :: Markup",
    "Topic :: Text Processing :: Markup :: XML",
]

setup(
    name=NAME,
    version=VERSION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    description=DESCRIPTION,
    long_description=LONG_DESC,
    license=LICENSE,
    keywords=KEYWORDS,
    packages=[NAME],
    classifiers=CLASSIFIERS,
    **setup_kwds
)
