from setuptools import setup, find_packages


VERSION = '0.0.9'
DESCRIPTION = 'print words'
LONG_DESCRIPTION = 'A package that allows you to print words easily'

# Setting up
setup(
    name="Printerpackage",
    version=VERSION,
    author="Asher Thomas",
    author_email="achutomonline@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description="long_description",
    packages=find_packages(),
    install_requires=['python'],
    keywords=['printer', 'words', 'hello'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)