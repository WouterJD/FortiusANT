from setuptools import setup, find_packages

setup(
    name='fortius-ant',
    version='6.5b',
    description='FortiusANT',
    author='Sebastien Laclau',
    author_email='seb.laclau@gmail.com',
    #package_dir={'fortiusant':'fortiusant'},
    packages=['fortius_ant'],
    entry_points={
        'console_scripts': [
            'fortius-ant=fortiusant.FortiusAnt:main',
        ],
    }
)
