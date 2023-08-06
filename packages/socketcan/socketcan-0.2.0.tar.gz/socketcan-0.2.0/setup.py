import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="socketcan",
    version="0.2.0",
    author="Patrick Menschel",
    author_email="menschel.p@posteo.de",
    description="A python 3 interface to socketcan",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/menschel/socketcan",
    packages=setuptools.find_packages(exclude = ['tests',]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: POSIX :: Linux",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Embedded Systems",
    ],
    python_requires=">=3.7",
    keywords="socketcan can"

)
