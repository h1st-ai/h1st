import os
from setuptools import find_namespace_packages, setup
from setuptools.command.install import install


def __read_requirement(type=None):
    filename = 'h1st/requirements%s.txt' % (".%s" % type if type else "")
    with open(filename, encoding='utf8') as f:
        return f.readlines()


def __read_version():
    return '2021.06'


with open(os.path.join(os.path.dirname(__file__), '.', 'README.md'), 'r', encoding='utf8') as f:
    long_description = f.read()


setup(
    cmdclass={'install': install},
    name='h1st',
    version=__read_version(),
    author='Arimo',
    author_email='admin@arimo.com',
    namespace_packages=['h1st'],
    packages=find_namespace_packages(include=['h1st.*']),
    include_package_data=True,
    zip_safe=False,
    url='https://h1st.ai',
    license='Apache 2.0',
    description='Human-First AI (H1ST)',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=__read_requirement(),
    python_requires='>= 3',
    entry_points="""
    [console_scripts]
    h1=h1st.cli:main
    """,
    extras_require={}
)
