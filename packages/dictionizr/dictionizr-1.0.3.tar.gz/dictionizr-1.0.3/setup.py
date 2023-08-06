import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dictionizr",
    version="1.0.3",
    author="Joseph Riddle",
    author_email="joeriddles10@gmail.com",
    description="A small package to convert custom python objects to dictionaries and back again",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/joeriddles/dictionizr",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    python_requires='>=3.6',
)