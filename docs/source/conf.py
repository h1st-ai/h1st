# Configuration file for the Sphinx documentation builder.

from datetime import date
import json
import os
import sys

# include h1st package in build path
sys.path.insert(0, os.path.abspath('./../../h1st'))

PACKAGE_NAMESPACE = 'h1st'
METADATA_FILE_NAME = 'metadata.json'
_metadata = json.load(open(os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    PACKAGE_NAMESPACE,
    METADATA_FILE_NAME)))


# -- Project information

project = _metadata['project']
author = _metadata['author']
copyright = f'{date.today().year}, {author}'

release = _metadata['release']
version = _metadata['version']

master_doc = 'README'
source_suffix = '.rst'

# -- General configuration

extensions = [
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'autoapi.extension'
]

autoapi_dirs = [os.path.abspath('./../../h1st')]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
}
intersphinx_disabled_domains = ['std']

templates_path = ['_templates']

# -- Options for HTML output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_css_files = ['css/custom.css']
#html_theme = 'furo'
#html_theme_path = ['themes', '../themes']

# -- Options for EPUB output
epub_show_urls = 'footnote'
