import bpy
import sys
from os.path import splitext

from bounding_box import minimal_bounding_box


fileArgument = sys.argv[-1]
filename = splitext(fileArgument)[0]
print("\r\nLoading File: " + filename + "\r\n\r\n")

# Rename the file.
bpy.ops.wm.open_mainfile(filepath=filename + ".blend")
bpy.ops.wm.save_as_mainfile(filepath=filename + "_boxes" + ".blend")

for collection in [ bpy.data.collections[7] ]:
   print(collection.name)
   new_boxes = []
   for obj in [ collection.all_objects[0] ]:
       if obj.type == "MESH":
           hull = minimal_bounding_box(obj)
           new_boxes.append(hull)
           bpy.ops.wm.save_mainfile()

   new_collection = bpy.data.collections.new(collection.name + "_boxes")
   for bounding_box in new_boxes:
       if bounding_box.type == "MESH":
           collection.objects.link(bounding_box)
           bpy.ops.wm.save_mainfile()
   bpy.context.scene.collection.children.link(new_collection)

bpy.ops.wm.save_mainfile()