import os, sys

# PATH is the absolute path leading to parent directory
PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, PATH)

import metrics

source_suffix = '.rst'
master_doc = 'contents'
project = 'django-site-metrics'
copyright = 'Raffaele Salmaso'
version = metrics.__version__
release = version
today_fmt = '%B %d, %Y'
add_function_parentheses = True
add_module_names = False
