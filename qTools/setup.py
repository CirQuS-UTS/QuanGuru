from setuptools import setup, find_packages  # type: ignore

setup(
    name="qsims",
    version="0.0.1",
    packages=find_packages(),
    author="CirQuS Team",
    include_package_data=True,
    python_requires=">=3.5"
)
