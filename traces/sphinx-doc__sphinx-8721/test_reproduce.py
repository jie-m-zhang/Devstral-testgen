"""
Test to reproduce the viewcode epub issue.

This test reproduces the bug where viewcode creates pages for epub
even if viewcode_enable_epub=False.
"""

import sys
sys.path.insert(0, '/testbed')

from pathlib import Path
import tempfile
import shutil

# Test that directly checks the collect_pages function behavior
def test_viewcode_epub_disabled():
    """
    Test that collect_pages respects viewcode_enable_epub=False for epub builders.

    This test creates a minimal Sphinx project and builds it with the epub builder
    to check if module pages are created when viewcode_enable_epub=False.
    """
    # Create a temporary directory for the test
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = Path(tmpdir) / 'test_project'
        test_dir.mkdir()

        # Create conf.py
        conf_py = test_dir / 'conf.py'
        conf_py.write_text("""
extensions = ['sphinx.ext.viewcode']
viewcode_enable_epub = False
exclude_patterns = ['_build']
""")

        # Create index.rst
        index_rst = test_dir / 'index.rst'
        index_rst.write_text("""
Test Documentation
==================

.. py:module:: test_module

.. py:function:: test_function()

   This is a test function.
""")

        # Create a simple Python module
        test_module_dir = test_dir / 'test_module'
        test_module_dir.mkdir()
        init_py = test_module_dir / '__init__.py'
        init_py.write_text("""
\"\"\"Test module.\"\"\"

def test_function():
    \"\"\"This is a test function.\"\"\"
    return "test"
""")

        # Build the project with the epub builder
        from sphinx.application import Sphinx
        srcdir = str(test_dir)
        outdir = str(test_dir / '_build' / 'epub')
        doctreedir = str(test_dir / '_build' / '.doctrees')

        app = Sphinx(srcdir, srcdir, outdir, doctreedir, 'epub')

        # Build
        app.build()

        # Check that _modules directory does not exist in the epub output
        modules_dir = Path(outdir) / '_modules'

        # The bug is that modules_dir exists even though viewcode_enable_epub=False
        assert not modules_dir.exists(), (
            f"Module pages were created for epub even though viewcode_enable_epub=False. "
            f"Directory {modules_dir} should not exist."
        )

        print("Test passed - viewcode correctly respects viewcode_enable_epub=False for epub builder")

if __name__ == "__main__":
    test_viewcode_epub_disabled()