import ast
import operator as op
from functools import reduce
import nbformat
import IPython
import os
import glob


_use_nb_vers = 4


def pkg_name_from_mod_name(mod_name):
    """Extract the package name from a module name."""
    return mod_name.split('.')[0]


def get_refd_pkgs(s):
    """Extract the set of packages referenced by the Python imports in a string
    of Python code.

    Does this by creating an Abstract Syntax Tree (AST) rather than by text
    search.

    Returns a set of package names.
    """
    pkgs = set()

    tree = ast.parse(s)
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

    # Use an IPythonInputSplitter to transform IPython code
    # (complete with line and cell magics) to pure Python
    s = IPython.core.inputsplitter.IPythonInputSplitter()

    # Combine the sets of packages identified per cell by
    # finding the set union (using op.__or__) of those sets
    return reduce(op.__or__,
                  (get_refd_pkgs(s.transform_cell(c.source))
                   for c in nb['cells'] if c['cell_type'] == 'code'))


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
    parser.add_argument("-o", "--req_txt_fname", type=str,
                        default='requirements.txt',
        help="Path to directory containing Jupyter (Python) Notebooks")
    args = parser.parse_args()
    gen_req_txt_for_notebooks(nbs_dir=args.nbs_dir,
                              req_txt_fname=args.req_txt_fname)


# TESTING

def test_get_pkg_name_from_mod_name():
    assert pkg_name_from_mod_name('matplotlib.pyplot') == 'matplotlib'


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
