from setuptools import setup, find_packages


with open("README.md", "r") as readme:
    long_description = readme.read()

setup(
    name="autoconfiguration",
    version="2.3.2",
    author="Konstantin Müller",
    author_email="konstantin.mueller.dev@gmail.com",
    description="Load configuration files (.ini) automatically",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/konstantin-mueller/python-autoconfiguration",
    download_url="https://gitlab.com/konstantin-mueller/python-autoconfiguration",
    project_urls={
        "repository": "https://gitlab.com/konstantin-mueller/python-autoconfiguration",
        "bugs": "https://gitlab.com/konstantin-mueller/python-autoconfiguration/issues",
    },
    license="Apache License 2.0",
    packages=find_packages(),
    package_data={
        "": ["LICENSE", "README.md"],
        "autoconfiguration": ["*.py", "py.typed"],
    },
    include_package_data=True,
    classifiers=[
        "Topic :: Software Development :: Libraries",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3 :: Only",
    ],
    python_requires=">=3.8,<4",
)
