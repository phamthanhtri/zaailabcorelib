from distutils.core import setup
import setuptools
def parse_requirements(filename):
    """ load requirements from a pip requirements file """
    lineiter = (line.strip() for line in open(filename))
    return [line for line in lineiter if line and not line.startswith("#")]


install_reqs = parse_requirements("requirements.txt")

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="zaailabcorelib",
    version="0.2.1.2",
    author="ailabteam",
    include_package_data=True,
    description="A useful tools inside ZAI Lab",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    tests_require=["pytest", "mock"],
    test_suite="pytest",
    install_requires=install_reqs,
)
