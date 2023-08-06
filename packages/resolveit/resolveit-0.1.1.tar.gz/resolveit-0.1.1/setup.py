# following this
# https://medium.com/@thucnc/how-to-publish-your-own-python-package-to-pypi-4318868210f9

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    README = readme_file.read()

with open('HISTORY.md') as history_file:
    HISTORY = history_file.read()

setup_args = dict(
    name='resolveit',
    version='0.1.1',
    description='Resolve data schemas',
    long_description_content_type="text/markdown",
    long_description=README + '\n\n' + HISTORY,
    license='MIT',
    packages=find_packages(),
    author='David Johnston',
    author_email='dave31415@gmail.com',
    keywords=[],
    url='https://github.com/dave31415/resolveit',
    download_url='https://pypi.org/project/resolveit/'
)

install_requires = [
    'pytest',
    'numpy',
    'bokeh'
]

if __name__ == '__main__':
    setup(include_package_data=True,
          install_requires=install_requires, **setup_args)
