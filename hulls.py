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
   for i, obj in enumerate(collection.all_objects):
       print("\r\n\r\n\r\n\r\n", collection.name, " ", i, " of " , len(collection.all_objects), "\r\n\r\n\r\n\r\n")
       if obj.type == "MESH":
           hull = convex_hull(obj.name, obj)
           new_hulls.append(hull)
           bpy.ops.wm.save_mainfile()

   new_collection = bpy.data.collections.new(collection.name + "_hulls")
   for h in new_hulls:
       print(h.name, ": ", h.type)
       if h.type == "MESH":
           new_collection.objects.link(h)
           bpy.ops.wm.save_mainfile()

   print(collection.name)

bpy.ops.wm.save_mainfile()