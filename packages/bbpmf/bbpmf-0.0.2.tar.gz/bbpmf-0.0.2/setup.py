import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='bbpmf',
    version='0.0.2',
    author='Anthony Aylward',
    author_email='aaylward@eng.ucsd.edu',
    description='Probability mass function for a beta-binomial distribution',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/anthony-aylward/bbpmf.git',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    install_requires=['scipy']
)
