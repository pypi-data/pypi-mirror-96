from distutils.core import setup
from setuptools import find_packages, Extension, Command
from Cython.Build import cythonize

import os
import sys

CLASSIFIERS = """Development Status :: 5 - Production/Stable
Operating System :: MacOS :: MacOS X
Operating System :: POSIX
Operating System :: POSIX :: Linux
Operating System :: Unix
Programming Language :: Python
Topic :: Scientific/Engineering
Topic :: Scientific/Engineering :: Bio-Informatics"""

# split into lines and filter empty ones
CLASSIFIERS = CLASSIFIERS.splitlines()

# macros = [("CYTHON_TRACE", "1")]

# if macros:
#     from Cython.Compiler.Options import get_directive_defaults
#     directive_defaults = get_directive_defaults()
#     directive_defaults['linetrace'] = True
#     directive_defaults['binding'] = True

# extension sources
macros = []

extensions = [
    Extension(
        "sorted_nearest.src.sorted_nearest",
        ["sorted_nearest/src/sorted_nearest.pyx"],
        define_macros=macros),
    Extension(
        "sorted_nearest.src.max_disjoint_intervals",
        ["sorted_nearest/src/max_disjoint_intervals.pyx"],
        define_macros=macros),
    Extension(
        "sorted_nearest.src.k_nearest", ["sorted_nearest/src/k_nearest.pyx"],
        define_macros=macros),
    Extension(
        "sorted_nearest.src.k_nearest_ties", ["sorted_nearest/src/k_nearest_ties.pyx"],
        define_macros=macros),
    Extension(
        "sorted_nearest.src.clusters", ["sorted_nearest/src/clusters.pyx"],
        define_macros=macros),
    Extension(
        "sorted_nearest.src.annotate_clusters",
        ["sorted_nearest/src/annotate_clusters.pyx"],
        define_macros=macros),
    Extension(
        "sorted_nearest.src.cluster_by", ["sorted_nearest/src/cluster_by.pyx"],
        define_macros=macros),
    Extension(
        "sorted_nearest.src.merge_by", ["sorted_nearest/src/merge_by.pyx"],
        define_macros=macros),
    Extension(
        "sorted_nearest.src.introns", ["sorted_nearest/src/introns.pyx"],
        define_macros=macros),
    Extension(
        "sorted_nearest.src.windows", ["sorted_nearest/src/windows.pyx"],
        define_macros=macros),
    Extension(
        "sorted_nearest.src.tiles", ["sorted_nearest/src/tiles.pyx"],
        define_macros=macros),
]

__version__ = open("sorted_nearest/version.py").readline().split(
    " = ")[1].replace('"', '').strip()

install_requires = ["cython", "numpy"]

setup(
    name = "sorted_nearest",
    version=__version__,
    packages=find_packages(),
    ext_modules = cythonize(extensions, language_level=3),
    install_requires = install_requires,
    description = \
    'Find nearest interval.',
    long_description = __doc__,
    author = "Endre Bakken Stovner",
    author_email='endrebak85@gmail.com',
    url = 'https://github.com/endrebak/sorted_nearest',
    license = 'New BSD License',
    classifiers = CLASSIFIERS,
    package_data={'': ['*.pyx', '*.pxd', '*.h', '*.c']},
    include_dirs=["."],
)
