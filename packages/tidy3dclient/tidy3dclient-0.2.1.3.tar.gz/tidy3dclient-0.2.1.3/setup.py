from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

with open('README.md', 'r') as f:
    readme = f.read()

version = '0.2.1.3'
setup(
    name='tidy3dclient',
    version=version,
    description='A Python API for Tidy3D FDTD Solver',
    author='FlexCompute, Inc.',
    author_email='lei@flexcompute.com',
    long_description=readme,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=['aws-requests-auth', 'bcrypt'] + requirements,
    dependency_links=['http://github.com/flexcompute/warrant/tarball/master#egg=warrant-0.6.4'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6'
)
