"""
    Resets to default settings for matplotlib, 
    undoing any previous setting changes from package imports.
    This module is automatically imported when quanguru.classes is imported.
"""

from matplotlib_inline.backend_inline import set_matplotlib_formats
set_matplotlib_formats("png")
