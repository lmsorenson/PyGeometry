import bpy
import bmesh
import math
import pprint
from mathutils import Vector


def bary_center(vertices):
    bc = len(vertices)
    bx = 0
    by = 0
    bz = 0
    for point in vertices:
        bx += point.co.x
        by += point.co.y
        bz += point.co.z
    return Vector([bx / bc, by / bc, bz / bc])


def compute_normal(bc, p, q, r):
    off_p = p - bc
    off_q = q - bc
    off_r = r - bc
    a = off_q - off_p
    b = off_r - off_p
    n = a.cross(b)
    return n


def find_plane_equation(bc, p, q, r):
    normal = compute_normal(bc, p, q, r)
    x = p * (normal * -1)
    d = (x.x + x.y + x.z)
    return lambda v: (v.x * normal.x + v.y * normal.y + v.z * normal.z) + d


def create_base_hull(center, object):
    if object.type == "MESH":
        verts = []
        edges = []
        faces = [[0, 1, 2], [0, 1, 3], [2, 3, 0], [2, 3, 1]]

        # First off, select 4 points that are non coplaner
        v_list = object.data.vertices

        # Start with the first 3 points.
        verts.append(v_list[0].co)
        verts.append(v_list[1].co)
        verts.append(v_list[2].co)

        # Find the formula to tell if a point lies on
        # the plane created by the first three points in the list of vectors.
        is_coplanar = find_plane_equation(center, v_list[0].co, v_list[1].co, v_list[2].co)

        # Find the first point of the remaining points that is not coplanar
        # with respect to the previous 3.
        for idx, x in enumerate(v_list):
            print("len " + str(len(verts)))
            if not is_coplanar(x.co) == 0:
                verts.append(x.co)
                print("len " + str(len(verts)))
                break

        # if the mesh is a perfect plane, we may not find a non-coplanar vertex.
        if (len(verts) == 4):
            print("success")

            hull_mesh = bpy.data.meshes.new("hull_mesh")
            hull_mesh.from_pydata(verts, edges, faces)
            hull_mesh.update()

            hull_object = bpy.data.objects.new('hull_object', hull_mesh)
            new_collection = bpy.data.collections.get('Collection')
            new_collection.objects.link(hull_object)

        else:
            print("All vertices are coplanar.")


def add_new_point(hull, center, new_point):
    bpy.context.scene.cursor.location = (new_point.x, new_point.y, new_point.z)
    h_list = hull.data.vertices

    # Open a transaction to modify the existing hull.
    if hull.data.is_editmode:
        bm = bmesh.from_edit_mesh(o)
    else:
        bm = bmesh.new()
        bm.from_mesh(hull.data)

    conflict_graph = []
    bpy.context.view_layer.objects.active = hull

    # Go through the h list.
    for face in bm.faces:
        p = face.verts[0].co
        q = face.verts[1].co
        r = face.verts[2].co
        face_normal = compute_normal(center, p, q, r)
        face_normal.normalize()

        existing_hull_center = bary_center(h_list)
        face_center = bary_center(face.verts)
        face_displacement = face_center - existing_hull_center
        face_displacement.normalize()
        normal_faces_out = face_displacement.dot(face_normal) >= 0

        if normal_faces_out:
            is_coplanar = find_plane_equation(center, p, q, r)
        else:
            is_coplanar = find_plane_equation(center, p, r, q)
            face_normal *= -1

        if is_coplanar(new_point) > 0:
            conflict_graph.append(face)

    ob = bpy.context.object
    assert ob.type == "MESH"
    mat = ob.matrix_world
    me = ob.data

    boundary = {}
    for face in conflict_graph:
        for edge in face.edges:
            if edge.index in boundary:
                # an edge in this convex hull should
                # only border two faces if two visible
                # faces both contain this edge then it is
                # not on the boundary.
                del boundary[edge.index]
            else:
                boundary[edge.index] = edge

    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(boundary)

    # Create new faces.
    for index, edge in boundary.items():
        verts = [bm.verts.new(new_point)]
        for vert in edge.verts:
            verts.append(bm.verts.new(vert.co))
        #        bmesh.ops.contextual_create(bm, geom=verts)
        bm.faces.new(verts)

    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.01)

    # Delete existing faces.
    bmesh.ops.delete(bm,
                     geom=conflict_graph,
                     context='FACES_ONLY')

    if bm.is_wrapped:
        bmesh.update_edit_mesh(hull.data)
    else:
        bm.to_mesh(hull.data)
        hull.data.update()

    bm.free()


def convex_hull(object):
    # Create the simple starting mesh with 4 points.
    hull_center = bary_center(object.data.vertices)
    create_base_hull(hull_center, object)
    hull = bpy.data.objects.get("hull_object")

    v_list = object.data.vertices
    #        add_new_point(hull, hull_center, v_list[10].co)
    #        add_new_point(hull, hull_center, v_list[11].co)
    #        add_new_point(hull, hull_center, v_list[12].co)
    #        add_new_point(hull, hull_center, v_list[13].co)

    i = 0
    for vert in v_list:
        #            if i > 50:
        #                break

        add_new_point(hull, hull_center, vert.co)
        i += 1


suzanne = bpy.data.objects.get("Suzanne")
convex_hull(suzanne)

n = compute_normal(
    Vector([0, 0, 0]),
    Vector([0, 0, 0]),  # p
    Vector([0, 0, 1]),  # q
    Vector([1, 0, 0]))  # r
print(n)

exp = find_plane_equation(
    Vector([0, 0, 0]),
    Vector([0, 0, 0]),
    Vector([1, 0, 0]),
    Vector([0, 0, 1]))

vec = exp(Vector([1, 1, 1]))
vec2 = exp(Vector([1, 1, -1]))
print(vec)
print(vec2)