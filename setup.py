import pathlib

from setuptools import setup

here = pathlib.Path(__file__).parent.resolve()
# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    # $ pip install sampleproject https://pypi.org/project/sampleproject/
    name="socialetl",
    version="0.1",
    description="Extract transform and load for the project of 2022 Social Network Analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gatto/ds-network-analysis",
    author="Fabio Michele Russo",
    classifiers=[
        # 3 - Alpha, 4 - Beta, 5 - Production/Stable
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        # Specify the Python versions you support here. In particular, ensure that you indicate you support Python 3. These classifiers are *not* checked by 'pip install'. See instead 'python_requires' below.
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords="datascience, extract, etl",
    package_dir={"socialetl": "src"},
    packages=["socialetl"],
    python_requires=">=3.7, <4",
    install_requires=["pandas", "attrs", "scikit-learn"],
    # If there are data files included in your packages that need to be
    # installed, specify them here.
    package_data={
        "socialetl": ["data/*.csv"],
    },
    project_urls={
        "Bug Reports": "https://github.com/gatto/ds-network-analysis/issues",
        "Source": "https://github.com/gatto/ds-network-analysis/",
    },
)
