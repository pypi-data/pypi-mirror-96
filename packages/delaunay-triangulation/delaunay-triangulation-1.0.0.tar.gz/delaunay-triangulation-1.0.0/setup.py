import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="delaunay-triangulation",
    version="1.0.0",
    author="sleoh",
    author_email="simon.henkel@gmx.de",
    description="A lightweight collection of helper classes and methods to create a delaunay triangulation.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/sleoh/delaunay-triangulation",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)