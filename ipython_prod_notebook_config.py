import os
import sys

if 'PROD_NOTEBOOK_PASSWORD_HASH' not in os.environ:
    print('Please set PROD_NOTEBOOK_PASSWORD_HASH to password-protect the '
          'admin site', file=sys.stderr)
    sys.exit(2)

c = get_config()

c.NotebookApp.base_url = '/admin/'
c.NotebookApp.base_project_url = '/admin/'
c.NotebookApp.open_browser = False
c.NotebookApp.trust_xheaders = True

c.NotebookApp.port = 8888
# Since we use an nginx proxy, it MUST be at port 8888, so don't try others.
c.NotebookApp.port_retries = 0

c.NotebookApp.password = os.environ['PROD_NOTEBOOK_PASSWORD_HASH']
