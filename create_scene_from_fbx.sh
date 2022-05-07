#!/bin/bash

echo "Creating a new scene."

/Applications/Blender.app/Contents/MacOS/Blender \
--background \
--python create_scene_from_fbx.py \
$1
