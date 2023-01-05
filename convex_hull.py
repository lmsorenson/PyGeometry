import bpy
import bmesh
import math
import pprint
from mathutils import Vector
from bary_centric_coordinates import is_point_inside_triangle


def bary_center(vertices):
    bc = len(vertices)
    bx = 0
    by = 0
    bz = 0
    for point in vertices:
        bx += point.co.x
        by += point.co.y
        bz += point.co.z
    return (Vector([bx / bc, by / bc, bz / bc]), bc, bx, by, bz)

def bary_center_add(x, y, z, c, new_point):
    bc = c + 1
    bx = x + new_point.co.x
    by = y + new_point.co.y
    bz = z + new_point.co.z
    return (Vector([bx / bc, by / bc, bz / bc]), bc, bx, by, bz)


def compute_normal(p, q, r):
    a = q - p
    b = r - p
    n = a.cross(b)
    return n


# a(x-x1) + b(y-y1) + c(z-z1) = 0
# <a,b,c> is the normal to points p, q, r
# p will be substituted for <x1, y1, z1>
def find_plane_equation(p, q, r):
    normal = compute_normal(p, q, r)
    # the normal will be distributed to p (given by p * normal) which gives us the
    # constants of the equation which when added together give us d.
    x = (p * -1) * normal
    d = (x.x + x.y + x.z)
    return lambda v: (v.x * normal.x + v.y * normal.y + v.z * normal.z) + d

def point_lies_in_plane(p, q, r, x):
    a1 = q.x - p.x
    b1 = q.y - p.y
    c1 = q.z - p.z
    a2 = r.x - p.x
    b2 = r.y - p.y
    c2 = r.z - p.z
    a = b1 * c2 - b2 * c1
    b = a2 * c1 - a1 * c2
    c = a1 * b2 - b1 * a2
    d = (- a * p.x - b * p.y - c * p.z)

    return a * x.x + b * x.y + c * x.z + d

def point_lies_in_triangle(p, a, b, c):
    ab = b - a
    ac = c - a
    area = ab.cross(ac) / 2

    pa = p - a
    pb = p - b
    pc = p - c

    alpha = pb.cross(pc) / (2 * area)
    beta = pc.cross(pa) / (2 * area)
    gamma = (1 - alpha - beta)

    if alpha < 0 or alpha > 1:
        return False
    if beta < 0 or beta > 1:
        return False
    if gamma < 0 or gamma > 1:
        return False

    return (alpha + beta + gamma) == 1


def create_base_hull(hull_name, center, vertices):
    mesh_name = hull_name + "_mesh"
    print(len(vertices))

    bm = bmesh.new()
    mesh = bpy.data.meshes.new(mesh_name)

    # Start with the first 3 points.
    v1 = bm.verts.new(vertices[0])
    v2 = bm.verts.new(vertices[1])
    v3 = bm.verts.new(vertices[2])
    print(v1.co)
    print(v2.co)
    print(v3.co)
    print(len(bm.verts))

    # create a face for those three points.
    face = bm.faces.new((v1, v2, v3))

    # Find the formula to tell if a point lies on
    # the plane created by the first three points in the list of vectors.
    is_coplanar = find_plane_equation(v1.co, v2.co, v3.co)

    # Find the first point of the remaining points that is not coplanar
    # with respect to the previous 3.
    for idx, x in enumerate(vertices):
        print(x)
        if idx == 0 or idx == 1 or idx == 2:
            continue

        if not round(is_coplanar(x), 3) == 0:
            print("is not coplanar")
            print(idx)
            r = bm.verts.new(x)
            for edge in face.edges:
                p = edge.verts[0]
                q = edge.verts[1]
                bm.faces.new((p, q, r))
            ## If the point is finished do not continue looping through
            break
    print(len(bm.verts))
    print("removing doubles")
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.00001)

    # if the mesh is a perfect plane, we may not find a non-coplanar vertex.
    if (len(bm.verts) == 4):
        bm.to_mesh(mesh)
        if mesh_name in bpy.data.objects:
            to_delete = bpy.data.objects[mesh_name]
            bpy.data.objects.remove(to_delete, do_unlink=True)
        hull_object = bpy.data.objects.new(hull_name, mesh)

        print("Hull created.")
        return hull_object

    else:
        print("All vertices are coplanar.")

    bm.free()
    return None


