# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

import os
import sys
sys.path.insert(0, os.path.abspath('..'))

# Import the package to get version
try:
    import ncbi_client
    version = ncbi_client.__version__
    release = version
except ImportError:
    version = "1.0.0"
    release = "1.0.0"

# -- Project information -----------------------------------------------------

project = 'NCBI Client'
copyright = '2024, NCBI Client Contributors'
author = 'NCBI Client Contributors'

# The full version, including alpha/beta/rc tags
# version and release are set above

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'sphinx.ext.coverage',
    'sphinx.ext.doctest',
    'myst_parser',
    'sphinx_rtd_theme',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# The suffix(es) of source filenames.
source_suffix = {
    '.rst': None,
    '.md': None,
}

# The master toctree document.
master_doc = 'index'

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = 'sphinx_rtd_theme'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
html_theme_options = {
    'canonical_url': '',
    'analytics_id': '',  # Google Analytics ID
    'logo_only': False,
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': False,
    'vcs_pageview_mode': '',
    'style_nav_header_background': '#2980B9',
    # Toc options
    'collapse_navigation': True,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Custom CSS files
html_css_files = [
    'custom.css',
]

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
# html_logo = '_static/logo.png'

# The name of an image file (relative to this directory) to use as a favicon of
# the docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
# html_favicon = '_static/favicon.ico'

# -- Extension configuration -------------------------------------------------

# -- Options for autodoc extension ------------------------------------------

# This value selects what content will be inserted into the main body of an
# autoclass directive.
autoclass_content = 'both'

# This value is a list of autodoc directive flags that should be automatically
# applied to all autodoc directives.
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}

# -- Options for napoleon extension -----------------------------------------

# Enable parsing of Google style docstrings
napoleon_google_docstring = True

# Enable parsing of NumPy style docstrings
napoleon_numpy_docstring = True

# Include init docstrings in class docstring
napoleon_include_init_with_doc = False

# Include private members (like _private_method) in documentation
napoleon_include_private_with_doc = False

# Include special members (like __special_method__) in documentation
napoleon_include_special_with_doc = True

# Use the .. admonition:: directive for sections
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False

# Use the .. code-block:: directive for examples
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True

# -- Options for intersphinx extension --------------------------------------

# Links to other project documentations
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'requests': ('https://docs.python-requests.org/en/stable/', None),
    'click': ('https://click.palletsprojects.com/en/8.1.x/', None),
    'pandas': ('https://pandas.pydata.org/docs/', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'matplotlib': ('https://matplotlib.org/stable/', None),
}

# -- Options for myst extension ---------------------------------------------

# Enable specific MyST features
myst_enable_extensions = [
    "amsmath",
    "colon_fence", 
    "deflist",
    "dollarmath",
    "fieldlist",
    "html_admonition",
    "html_image",
    "linkify",
    "replacements",
    "smartquotes",
    "strikethrough",
    "substitution",
    "tasklist",
]

# URL schemes that will be recognised as external URLs in Markdown files
myst_url_schemes = ("http", "https", "mailto", "ftp")

# -- Options for coverage extension -----------------------------------------

# List of modules to be covered by the coverage extension
coverage_modules = ['ncbi_client']

# -- Custom configuration ---------------------------------------------------

# Add custom roles and directives
def setup(app):
    """Setup function for custom Sphinx configuration."""
    app.add_css_file('custom.css')
    
    # Add custom roles
    app.add_role('py:mod', lambda name, rawtext, text, lineno, inliner, options={}, content=[]: 
                 inliner.problematic(rawtext, rawtext, ValueError("py:mod role not implemented")))

# -- Build configuration ----------------------------------------------------

# Suppress warnings
suppress_warnings = ['myst.header']

# Configure autosummary
autosummary_generate = True

# HTML output options
html_show_sourcelink = True
html_show_sphinx = True
html_show_copyright = True

# LaTeX output options  
latex_elements = {
    'papersize': 'letterpaper',
    'pointsize': '10pt',
    'preamble': '',
    'fncychap': '',
    'maketitle': '\\sphinxmaketitle',
    'printindex': '\\footnotesize\\raggedright\\printindex',
}

# Grouping the document tree into LaTeX files
latex_documents = [
    (master_doc, 'ncbi-client.tex', 'NCBI Client Documentation',
     'NCBI Client Contributors', 'manual'),
]

# EPUB options
epub_title = project
epub_author = author
epub_publisher = author
epub_copyright = copyright

# The basename for the epub file. It defaults to the project name.
epub_basename = 'ncbi-client'

# Manual page output
man_pages = [
    (master_doc, 'ncbi-client', 'NCBI Client Documentation',
     [author], 1)
]

# Texinfo output
texinfo_documents = [
    (master_doc, 'ncbi-client', 'NCBI Client Documentation',
     author, 'ncbi-client', 'Python client for NCBI databases.',
     'Miscellaneous'),
]
