import bpy
import bmesh
import sys
from os.path import splitext
from convex_hull import bary_center
from mathutils import Vector

fileArgument = sys.argv[-1]
filename = splitext(fileArgument)[0]
print("\r\nLoading File: " + filename + "\r\n\r\n")

# Rename the file.
bpy.ops.wm.open_mainfile(filepath=filename + ".blend")
bpy.ops.wm.save_as_mainfile(filepath=filename + "_clustered" + ".blend")

for collection in [ bpy.data.collections[6] ]:
   print(collection.name)
   print("Contains ", len(collection.all_objects), " objects");
   old_objs = []
   new_objs = []
   for obj in collection.all_objects:
       if obj.type == "MESH":
           cluster1_faces = []
           cluster2_faces = []
           if obj.data.is_editmode:
               bm = bmesh.from_edit_mesh(obj.data)
           else:
               bm = bmesh.new()
               bm.from_mesh(obj.data)
           ###

           c = bary_center(bm.verts)
           center_1 = c[0] + Vector((0, 0, -1))
           center_2 = c[0] + Vector((0, 0, 1))

           print("obj: ", obj.name, " verts: ", len(bm.verts))
           for face in bm.faces:
               bc = bary_center(face.verts)
               d1 = bc[0] - center_1
               d2 = bc[0] - center_2
               if d2.length > d1.length:
                   cluster1_faces.append(face)
               else:
                   cluster2_faces.append(face)

           object_name = obj.name
           print("Creating new meshes...")
           bcluster1 = bmesh.new()
           for face in cluster1_faces:
               bverts = []
               for vert in face.verts:
                   bverts.append(bcluster1.verts.new(vert.co))
               bcluster1.faces.new(bverts)
           bmesh.ops.remove_doubles(bcluster1, verts=bcluster1.verts, dist=0.01)

           bcluster1_mesh = bpy.data.meshes.new(object_name + "_cluster1_mesh")
           bcluster1.to_mesh(bcluster1_mesh)
           bcluster1.free()
           new_objs.append(bpy.data.objects.new(object_name + "_cluster1", bcluster1_mesh))
           print("finished cluster 1")

           bcluster2 = bmesh.new()
           for face in cluster2_faces:
               bverts = []
               for vert in face.verts:
                   bverts.append(bcluster2.verts.new(vert.co))
               bcluster2.faces.new(bverts)
           bmesh.ops.remove_doubles(bcluster2, verts=bcluster2.verts, dist=0.01)

           bcluster2_mesh = bpy.data.meshes.new(object_name + "_cluster2_mesh")
           bcluster2.to_mesh(bcluster2_mesh)
           bcluster2.free()
           new_objs.append(bpy.data.objects.new(object_name + "_cluster2", bcluster2_mesh))
           print ("finished cluster 2")

           old_objs.append(obj)

           print("c1: ", len(cluster1_faces), " c2: ", len(cluster2_faces))

           ###
           if bm.is_wrapped:
               bmesh.update_edit_mesh(obj.data)
           else:
               bm.to_mesh(obj.data)
               obj.data.update()

           bm.free()
       else:
           print("object ", obj.name);

   for o in new_objs:
       collection.objects.link(o)


   bpy.ops.object.delete({"selected_objects": old_objs})

bpy.ops.wm.save_mainfile()