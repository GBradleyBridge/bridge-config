from setuptools import find_packages, setup

<<<<<<< HEAD
setup(
    name="bridge-config",
    version="1.7",
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
||||||| 3f561b7
setup(name='bridge-config',
      version='1.4',
      description='Bridge Marketing SSM simple manager',
      url='https://github.com/BridgeMarketing/bridge-config',
      author='Bridge',
      author_email='guido.accardo@bridgecorp.com',
      license='GPL',
      long_description=open('README.md').read(),
      packages=find_packages(exclude=('tests')),
      install_requires=['boto3'],
      #tests_require=['mock', 'nose', 'requests-mock'],
      zip_safe=False)
=======
setup(name='bridge-config',
      version='1.5',
      description='Bridge Marketing SSM simple manager',
      url='https://github.com/BridgeMarketing/bridge-config',
      author='Bridge',
      author_email='guido.accardo@bridgecorp.com',
      license='GPL',
      long_description=open('README.md').read(),
      packages=find_packages(exclude=('tests')),
      install_requires=['boto3'],
      #tests_require=['mock', 'nose', 'requests-mock'],
      zip_safe=False)
>>>>>>> 59c955fa82c8a095945f2550e1655cd5f44bc106
