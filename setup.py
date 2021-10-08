from setuptools import find_packages, setup

with open('CHANGELOG.md', 'r') as fh:
    for line in fh.readlines():
        if 'Current Version: ' in line:
            version = line.replace('Current Version: ', '')
            break

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fh:
    requirements = fh.readlines()

with open("dev_requirements.txt", "r") as fh:
    dev_requirements = fh.readlines()

setup(
    name="thsl",
    version=version,
    description="Typed Human-friendly Serialization Language",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Anthony Post",
    author_email="postanthony3000@gmail.com",
    license="MIT License",
    url="https://github.com/Ayehavgunne/thsl/",
    packages=find_packages(),
    install_requires=requirements,
    extras_require={"dev": dev_requirements},
    python_requires=">=3.10",
)
