import bpy
import sys
from os.path import splitext

from convex_hull import convex_hull


fileArgument = sys.argv[-1]
filename = splitext(fileArgument)[0]
print("\r\nLoading File: " + filename + "\r\n\r\n")

# Rename the file.
bpy.ops.wm.open_mainfile(filepath=filename + ".blend")

for i, collection in enumerate(bpy.data.collections):
   print(i, " ", collection.name)