def add_new_point(hull, center, new_point):
    point_added = False
    if hull is not None:
        #        bpy.context.scene.cursor.location = (new_point.x, new_point.y, new_point.z)
        # Open a transaction to modify the existing hull.
        if hull.data.is_editmode:
            bm = bmesh.from_edit_mesh(hull.data)
        else:
            bm = bmesh.new()
            bm.from_mesh(hull.data)

        conflict_graph = []

        existing_hull_center, ehcc, ehcx, ehcy, ehcz = bary_center(hull.data.vertices)

        # Go through the h list.
        for face in bm.faces:
            p = face.verts[0].co
            q = face.verts[1].co
            r = face.verts[2].co
            face_normal = compute_normal(p, q, r)
            face_normal.normalize()

            face_center, c, x, y, z = bary_center(face.verts)
            face_displacement = face_center - existing_hull_center
            face_displacement.normalize()
            normal_faces_out = face_displacement.dot(face_normal) >= 0

            if normal_faces_out:
                # is_coplanar = find_plane_equation(p, q, r)
                f_result = point_lies_in_plane(p, q, r, new_point)
                point_in_triangle = is_point_inside_triangle(p, r, q, new_point);
            else:
                # is_coplanar = find_plane_equation(p, r, q)
                f_result = point_lies_in_plane(p, r, q, new_point)
                face_normal *= -1
                point_in_triangle = is_point_inside_triangle(p, q, r, new_point);


            #print(f'Is Coplanar: {f_result}.')
            # f_result of greater than to zero implies a visible face.
            if f_result > 0:
                conflict_graph.append(face)

            # if f_result is 0 the point should be coplanar with the face.
            # if the point is not in the triangle then the face should be deleted.
            elif f_result == 0 and not point_in_triangle:
                conflict_graph.append(face)


        #        ob = bpy.context.object
        #        mat = ob.matrix_world
        #        me = ob.data

        #print(f'Conflict: {len(conflict_graph)}.')

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

        # Create new faces.
        for index, edge in boundary.items():
            if (edge.is_valid):
                verts = [bm.verts.new(new_point)]
                for vert in edge.verts:
                    verts.append(bm.verts.new(vert.co))
                bm.faces.new(verts)
                point_added = True

        # Do Clean Up
        bmesh.ops.delete(bm, geom=conflict_graph, context='FACES')
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)

        #print("finished adding point")
        if bm.is_wrapped:
            bmesh.update_edit_mesh(hull.data)
        else:
            bm.to_mesh(hull.data)
            hull.data.update()

        bm.free()
    return point_added


def convex_hull(hull_name, object):
    # Create the simple starting mesh with 4 points.
    hull_center, hc, hx, hy, hz = bary_center(object.data.vertices)
    bpy.context.scene.cursor.location = hull_center

    vertices = []
    for vert in object.data.vertices:
        vertices.append(vert.co - hull_center)

    hull = create_base_hull(hull_name + "_hull", hull_center, vertices)

    if object.data.is_editmode:
        bm = bmesh.from_edit_mesh(object.data)
    else:
        bm = bmesh.new()
        bm.from_mesh(object.data)

    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.01)

    existing_hull_center, ehcc, ehcx, ehcy, ehcz = bary_center(hull.data.vertices)

    processed = 0
    for vert in bm.verts:
        if (vert.is_valid):
            #print("Processed ", processed, " verts out of ", len(bm.verts))
            point_added = add_new_point(hull, hull_center, vert.co - hull_center)
            if point_added:
                #print("point added")
                existing_hull_center, ehcc, ehcx, ehcy, ehcz = bary_center_add(ehcx, ehcy, ehcz, ehcc, vert)
            processed += 1

    bm.free()

    # tranform the bmesh by the hull center.
    if object.data.is_editmode:
        hull_bm = bmesh.from_edit_mesh(hull.data)
    else:
        hull_bm = bmesh.new()
        hull_bm.from_mesh(hull.data)

    for vert in hull_bm.verts:
        vert.co += hull_center

    if hull_bm.is_wrapped:
        bmesh.update_edit_mesh(hull.data)
    else:
        hull_bm.to_mesh(hull.data)
        hull.data.update()

    hull_bm.free()

    return hull;