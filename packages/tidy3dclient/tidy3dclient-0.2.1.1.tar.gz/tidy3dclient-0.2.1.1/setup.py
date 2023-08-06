from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

version = '0.2.1.1'
setup(
    name='tidy3dclient',
    version=version,
    description='A Python API for Tidy3D FDTD Solver',
    author='FlexCompute, Inc.',
    author_email='lei@flexcompute.com',
    long_description='README.md',
    packages=find_packages(),
    install_requires=['aws-requests-auth', 'bcrypt'] + requirements,
    dependency_links=['http://github.com/flexcompute/warrant/tarball/master#egg=warrant-0.6.4'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6'
)
