from setuptools import setup, find_packages

with open("README.md", "r") as readme_file:
    readme = readme_file.read()

with open("requirements.txt", "r") as requirements:
    requirements = requirements.readlines()
    requirements = [req.strip() for req in requirements]

VERSION = (0, 0, 1)
__version__ = VERSION
__versionstr__ = '.'.join(map(str, VERSION))


setup(
    name="robotac",
    version=__versionstr__,
    author="ICEYE-SOFTWARE_QA",
    author_email="",
    description="Robot test case integration tool",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="",
    install_requires=requirements,
    license='MIT',
    packages=find_packages(),
    package_data={'robotac': ['modules/*']},
    include_package_data=True,
    # Checks MANIFEST.in for explicit rules
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS independent"
    ],
    python_requires='>=3.8',
    scripts=['./bin/robotac-tr'],
)
