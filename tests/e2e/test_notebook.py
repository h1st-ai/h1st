from unittest import TestCase, SkipTest
import subprocess
import os
import shutil

class AutoCyberE2ETest(TestCase):
    slow = 0

    def test_e2e_autocyber_tutorial(self):
        try:
            subprocess.check_call(['ipython', '-V'])
        except:
            raise SkipTest('IPython is not installed')

        nb_file = os.path.join(os.path.dirname(__file__), "AutoCyberTutorial.ipynb")
        nb_folder = "examples/AutoCyber/"

        shutil.copy2(nb_file, nb_folder)

        try:

            subprocess.check_call(['ipython', "AutoCyberTutorial.ipynb"], cwd=nb_folder)
        finally:
            # not to make this tutorial folder dirty
            os.unlink(os.path.join(nb_folder, "AutoCyberTutorial.ipynb"))
