import codecs

from setuptools import setup
import instachatbot


def long_description():
    try:
        return codecs.open('README.md', 'r', 'utf-8').read()
    except IOError:
        return 'Long description error: Missing README.rst file'


description = (
    'Simple framework for building Instagram chat bots '
    'with menu driven interface'
)

setup(
    name='instachatbot',
    description=description,
    keywords='chatbot, instagram',
    author='Artem Vasilyev',
    author_email='artem.v.vasilyev@gmail.com',
    long_description=long_description(),
    long_description_content_type='text/markdown',
    url='https://github.com/art-vasilyev/instachatbot',
    version=instachatbot.__version__,
    packages=['instachatbot'],
    python_requires=">=3.5",
    platforms=['any'],
    license='MIT',
    install_requires=[
        'instabot>=0.41'
    ]
)
