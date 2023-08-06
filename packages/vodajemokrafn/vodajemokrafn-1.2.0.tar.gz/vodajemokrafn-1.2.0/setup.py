import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="vodajemokrafn",
    version="1.2.0",
    author="Kojofix",
    author_email="kojofix@equalggz.eu",
    description="Voda API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://kojofix.equalggz.eu",
    packages=["vodajemokra","vodajemokra.ext.commands"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
