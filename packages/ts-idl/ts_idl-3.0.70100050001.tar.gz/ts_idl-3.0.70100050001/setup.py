import sys
import os
import setuptools

import pathlib
import glob

install_requires = []
tests_require = []
dev_requires = install_requires + tests_require + ["documenteer[pipelines]"]
tools_path = pathlib.Path(setuptools.__path__[0])
base_prefix = pathlib.Path(sys.base_prefix)
data_files_path = tools_path.relative_to(base_prefix).parents[1]
idl_files = glob.glob("idl/*.idl")

scm_version_template = """# Generated by setuptools_scm
__all__ = ["__version__"]

__version__ = "{version}"
"""


def local_scheme(version):
    sal_version = (
        os.environ.get("TS_SAL_VERSION", "0")
        .strip("v")
        .replace("pre", "")
        .split("_")[0]
    )
    xml_version = os.environ.get("TS_XML_VERSION", "0").strip("v")

    hash = [f"{int(v):02}" for v in f"{xml_version}.{sal_version}".split(".")]
    hash_str = ""
    for h in hash:
        hash_str += h
    return hash_str


setuptools.setup(
    name="ts_idl",
    description="Contains helper functions for the generated idl library by ts_sal.",
    # install_requires=install_requires,
    package_dir={"": "python"},
    use_scm_version={
        "write_to": "python/lsst/ts/idl/version.py",
        "write_to_template": scm_version_template,
        "local_scheme": local_scheme,
    },
    packages=setuptools.find_namespace_packages(where="python"),
    data_files=[(os.path.join(data_files_path, "idl"), idl_files)],
    include_package_data=True,
    # scripts=[],
    # tests_require=tests_require,
    extras_require={"dev": dev_requires},
    license="GPL",
    project_url={
        "Bug Tracker": "https://jira.lsstcorp.org/secure/Dashboard.jspa",
        "Source Code": "https://github.com/lsst-ts/ts_idl",
    },
)
