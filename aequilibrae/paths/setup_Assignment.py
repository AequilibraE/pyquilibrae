import os
import sys
import platform
import numpy as np
import pyarrow as pa
import Cython.Compiler.Options
from Cython.Distutils import build_ext
from Cython.Build import cythonize
import shutil

# Cython.Compiler.Options.annotate = True

try:
    from setuptools import setup
    from setuptools import Extension
except ImportError:
    from distutils.core import setup
    from distutils.extension import Extension

sys.dont_write_bytecode = True

if "WINDOWS" in platform.platform().upper():
    ext_modules = [
        Extension(
            "AoN",
            ["AoN.pyx"],
            extra_compile_args=["/openmp", "/O2"],
            extra_link_args=["/openmp"],
            include_dirs=[np.get_include(), pa.get_include()],
            language="c++",
            libraries=pa.get_libraries(),
            library_dirs=pa.get_library_dirs(),
            runtime_library_dirs=pa.get_library_dirs(),
        )
    ]
else:
    ext_modules = [
        Extension(
            "AoN",
            ["AoN.pyx"],
            extra_compile_args=["-fopenmp", "-std=c++11", "-O3"],  # do we want -Ofast?
            extra_link_args=["-fopenmp"],
            include_dirs=[np.get_include(), pa.get_include()],
            language="c++",
            libraries=pa.get_libraries(),
            library_dirs=pa.get_library_dirs(),
            runtime_library_dirs=pa.get_library_dirs(),
            define_macros=("_GLIBCXX_USE_CXX11_ABI", "0"),
        )
    ]
    # I got inexplicable segfaults without the following line, see
    # https://arrow.apache.org/docs/python/extending.html# (see end of doc)
#     ext_modules[0].define_macros.append(("_GLIBCXX_USE_CXX11_ABI", "0"))
#
#
# for ext in ext_modules:
#     ext.libraries.extend(pa.get_libraries())
#     ext.library_dirs.extend(pa.get_library_dirs())
#     ext.runtime_library_dirs.extend(pa.get_library_dirs())

setup(name="AoN", ext_modules=cythonize(ext_modules))
