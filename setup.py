from setuptools import setup, find_packages

setup(
    name="dwlabbackup",
    version="0.6.1",
    packages=find_packages(),
    scripts=[],
    install_requires=["dwlabbasicpy>=0.6.1"],
)
