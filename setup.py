from setuptools import setup
import instachatbot

setup(
    name='instachatbot',
    version=instachatbot.__version__,
    packages=['instachatbot'],
    install_requires=[
        'instabot>=0.41'
    ]
)
