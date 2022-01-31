#!/bin/bash
if [ ! -d build/html ] ; then
    make html
fi
  
(cd build/html && python -m http.server)
