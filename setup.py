from setuptools import find_packages, setup

setup(
    name="bridge-config",
    version="1.5",
    description="Bridge Marketing SSM simple manager",
    url="https://github.com/BridgeMarketing/bridge-config",
    author="Bridge",
    author_email="guido.accardo@bridgecorp.com",
    license="GPL",
    long_description=open("README.md").read(),
    packages=find_packages(exclude=("tests")),
    install_requires=["boto3", "click", "terminaltables==3.1.0"],
    tests_require=[
        "isort",
        "black",
        "flake8",
        "flake8-print",
        "flake8-debugger",
        "flake8-comprehensions",
    ],
    entry_points={
        "console_scripts": [
            "bridgeconfig = bridgeconfig:cli",
        ],
    },
    zip_safe=False,
)
