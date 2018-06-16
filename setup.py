from setuptools import setup
from setuptools.command.test import test as TestCommand
import sys

with open('README.md', 'r') as f:
    readme = f.read()


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to pytest")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = ''

    def run_tests(self):
        import shlex
        import pytest
        errno = pytest.main(shlex.split(self.pytest_args))
        sys.exit(errno)


setup(
        name='ProjectNephos',
        version='0.1',
        description='Record, Process and Upload TV Channels',
        long_description=readme,
        url='http://github.com/AadityaNair/ProjectNephos',
        author='AadityaNair',
        author_email='aadityanair6494+Nephos@gmail.com',
        license='GPLv2',
        packages=['ProjectNephos'],
        install_requires=[
            'google-api-python-client',
            'oauth2client',
            'ffmpy',
        ],
        tests_require=[
            'pytest',
            'mock',
        ],
        cmdclass={'test': PyTest},
        entry_points={
            'console_scripts': ['nephos=ProjectNephos.nephos:main'],
        },
        zip_safe=False,
        include_package_data=True,
)

