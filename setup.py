import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tjur",
    version="0.0.1",
    author="80-am",
    author_email="adam@flonko.com",
    description="A trading bot",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/80-am/tjur",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",  # nopep8
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
