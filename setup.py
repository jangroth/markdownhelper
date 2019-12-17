import setuptools


setuptools.setup(
    name='MarkdownHelper',
    version='0.0.1',
    author='Jan Groth',
    author_email='jan.groth.de@gmail.com',
    description='Adds or removes tables of content (TOC) to or from markdown documents.',
    url='https://github.com/jangroth/markdownhelper',
    packages=setuptools.find_packages(),
    scripts=['bin/mdh'],
    install_requires=['click'],
    python_requires='>=3.7'
)
