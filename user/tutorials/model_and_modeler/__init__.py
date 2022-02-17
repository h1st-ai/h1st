import sys
import os

__cur = __file__
while os.path.basename(__cur) != "h1st":
    __cur = os.path.dirname(__cur)
sys.path.append(__cur)

