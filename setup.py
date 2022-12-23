import os
from setuptools import setup, find_packages, Extension
from version import version

project_path = os.path.dirname(os.path.realpath(__file__))
requirements_file = '{}/requirements.txt'.format(project_path)

with open(requirements_file) as f:
    content = f.readlines()
install_requires = [x.strip() for x in content]

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="python_ms_core",
    version=version,
    author="Sujata Misra",
    author_email="sujatam@gaussiansolutions.com",
    description="Python Boilerplate with cloud interaction",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TaskarCenterAtUW/TDEI-Python-ms-core",
    install_requires=install_requires,
    packages=find_packages(where='src'),
    # packages=['python_ms_core'],
    # namespace_packages=['python_ms_core'],
    # packages={
    #     "python_ms_core": "src"
    # },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
    # ext_modules=[Extension('python_ms_core.src', ['python_ms_core.src.main'])]
    # py_modules=['python_ms_core'],
    package_dir={'': 'src'},
)
