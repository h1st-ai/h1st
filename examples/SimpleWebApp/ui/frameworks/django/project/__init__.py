# H1st customizations
import sys,os

def _set_project_root():
    ui_project_root = os.path.dirname(__file__)
    while True:
        base = os.path.basename(ui_project_root)
        if (base == 'ui'):
            sys.path.append(os.path.dirname(ui_project_root))
            break
        else:
            ui_project_root = os.path.dirname(ui_project_root)
            if (ui_project_root == "/"):
                break

_set_project_root()