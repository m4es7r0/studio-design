# tests/py/helpers.py
import os
import subprocess
import tempfile

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))


def make_client(testcase, slug='demo-client'):
    """Creates a client container from the template in a temp folder; returns its path."""
    tmp = tempfile.TemporaryDirectory()
    testcase.addCleanup(tmp.cleanup)
    env = dict(os.environ, CLIENTS_DIR=tmp.name)
    subprocess.run([os.path.join(REPO, 'scripts', 'new-client.sh'), slug, '--name', 'Demo Client', '--port', '5299'],
                   check=True, env=env, stdout=subprocess.DEVNULL)
    return os.path.join(tmp.name, slug)
