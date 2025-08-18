from setuptools import setup, find_packages

setup(
    name="dwlab_backup",
    version="0.6.1",
    packages=find_packages(),
    scripts=[],
    install_requires=["dwlab-basicpy>=0.6.1"],
)
