from setuptools import find_packages, setup
import os

with open(os.path.join(os.path.dirname(__file__), 'yaplee', '__init__.py')) as init_file:
    for line in init_file.read().splitlines():
        if(line.lower().startswith('__version__')):
            exec(line)

setup(
    name="Yaplee",
    version=str(__version__),
    description="Yaplee is a fun and simple python framework to build user interfaces on web pages",
    url="https://github.com/YapleeProject",
    author='Matin Najafi',
    author_email="matinnajafi.dev@gmail.com",
    license="MIT",
    include_package_data=True,
    long_description='Yaplee is a Powerful, Fun and Open Souce MIT-Licenced project for front-end programming in Python. Yaplee framework is very simple and does not have complicated details.',
    long_description_content_type="text/markdown",
    install_requires=['bs4'],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'yaplee = yaplee.main:Yaplee_Main'
        ]
    },
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    python_requires='>=3.6',
    zip_safe=False
)