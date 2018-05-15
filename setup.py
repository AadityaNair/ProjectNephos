from setuptools import setup

with open('README.md', 'r') as f:
    readme = f.read()


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
        ],
        tests_require=[
            'pytest',
            'mock',
        ],
        test_suite=None,  # TODO: Update later.
        entry_points={
            'console_scripts': ['nephos=ProjectNephos.nephos:main'],
        },
        zip_safe=False,
        include_package_data=True,
)
