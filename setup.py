from setuptools import find_packages
from setuptools import setup

setup(
    name='traffic-light',
    version='1.0',
    packages=find_packages(),
    install_requires=[
        'SQLAlchemy',
        'Flask',
        'Flask-SQLAlchemy',
        'Flask-Testing',
    ],
    entry_points={
        'console_scripts': [
            'traffic-light = traffic_light.runserver:main'
        ]
    },
    test_suite='tests',
    # long_description=open(join(dirname(__file__), 'README.txt')).read(),
)
