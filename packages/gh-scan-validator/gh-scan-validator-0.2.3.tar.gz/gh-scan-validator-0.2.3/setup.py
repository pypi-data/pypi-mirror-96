import setuptools

VERSION = "0.2.3"

with open("requirements.txt", "r") as f:
    reqs = [l.replace("\n", "") for l in f.readlines()]


setuptools.setup(
    name="gh-scan-validator",
    version=VERSION,
    author="Geza Velkey",
    author_email="geza.velkey@greehill.com",
    description="greeHill TSE Scan Validator",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
    ],
    install_requires=reqs,
    python_requires=">=3.7",
)
