#!/bin/bash

echo "Loading scene"

path=$(dirname "$0")
echo $path

Blender \
--background \
--python "$path"/clustering.py \
--python-use-system-env \
$1
