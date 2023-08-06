import codecs
import os

from setuptools import find_packages, setup

VERSION = "0.0.3"
AUTHOR = "Free Law Project"
EMAIL = "info@free.law"
HERE = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    """
    Build an absolute path from *parts* and and return the contents of the
    resulting file.  Assume UTF-8 encoding.
    """
    with codecs.open(os.path.join(HERE, *parts), "rb", "utf-8") as file:
        return file.read()


reqs_path = HERE + "/requirements.txt"
with open(reqs_path) as reqs_file:
    reqs = reqs_file.read().splitlines()


setup(
    name="bankruptcy",
    description="A bankruptcy document parser.",
    license="BSD",
    url="https://github.com/freelawproject/bankruptcy-parser",
    version=VERSION,
    author=AUTHOR,
    author_email=EMAIL,
    maintainer=AUTHOR,
    maintainer_email=EMAIL,
    keywords=["legal", "document", "bankruptcy", "PDF", "form"],
    long_description=read("README.rst"),
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    install_requires=reqs,
    test_suite="tests",
)
