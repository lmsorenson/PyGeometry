import bpy
from bpy import context

import sys
import os
from os.path import exists
from os.path import splitext

fileArgument = sys.argv[-1]

print("\r\n")
print("Looking for FBX file " + fileArgument + " in working directory:")
print(os.getcwd())

filename = splitext(fileArgument)[0]

if exists(filename + ".fbx"):
    print("FBX file name " + filename + " was found.\r\n")

else:
    sys.exit("FBX file named " + fileArgument + " was not found.\r\n")

bpy.ops.wm.save_as_mainfile(filepath=filename + ".blend")

# Delete all default objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
bpy.ops.wm.save_mainfile()

# Import fbx object.
bpy.ops.import_scene.fbx(filepath = str(filename + ".fbx"))
bpy.ops.wm.save_mainfile()


def ApplyMaterial(material_name, obj):
    mat = bpy.data.materials.get(material_name)

    if mat is not None:
        # assign material
        if obj.data.materials:
            # assign to 1st material slot
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)

def matcher(x):
    return '.' not in x.name

uniqueMaterials = filter(matcher, bpy.data.materials)
for material in uniqueMaterials:
    bpy.ops.object.select_all(action='DESELECT')
    mat_name = material.name
    col = bpy.data.collections.new(mat_name)
    bpy.context.scene.collection.children.link(col)
    print("Linking " + mat_name + " collection")

    for object in bpy.data.objects:
        # Select only mesh objects
        if object.type == "MESH":
            # Gets the first material for that object
            objectMaterial = object.data.materials[0]

            # if the object's material starts with the name of the current unique material
            # apply the unique material to that object.
            if objectMaterial is not None and objectMaterial.name.startswith(mat_name):
                bpy.context.view_layer.objects.active = object
                col.objects.link(object)
                ApplyMaterial(mat_name, object)

bpy.ops.wm.save_mainfile()
