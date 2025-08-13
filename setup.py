from setuptools import setup, find_packages

setup(
    name="dwlab_backup",
    version="0.06.01",
    packages=find_packages(),
    scripts=[],
    install_requires=["dwlab_basicpy>=0.06.01"],
)
