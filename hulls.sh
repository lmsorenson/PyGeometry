#!/bin/bash

echo "Loading scene"

path=$(dirname "$0")
echo $path

/Applications/Blender.app/Contents/MacOS/Blender \
--background \
--python "$path"/hulls.py \
--python-use-system-env \
$1
