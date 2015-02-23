import os


c = get_config()
c.FileNotebookManager.hide_globs = ['__pycache__', 'node_modules', 'output']

if 'PROD_NOTEBOOK' in os.environ:
    curdir = os.path.dirname(__file__)
    prod_cfg_path = os.path.join(curdir, 'ipython_prod_notebook_config.py')
    load_subconfig(prod_cfg_path)
