from setuptools import setup, find_packages

setup(
    name="crypto-evaluator",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "PyQt5>=5.15.0",
    ],
    python_requires=">=3.8",
)