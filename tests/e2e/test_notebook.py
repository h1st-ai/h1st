from unittest import TestCase, SkipTest
import subprocess
import os
import shutil

class ForecastE2ETest(TestCase):
    slow = 1

    def test_e2e_forecast(self):
        try:
            subprocess.check_call(['ipython', '-V'])
        except:
            raise SkipTest('IPython is not installed')

        nb_folder = "examples/Forecasting/notebooks"

        # prepare the data
        if not os.path.exists(nb_folder + "/data/train.csv"):
            subprocess.check_call(
                "mkdir -p data; cd data; curl -LO https://arimo-public-data.s3.amazonaws.com/rossmann-store-sales.tgz; tar -xf rossmann-store-sales.tgz",
                shell=True,
                cwd=nb_folder
            )

        subprocess.check_call(
            ['ipython', 'forecast_v1_it.ipynb'],
            cwd=nb_folder,
        )

class AutoCyberE2ETest(TestCase):
    slow = 0

    @SkipTest
    def test_e2e_autocyber_tutorial(self):
        try:
            subprocess.check_call(['ipython', '-V'])
        except:
            raise SkipTest('IPython is not installed')

        nb_file = os.path.join(os.path.dirname(__file__), "AutoCyberTutorial.ipynb")
        nb_folder = "examples/AutomotiveCybersecurity/notebooks"

        shutil.copy2(nb_file, nb_folder)

        try:

            subprocess.check_call(
                ['ipython', nb_file],
                cwd=nb_folder,
            )
        finally:
            # not to make this tutorial folder dirty
            os.unlink(os.path.join(nb_folder, "AutoCyberTutorial.ipynb"))
