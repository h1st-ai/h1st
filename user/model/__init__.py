# Don’t forget to import __init__

__local_dev = True

if __local_dev:
    # Include h1st/ in the system path for library imports. Will be slower.
    import sys, os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
