import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="quantumSoup",
    version="1.0.0",
    author="Hunter Matuse",
    author_email="hmatuse@advancingsimple.com",
    description="A Python API to Canary Lab's historian web services.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/huntermatuse/quantumSoup",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'ciso8601',
        'arrow',
        'urllib3',
        'requests'
    ]
)