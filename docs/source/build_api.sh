#!/usr/bin/env bash


# *** call this script INSIDE docs/ dir ***


MODULE_NAME=h1st
MODULE_PATH=../$MODULE_NAME

DOCS_SOURCE_DIR=source
APIDOC_DIR=$DOCS_SOURCE_DIR/api
DOCS_BUILD_DIR=_build

mkdir -p $APIDOC_DIR

DOCS_SOURCE_DIR_RST_FILE_PATHS="$APIDOC_DIR/$MODULE_NAME*.rst"

# remove old .RST files
rm -f $DOCS_SOURCE_DIR_RST_FILE_PATHS

# generate .RST files from module code & docstrings
# any pathnames given at the end are paths to be excluded ignored during generation
sphinx-apidoc \
  --force \
  --implicit-namespaces \
  --maxdepth 9 \
  --separate \
  --module-first \
  --output-dir $APIDOC_DIR \
  $MODULE_PATH

# remove undocumented members
sed -e /:undoc-members:/d -i .orig $DOCS_SOURCE_DIR_RST_FILE_PATHS
rm $APIDOC_DIR/*.orig

# remove old doc
rm -rf $DOCS_BUILD_DIR

# build new doc
if [[ "$1" == "--watch" ]]; then
  sphinx-autobuild \
    --delay 5 \
    --open-browser \
    --poll \
    --watch $DOCS_SOURCE_DIR \
    $DOCS_SOURCE_DIR $DOCS_BUILD_DIR
else
  sphinx-build $DOCS_SOURCE_DIR $DOCS_BUILD_DIR
fi

