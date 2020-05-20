import codecs
import sys

from setuptools import setup


def long_description():
    try:
        return codecs.open('README.md', 'r', 'utf-8').read()
    except IOError:
        return 'Long description error: Missing README.rst file'


description = (
    'Simple framework for building Instagram chat bots '
    'with menu driven interface'
)

if sys.version_info < (3, 6):
    sys.exit('instachatbot requires Python >=3.6')

setup(
    name='instachatbot',
    description=description,
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    keywords='chatbot, instagram',
    author='Artem Vasilyev',
    author_email='artem.v.vasilyev@gmail.com',
    long_description=long_description(),
    long_description_content_type='text/markdown',
    url='https://github.com/art-vasilyev/instachatbot',
    packages=['instachatbot'],
    python_requires=">=3.6",
    platforms=['any'],
    license='MIT',
    install_requires=[
        'instabot>=0.78'
    ]
)
