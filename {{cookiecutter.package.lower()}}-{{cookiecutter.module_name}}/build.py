"""Python->C++ package build."""
import os
import shutil
from distutils.command.build_ext import build_ext
from distutils.core import Distribution, Extension

from Cython.Build import cythonize

compile_args = ["-march=native", "-O3", "-msse", "-msse2", "-mfma", "-mfpmath=sse"]
link_args = []
include_dirs = []
libraries = ["m"]


def build():
    """Build function."""
    extensions = [
        Extension(
            "*",
            [], # Add your files to cythonize in this list
            extra_compile_args=compile_args,
            extra_link_args=link_args,
            include_dirs=include_dirs,
            libraries=libraries,
        )
    ]
    ext_modules = cythonize(
        extensions,
        include_path=include_dirs,
        compiler_directives={"binding": True, "language_level": 3, "linetrace": True},
    )

    distribution = Distribution({"name": "extended", "ext_modules": ext_modules})
    distribution.package_dir = "extended"

    cmd = build_ext(distribution)
    cmd.ensure_finalized()
    cmd.run()

    # Copy built extensions back to the project
    for source, output in zip(cmd.get_source_files(), cmd.get_outputs()):
        so_file = os.path.relpath(output, cmd.build_lib)
        relative_path = so_file
        print(output, relative_path)
        shutil.copyfile(output, relative_path)
        mode = os.stat(relative_path).st_mode
        mode |= (mode & 0o444) >> 2
        os.chmod(relative_path, mode)


if __name__ == "__main__":
    build()
