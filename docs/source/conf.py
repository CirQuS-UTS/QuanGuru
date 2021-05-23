# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
from pathlib import Path
path = str(Path(os.getcwd()))
sys.path.insert(0, path)


from pygments.style import Style
from pygments.styles.autumn import AutumnStyle
from pygments.token import Keyword, Name, Comment, String, Error, Text, \
    Number, Operator, Generic, Whitespace, Punctuation, Other, Literal

# notebook customisation
# nbsphinx_prolog = """
# .. raw:: html

#     <style>
#         div.nbinput.container,
#         div.nbinput.container div.prompt,
#         div.nbinput.container div.input_area,
#         div.nbinput.container div[class*=highlight],
#         div.nbinput.container div[class*=highlight] pre,
#         div.nboutput.container,
#         div.nboutput.container div.prompt,
#         div.nboutput.container div.output_area,
#         div.nboutput.container div[class*=highlight],
#         div.nboutput.container div[class*=highlight] pre {
#             background: #282a36;
#         }

#         div.nboutput.container div[class*=highlight] pre {
#         color: #c1303c;
#         }
#     </style>

# """
class DraculaStyle(Style):

    background_color = "#282a36"
    default_style = ""

    styles = {
        Comment: "#6272a4",                         # class: 'c'
        Comment.Hashbang: "#6272a4",                # class: 'ch'
        Comment.Multiline: "#6272a4",               # class: 'cm'
        Comment.Preproc: "#ff79c6",                 # class: 'cp'
        Comment.Single: "#6272a4",                  # class: 'c1'
        Comment.Special: "#6272a4",                 # class: 'cs'

        Generic: "#f8f8f2",                         # class: 'g'
        Generic.Deleted: "#8b080b",                 # class: 'gd'
        Generic.Emph: "#f8f8f2 underline",          # class: 'ge'
        Generic.Error: "#f8f8f2",                   # class: 'gr'
        Generic.Heading: "#f8f8f2 bold",            # class: 'gh'
        Generic.Inserted: "#f8f8f2 bold",           # class: 'gi'
        Generic.Output: "#6ef5ff",                  # class: 'go'
        Generic.Prompt: "#f8f8f2",                  # class: 'gp'
        Generic.Strong: "#f8f8f2",                  # class: 'gs'
        Generic.Subheading: "#f8f8f2 bold",         # class: 'gu'
        Generic.Traceback: "#f8f8f2",               # class: 'gt'

        Error: "#f8f8f2",                           # class: 'err'

        Keyword: "#ff79c6",                         # class: 'k'
        Keyword.Constant: "#ff79c6",                # class: 'kc'
        Keyword.Declaration: "#8be9fd italic",      # class: 'kd'
        Keyword.Namespace: "#ff79c6",               # class: 'kn'
        Keyword.Pseudo: "#ff79c6",                  # class: 'kp'
        Keyword.Reserved: "#ff79c6",                # class: 'kr'
        Keyword.Type: "#8be9fd",                    # class: 'kt'

        Literal: "#f8f8f2",                         # class: 'l'
        Literal.Date: "#f8f8f2",                    # class: 'ld'

        Name: "#f8f8f2",                            # class: 'n'
        Name.Attribute: "#50fa7b",                  # class: 'na'
        Name.Builtin: "#8be9fd italic",             # class: 'nb'
        Name.Builtin.Pseudo: "#f8f8f2",             # class: 'bp'
        Name.Class: "#50fa7b",                      # class: 'nc'
        Name.Constant: "#f8f8f2",                   # class: 'no'
        Name.Decorator: "#f8f8f2",                  # class: 'nd'
        Name.Entity: "#f8f8f2",                     # class: 'ni'
        Name.Exception: "#f8f8f2",                  # class: 'ne'
        Name.Function: "#50fa7b",                   # class: 'nf'
        Name.Label: "#8be9fd italic",               # class: 'nl'
        Name.Namespace: "#f8f8f2",                  # class: 'nn'
        Name.Other: "#f8f8f2",                      # class: 'nx'
        Name.Tag: "#ff79c6",                        # class: 'nt'
        Name.Variable: "#8be9fd italic",            # class: 'nv'
        Name.Variable.Class: "#8be9fd italic",      # class: 'vc'
        Name.Variable.Global: "#8be9fd italic",     # class: 'vg'
        Name.Variable.Instance: "#8be9fd italic",   # class: 'vi'

        Number: "#bd93f9",                          # class: 'm'
        Number.Bin: "#bd93f9",                      # class: 'mb'
        Number.Float: "#bd93f9",                    # class: 'mf'
        Number.Hex: "#bd93f9",                      # class: 'mh'
        Number.Integer: "#bd93f9",                  # class: 'mi'
        Number.Integer.Long: "#bd93f9",             # class: 'il'
        Number.Oct: "#bd93f9",                      # class: 'mo'

        Operator: "#ff79c6",                        # class: 'o'
        Operator.Word: "#ff79c6",                   # class: 'ow'

        Other: "#f8f8f2",                           # class: 'x'

        Punctuation: "#f8f8f2",                     # class: 'p'

        String: "#f1fa8c",                          # class: 's'
        String.Backtick: "#f1fa8c",                 # class: 'sb'
        String.Char: "#f1fa8c",                     # class: 'sc'
        String.Doc: "#f1fa8c",                      # class: 'sd'
        String.Double: "#f1fa8c",                   # class: 's2'
        String.Escape: "#f1fa8c",                   # class: 'se'
        String.Heredoc: "#f1fa8c",                  # class: 'sh'
        String.Interpol: "#f1fa8c",                 # class: 'si'
        String.Other: "#f1fa8c",                    # class: 'sx'
        String.Regex: "#f1fa8c",                    # class: 'sr'
        String.Single: "#f1fa8c",                   # class: 's1'
        String.Symbol: "#f1fa8c",                   # class: 'ss'

        Text: "#f8f8f2",                            # class: ''

        Whitespace: "#f8f8f2"                       # class: 'w'
    }


