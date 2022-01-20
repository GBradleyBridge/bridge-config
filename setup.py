from setuptools import find_packages, setup

setup(
    name="bridge-config",
    version="1.7.3",
    description="Bridge Marketing SSM simple manager",
    url="https://github.com/BridgeMarketing/bridge-config",
    author="Bridge",
    author_email="guido.accardo@bridgecorp.com",
    license="GPL",
    long_description=open("README.md").read(),
    packages=find_packages(exclude=("tests")),
    install_requires=[
        "boto3>=1.10.*",
        "click==7.1.*",
        "terminaltables==3.1.*",
        "dynaconf==2.2.*",
        "toml>=0.10.*",
        "termcolor==1.1.0",
    ],
    extras_require={
        "tests": [
            "isort",
            "black",
            "flake8",
            "flake8-print",
            "flake8-debugger",
            "flake8-comprehensions",
            "nose",
        ],
    },
    entry_points={
        "console_scripts": [
            "bridgeconfig = bridgeconfig:cli",
        ],
    },
    zip_safe=False,
)
