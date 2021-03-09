from setuptools import setup, find_packages

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