def pygments_monkeypatch_style(mod_name, cls):
    import sys
    import pygments.styles
    cls_name = cls.__name__
    mod = type(__import__("os"))(mod_name)
    setattr(mod, cls_name, cls)
    setattr(pygments.styles, mod_name, mod)
    sys.modules["pygments.styles." + mod_name] = mod
    from pygments.styles import STYLE_MAP
    STYLE_MAP[mod_name] = mod_name + "::" + cls_name
    #print(pygments.styles)

pygments_monkeypatch_style("dracula", DraculaStyle)

# -- Project information -----------------------------------------------------

project = 'quanguru'
copyright = '2020, Cahit Kargi'
author = 'Cahit Kargi'

# The full version, including alpha/beta/rc tags
release = '1'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon',
    'sphinx.ext.mathjax',
    'sphinx.ext.imgmath',
    'sphinx.ext.viewcode',
    'sphinx.ext.extlinks',
    'sphinx_tabs.tabs',
    'jupyter_sphinx',
    'sphinx.ext.doctest',
    'sphinx_copybutton',
    'nbsphinx',
    'recommonmark',
    'IPython.sphinxext.ipython_console_highlighting'
]

copybutton_prompt_text = ">>> "

autodoc_member_order = 'bysource'
napoleon_use_param = True
nbsphinx_timeout = 60
#nbsphinx_execute = 'never'
html_sourcelink_suffix = ''
exclude_patterns = ['_build', '**.ipynb_checkpoints']

intersphinx_mapping = {'python': ('https://docs.python.org/3', None)}

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# If true, figures, tables and code-blocks are automatically numbered if they
# have a caption.
numfig = True

# A dictionary mapping 'figure', 'table', 'code-block' and 'section' to
# strings that are used for format of figure numbers. As a special character,
# %s will be replaced to figure number.
numfig_format = {
    'table': 'Table %s'
}

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# For Adding Locale
locale_dirs = ['locale/']   # path is example but recommended.
gettext_compact = False     # optional.

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# The name of the Pygments (syntax highlighting) style to use.
#pygments_style = 'dracula'

# A boolean that decides whether module names are prepended to all object names
# (for object types where a “module” of some kind is defined), e.g. for
# py:function directives.
add_module_names = False


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "pydata_sphinx_theme"

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
# html_theme_options = {
#     'logo_only': False,
#     'display_version': True,
#     'prev_next_buttons_location': 'bottom',
#     'style_external_links': False,
#     # Toc options
#     'collapse_navigation': True,
#     'sticky_navigation': True,
#     'navigation_depth': 2,
#     'includehidden': True,
#     'titles_only': False,
#     'style_nav_header_background': '#1D2951',

# }

sphinx_gallery_line_numbers = True
# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']
templates_path = ['_templates']
html_css_files = ['style.css', 'custom.css', 'gallery.css']

# html_logo = 'images/logo.png'
# html_favicon = 'images/favicon.ico'

html_last_updated_fmt = '%Y/%m/%d'

autosummary_generate = True
autosummary_generate_overwrite = False

# autodoc_default_options = {
#     'inherited-members': None,
# }
