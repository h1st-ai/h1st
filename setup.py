import json
from pathlib import Path
from setuptools import find_namespace_packages, setup


H1ST_PACKAGE_NAME = 'h1st'


current_dir_path = Path(__file__).parent

metadata = json.load(open(current_dir_path /
                          H1ST_PACKAGE_NAME /
                          'metadata.json'))

with open(current_dir_path / 'README.md', encoding='utf8') as f:
    long_description = f.read()

with open(current_dir_path / H1ST_PACKAGE_NAME /
          'requirements.txt') as f:
    requirements = f.readlines()

with open(current_dir_path / H1ST_PACKAGE_NAME /
          'django' / 'requirements.txt') as f:
    django_requirements = f.readlines()


setup(
    name=metadata['PACKAGE'],
    version=metadata['VERSION'],
    description=metadata['DESCRIPTION'],
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=metadata['AUTHOR'],
    url=metadata['URL'],
    download_url=metadata['DOWNLOAD_URL'],
    packages=find_namespace_packages(include=[f'{H1ST_PACKAGE_NAME}.*']),
    scripts=['h1st/django/util/cli/h1st',
             'h1st/django/util/cli/aws-eb/h1st-aws',
             'h1st/django/util/cli/clone-template/h1st-clone',
             'h1st/django/util/cli/clone-template/h1st-templates'],
    classifiers=metadata['CLASSIFIERS'],
    license='Apache 2.0',
    keywords=metadata['KEYWORDS'],
    include_package_data=True,
    zip_safe=False,
    install_requires=requirements,
    entry_points="""
    [console_scripts]
    h1=h1st.cli:main
    """,
    extras_require=dict(django=django_requirements),
    python_requires='>= 3.7',
    namespace_packages=[H1ST_PACKAGE_NAME]
)
