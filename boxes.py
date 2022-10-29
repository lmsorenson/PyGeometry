import bpy
import sys
from os.path import splitext

from BoundingBox import minimal_bounding_box


fileArgument = sys.argv[-1]
filename = splitext(fileArgument)[0]
print("\r\nLoading File: " + filename + "\r\n\r\n")

# Rename the file.
bpy.ops.wm.open_mainfile(filepath=filename + ".blend")
bpy.ops.wm.save_as_mainfile(filepath=filename + "_boxes" + ".blend")

for collection in [ bpy.data.collections[6] ]:
   print(collection.name)
   new_hulls = []
   for obj in [ collection.all_objects[0] ]:
       if obj.type == "MESH":
           hull = minimal_bounding_box(obj)
           new_hulls.append(hull)
           bpy.ops.wm.save_mainfile()

   for hull in new_hulls:
       if hull.type == "MESH":
           collection.objects.link(hull)
           bpy.ops.wm.save_mainfile()

bpy.ops.wm.save_mainfile()