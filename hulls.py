import bpy
import sys
from os.path import splitext

from convex_hull import convex_hull


fileArgument = sys.argv[-1]
filename = splitext(fileArgument)[0]
print("\r\nLoading File: " + filename + "\r\n\r\n")

# Rename the file.
bpy.ops.wm.open_mainfile(filepath=filename + ".blend")
bpy.ops.wm.save_as_mainfile(filepath=filename + "_hulls" + ".blend")

for collection in [ bpy.data.collections[6] ]:
   print(collection.name)
   new_hulls = []
   for obj in collection.all_objects:
       if obj.type == "MESH":
           hull = convex_hull(obj.name, obj)
           new_hulls.append(hull)
           bpy.ops.wm.save_mainfile()

   for hull in new_hulls:
       if hull.type == "MESH":
           collection.objects.link(hull)
           bpy.ops.wm.save_mainfile()

bpy.ops.wm.save_mainfile()