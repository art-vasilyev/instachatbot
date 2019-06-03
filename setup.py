from setuptools import setup, find_packages

import instachatbot

setup(
    name='instachatbot',
    version=instachatbot.version,
    packages=find_packages(),
    install_requires=[
        'instabot>=0.41'
    ]
)
