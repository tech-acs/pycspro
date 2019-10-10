import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pycspro",
    version="0.9.0",
    author="Nahom Tamerat",
    author_email="nahomt@amestsantim.com",
    description="A Python library for parsing CSPro dictionaries and cases.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/amestsantim/pycspro",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'transitions'
    ],
    python_requires='>=3.6',
)