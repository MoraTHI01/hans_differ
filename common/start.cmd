: # Builds and runs the webfrontend for testing
:<<"::CMDLITERAL"
@ECHO OFF
GOTO :CMDSCRIPT
::CMDLITERAL
#!/bin/bash

flagBuild=0
flagTest=0
flagReBuild=0

while getopts brt flag
do
    case "${flag}" in
        b) flagBuild=1;;
        r) flagReBuild=1;;
        t) flagTest=1;;
    esac
done


MODULE_DIR="modules"
DIST_DIR="$MODULE_DIR/dist"

PY_VERSIONS=("3.9")

mkdir -p "$DIST_DIR"

for PYVER in "${PY_VERSIONS[@]}"; do
  echo "🔧 Building wheel for Python $PYVER..."
  docker run --rm \
    -v "$(pwd)/$MODULE_DIR":/app \
    -w /app \
    python:$PYVER \
    bash -c "pip install build && python -m build --wheel --outdir /app/dist"
done

echo "✅ Wheels built in $DIST_DIR"
exit $?

:CMDSCRIPT
ECHO Windows is currently not supported, please use WSL2 or Hyper-V and Docker Desktop!
