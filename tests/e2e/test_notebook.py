from unittest import TestCase, SkipTest
import subprocess
import os
import shutil

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor, CellExecutionError

class AutoCyberE2ETest(TestCase):
    slow = 0

    def test_e2e_autocyber_tutorial(self):
        try:
            subprocess.check_call(['ipython', '-V'])
        except:
            raise SkipTest('IPython is not installed')

        nb_file = os.path.join(os.path.dirname(__file__), "AutoCyberTutorial.ipynb")
        nb_out_file = os.path.join(os.path.dirname(__file__), "AutoCyberTutorial_output.ipynb")
        autocyber_folder = "examples/AutomotiveCybersecurity/"

        with open(nb_file) as f:
            nb = nbformat.read(f, as_version=4)

        ep = ExecutePreprocessor(timeout=600, kernel_name='python3')

        try:
            ep.preprocess(nb, {'metadata': {'path': autocyber_folder}})
        except CellExecutionError:
            out = None
            msg = 'Error executing the notebook "%s".\n\n' % nb_file
            msg += 'See notebook "%s" for the traceback.' % nb_out_file
            print(msg)
            raise
        finally:
            with open(nb_out_file, mode='w', encoding='utf-8') as f:
                nbformat.write(nb, f)        
