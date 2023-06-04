from glob import glob
from os.path import basename
from os.path import splitext
from setuptools import find_packages
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="falcon-fdr-dictionary",
    version="0.0.4",
    author="CrowdStrike",
    description="Script to retrieve the FDR event dictionary from the CrowdStrike API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cs-shadowbq/fdr-event-dictionary",
    packages=find_packages("."),
    package_dir={"": "."},
    py_modules=[splitext(basename(path))[0] for path in glob("*.py")],
    include_package_data=True,
    install_requires=[
        'json',
        'requests',
        'crowdstrike-falconpy'
    ],
    extras_require={
        'devel': [
            'flake8',
            'pylint',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: Unix",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: The Unlicense (Unlicense)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
