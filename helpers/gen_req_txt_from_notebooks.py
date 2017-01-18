import ast
import operator as op
from functools import reduce
import nbformat
import os
import glob


_use_nb_vers = 4


def pkg_name_from_mod_name(mod_name):
    """Extract the package name from a module name."""
    return mod_name.split('.')[0]


def remove_ipy_magic_lines(code_cell_str):
    """Remove IPython 'magic' lines from a Python code snipped."""
    return os.linesep.join([s for s in code_cell_str.splitlines()
                            if s.strip() and s.strip()[0] != '%'])


def get_refd_pkgs(s):
    """Extract the set of packages referenced by the Python imports in a string ofo Python code.

    Does this by creating an Abstract Syntax Tree (AST) rather than by text search.

    Returns a set of package names.
    """
    tree = ast.parse(remove_ipy_magic_lines(s))
    pkgs = set()
    for node in tree.body:
        if isinstance(node, ast.ImportFrom):
            pkgs.add(pkg_name_from_mod_name(node.module))
        elif isinstance(node, ast.Import):
            pkgs.update(pkg_name_from_mod_name(n.name) for n in node.names)
    return set(pkgs)


def get_pkgs_used_in_notebook(nb_path):
    """Get the set of Python packages referenced by a Jupyter Notebook.

    Returns a set of package names.
    """
    nb = nbformat.read(nb_path, as_version=_use_nb_vers)
    assert nb['metadata']['language_info']['name'] == 'python'
    return reduce(op.__or__,
                  (get_refd_pkgs(c.source)
                   for c in nb['cells']
                   if c['cell_type'] == 'code'))


def gen_req_txt_for_notebooks(nbs_dir='.', req_txt_fname='requirements.txt'):
    """Generate a pip requirements file for all Notebooks in a directory."""
    nb_fnames = glob.glob(os.path.join(nbs_dir, r'*ipynb'))
    pkgs = set()
    for nb_fname in nb_fnames:
        with open(nb_fname, 'r') as f:
            pkgs |= get_pkgs_used_in_notebook(nb_fname)
    req_txt = os.linesep.join(sorted(pkgs))
    with open(req_txt_fname, 'w') as f:
        f.write(req_txt)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--nbs_dir", type=str, default='.',
                        help="Path to directory containing Jupyter (Python) Notebooks")
    parser.add_argument("-o", "--req_txt_fname", type=str, default='requirements.txt',
                        help="Path to directory containing Jupyter (Python) Notebooks")
    gen_req_txt_for_notebooks(nbs_dir=parser.nbs_dir, req_txt_fname=parser.req_txt_fname)


### TESTING ###

def test_get_pkg_name_from_mod_name():
    assert pkg_name_from_mod_name('matplotlib.pyplot') == 'matplotlib'


def test_remove_ipy_magic_lines():
    code_cell_str = "%matplotlib\na=3\nb=3\nc=5"
    assert remove_ipy_magic_lines(code_cell_str) == 'a=3\nb=3\nc=5'


def test_get_refd_pkgs():
    code_string = "a = 3; b = 5; a + b; import numpy as np; from scipy import *; import matplotlib.pyplot"
    pkgs = set(('matplotlib', 'numpy', 'scipy'))
    assert get_refd_pkgs(code_string) == pkgs


def test_no_imports():
    code_string = "a = 3; b = 5"
    pkgs = set()
    assert get_refd_pkgs(code_string) == pkgs


def test_commented_imports():
    code_string = "a = 3; b = 5;#import blah"
    pkgs = set()
    assert get_refd_pkgs(code_string) == pkgs
