import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="wb_harmonize-btrx-kanderson",
    version="0.0.1",
    author="Kevin Anderson",
    author_email="kevin.anderson@neumoratx.com",
    description="A package to make surface conversions easy and fast.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/btrx-kanderson/wb_harmonize",
    project_urls={
        "Bug Tracker": "https://github.com/btrx-kanderson/wb_harmonize",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)