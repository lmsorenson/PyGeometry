#!/bin/bash

echo "Creating a new scene."

path=$(dirname "$0")
echo $path

Blender \
--background \
--python "$path"/create_scene_from_fbx.py \
--python-use-system-env \
$1
