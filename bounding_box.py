import bpy
import bmesh
import math
from mathutils import Vector
from convex_hull import bary_center
from convex_hull import compute_normal

# (1-t)(r0) + t(r1)
def intersect(bc, p, q, r, r0, r1):
    normal = compute_normal(p, r, q)
    vec = p * (normal * -1)
    c = (vec.x + vec.y + vec.z)
    q = (c - (r0.x * normal.x) - (r0.y * normal.y) - (r0.z * normal.z))
    div = ((-1 * (r0.x + r1.x) * normal.x) - ((r0.y + r1.y) * normal.y) - ((r0.z + r1.z) * normal.z))

    if div == 0:
        return None

    t = q / div

    if t <= 1 and t >= 0:
        return None

    x = r0.x - (t * (r0.x + r1.x))
    y = r0.y - (t * (r0.y + r1.y))
    z = r0.z - (t * (r0.z + r1.z))

    intersect = Vector([x, y, z])
    if r0.dot(intersect) > 0:
        return intersect.normalized()
    else:
        return intersect.normalized() * -1

def gaussian_sphere(name, polyhedron):
    if polyhedron.type == "MESH":

        hull = bmesh.new()
        hull.from_mesh(polyhedron.data)

        #        origin = bary_center(hull.verts)
        origin = Vector([0, 0, 0])

        sphere_mesh = bpy.data.meshes.new(name + "_mesh")
        bm = bmesh.new()
        o = bm.verts.new(origin)

        dict = {}
        regions = {}
        for face in hull.faces:
            verts = []
            bc, bx, by, bz, bcount = bary_center(face.verts)
            nc = bc - origin
            nc.normalize()
            c = bm.verts.new(nc + origin)
            dict[face.index] = c

        for edge in hull.edges:
            f1 = edge.link_faces[0]
            f2 = edge.link_faces[1]

            v1 = dict[f1.index]
            v2 = dict[f2.index]
            e = bm.edges.new((v1, v2))
            for v in edge.verts:
                if v.index in regions:
                    regions[v.index].append(e)
                else:
                    regions[v.index] = [e]

        for i, region in regions.items():
            bmesh.ops.contextual_create(bm, geom=region)

        bm.to_mesh(sphere_mesh)
        bm.free()

        sphere_object = bpy.data.objects.new(name, sphere_mesh)
        new_collection = bpy.data.collections.get('SphereCollection')
        if new_collection == None:
            new_collection = bpy.data.collections.new('SphereCollection')
        new_collection.objects.link(sphere_object)
        return sphere_object


def sigma(x):
    if x >= 0:
        return 1
    else:
        return -1


def r(theta1, fi):
    return math.sqrt((math.cos(theta1) ** 2) + (math.sin(theta1) ** 2) * (math.sin(fi) ** 2))


def x2(theta1, fi): return (sigma(fi) * -1) * math.sin(theta1) * math.sin(fi) / r(theta1, fi)


def y2(theta1, fi): return sigma(fi) * math.cos(theta1) * math.sin(fi) / r(theta1, fi)


def z2(theta1, fi): return (-1 * math.cos(theta1)) * math.cos(fi) / r(theta1, fi)


def box_normals(origin, theta1, n1, fi):
    n2 = Vector([x2(theta1, fi), y2(theta1, fi), z2(theta1, fi)])
    n2.normalize()

    n3 = n1.cross(n2)
    n3.normalize()

    return n2, n3


def rotate(obj, quat):
    if obj.data.is_editmode:
        bm = bmesh.from_edit_mesh(obj.data)
    else:
        bm = bmesh.new()
        bm.from_mesh(obj.data)

    for v in bm.verts:
        v.co.rotate(quat)

    if bm.is_wrapped:
        bmesh.update_edit_mesh(obj.data)
    else:
        bm.to_mesh(obj.data)
        obj.data.update()

    bm.free()


def translate(obj, vector):
    if obj.data.is_editmode:
        bm = bmesh.from_edit_mesh(obj.data)
    else:
        bm = bmesh.new()
        bm.from_mesh(obj.data)

    for v in bm.verts:
        v.co = v.co + vector

    if bm.is_wrapped:
        bmesh.update_edit_mesh(obj.data)
    else:
        bm.to_mesh(obj.data)
        obj.data.update()

    bm.free()


def verts_of_edge(obj, i):
    if obj.data.is_editmode:
        bm = bmesh.from_edit_mesh(obj.data)
    else:
        bm = bmesh.new()
        bm.from_mesh(obj.data)

    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

    e = bm.edges[i]
    verts = [e.verts[0].co, e.verts[1].co]

    if bm.is_wrapped:
        bmesh.update_edit_mesh(obj.data)
    else:
        bm.to_mesh(obj.data)
        obj.data.update()

    bm.free()

    return verts


def find_possible_theta_values(origin, g_sphere_obj, e2):
    #    bm = bmesh.new()
    #    theta_illustration_mesh = bpy.data.meshes.new("theta_illustration_mesh")
    #    o = bm.verts.new(Vector())

    # Go through all edges and determine if that line intersects
    # with the path of n.
    possible_theta = []
    for i in range(0, len(g_sphere_obj.data.edges)):
        everts = verts_of_edge(g_sphere_obj, i)
        r0 = everts[1]
        r1 = everts[0]

        # edges intersecting n1 path.
        p = Vector([0, 0, 0])
        q = Vector([1, 0, 0])
        r = Vector([0, 1, 0])
        i = intersect(origin, p, q, r, r0, r1)

        if i is not None:
            # take the dot product of the point of
            # intersection and the positive x
            d = i.dot(q)
            if d < -1:
                theta = math.acos(-1)
            elif d > 1:
                theta = math.acos(1)
            else:
                theta = math.acos(d)

            p = i.dot(r)
            if p < 0:
                theta *= -1

            if theta <= 0 and theta >= (math.pi * -1):
                possible_theta.append(theta)
        #                ip = bm.verts.new(i)
        #                bm.edges.new((o, ip))

        # edges intersecting n2 path.
        p2 = Vector([0, 0, 0])
        q2 = Vector([1, 0, 0])
        r2 = q2.cross(e2)
        i = intersect(origin, p2, q2, r2, r0, r1)

        if i is not None:
            # take the dot product of the point of
            # intersection and the positive x
            d = i.dot(q2)
            if d < -1:
                theta2 = math.acos(-1)
            elif d > 1:
                theta2 = math.acos(1)
            else:
                theta2 = math.acos(d)

            p = i.dot(r2)
            if p < 0:
                theta2 *= -1

    #            if theta2 <= (math.pi / 2) and theta2 >= ((math.pi / 2) * -1):
    #                ip = bm.verts.new(i)
    #                bm.edges.new((o, ip))

    #    bm.to_mesh(theta_illustration_mesh)
    #    bm.free()

    #    if "theta_illustration" in bpy.data.objects:
    #        to_delete = bpy.data.objects["theta_illustration"]
    #        bpy.data.objects.remove(to_delete, do_unlink=True)
    #    theta_illustration_object = bpy.data.objects.new("theta_illustration", theta_illustration_mesh)
    #    new_collection = bpy.data.collections.get('Collection')
    #    new_collection.objects.link(theta_illustration_object)

    return possible_theta


def ex(v, n, ex):
    s_c = v.co.dot(n) / n.length
    if (s_c < ex):
        ex = sc


def compute_minima(name, sph, origin, e1, e2, hull_points, min_vol):
    tv = e1.verts[0].co

    # translate edges to the origin.
    e1v = e1.verts[1].co - tv
    e1v.normalize()
    e2v = e2.verts[1].co - e2.verts[0].co
    e2v.normalize()

    # Rotate the edges so that it lies on the z axis
    u = Vector([0, 0, 1])
    q1 = e1v.rotation_difference(u)
    e1v.rotate(q1)
    e2v.rotate(q1)

    # Rotate the edges so that e2 lies on the y-z plane
    yp = Vector([0, 1, 0])
    jj = Vector([e2v.x, e2v.y, 0])
    q2 = jj.rotation_difference(yp)
    e1v.rotate(q2)
    e2v.rotate(q2)

    # Rotate the gaussian sphere to fit the illustration
    rotate(sph, q1)
    rotate(sph, q2)

    # Find values for theta
    possible_theta = find_possible_theta_values(origin, sph, e2v)
    possible_theta.sort()
    #    pprint.pprint(possible_theta)

    b = False
    for th in possible_theta:
        # Calculate Fi
        fdot = e2v.dot(Vector([0, 1, 0]))

        if (fdot > 1):
            fdot = 1
        if (fdot < -1):
            fdot = -1

        fi = math.acos(fdot)
        n1 = Vector([math.cos(th), math.sin(th), 0])
        n1.normalize()

        n2, n3 = box_normals(origin, th, n1, fi)
        #        if round(e1v.dot(n1), 6) == 0 and round(e2v.dot(n2), 6) == 0:
        #            print("GOOD")
        #            b = True
        #        else:
        #            print("BAD")
        #            break

        n1.rotate(q2.inverted())
        n1.rotate(q1.inverted())
        n2.rotate(q2.inverted())
        n2.rotate(q1.inverted())
        n3.rotate(q2.inverted())
        n3.rotate(q1.inverted())

        n1_neg_ex = None
        n2_neg_ex = None
        n3_neg_ex = None
        n1_pos_ex = None
        n2_pos_ex = None
        n3_pos_ex = None
        for v in hull_points:
            s_c_1 = v.co.dot(n1) / n1.length
            if (n1_neg_ex is None or s_c_1 < n1_neg_ex):
                n1_neg_ex = s_c_1
            s_c_2 = v.co.dot(n2) / n2.length
            if (n2_neg_ex is None or s_c_2 < n2_neg_ex):
                n2_neg_ex = s_c_2
            s_c_3 = v.co.dot(n3) / n3.length
            if (n3_neg_ex is None or s_c_3 < n3_neg_ex):
                n3_neg_ex = s_c_3

            s_c_p_1 = v.co.dot(n1) / n1.length
            if (n1_pos_ex is None or s_c_p_1 > n1_pos_ex):
                n1_pos_ex = s_c_p_1
            s_c_p_2 = v.co.dot(n2) / n2.length
            if (n2_pos_ex is None or s_c_p_2 > n2_pos_ex):
                n2_pos_ex = s_c_p_2
            s_c_p_3 = v.co.dot(n3) / n3.length
            if (n3_pos_ex is None or s_c_p_3 > n3_pos_ex):
                n3_pos_ex = s_c_p_3

        disp_1 = n1 * n1_neg_ex
        disp_2 = n2 * n2_neg_ex
        disp_3 = n3 * n3_neg_ex
        disp_1_pos = n1 * n1_pos_ex
        disp_2_pos = n2 * n2_pos_ex
        disp_3_pos = n3 * n3_pos_ex
        disp = disp_1 + disp_2 + disp_3
        disp2 = disp_1_pos + disp_2_pos + disp_3_pos

        bm_box = bmesh.new()
        box_mesh = bpy.data.meshes.new(name + "_box_mesh")
        v0 = bm_box.verts.new(Vector() + disp)
        v7 = bm_box.verts.new(Vector() + disp2)

        l1 = (v7.co - v0.co).dot(n1) / n1.length
        l2 = (v7.co - v0.co).dot(n2) / n2.length
        l3 = (v7.co - v0.co).dot(n3) / n3.length

        volume = l1 * l2 * l3
        if min_vol == 0 or volume < min_vol:
            min_vol = volume
        else:
            continue

        v1 = bm_box.verts.new(n1 * l1 + disp)
        bm_box.edges.new((v0, v1))
        v2 = bm_box.verts.new(n2 * l2 + disp)
        bm_box.edges.new((v0, v2))
        v3 = bm_box.verts.new(n3 * l3 + disp)
        bm_box.edges.new((v0, v3))

        v4 = bm_box.verts.new(n1 * l1 * -1 + disp2)
        bm_box.edges.new((v7, v4))
        v5 = bm_box.verts.new(n2 * l2 * -1 + disp2)
        bm_box.edges.new((v7, v5))
        v6 = bm_box.verts.new(n3 * l3 * -1 + disp2)
        bm_box.edges.new((v7, v6))

        bm_box.edges.new((v3, v4))
        bm_box.edges.new((v2, v4))
        bm_box.edges.new((v1, v5))
        bm_box.edges.new((v1, v6))
        bm_box.edges.new((v3, v5))
        bm_box.edges.new((v2, v6))

        bm_box.to_mesh(box_mesh)
        minima_name = name + "_minima"
        if minima_name in bpy.data.objects:
            to_delete = bpy.data.objects[minima_name]
            bpy.data.objects.remove(to_delete, do_unlink=True)
        box_object = bpy.data.objects.new(minima_name, box_mesh)
        new_collection = bpy.data.collections.get('MinimaCollection')
        if new_collection == None:
            new_collection = bpy.data.collections.get('MinimaCollection')
        new_collection.objects.link(box_object)

    if (b == True):
        print("d true")
    return b, min_vol


def minimal_bounding_box(polyhedron):
    if polyhedron.type == "MESH":
        sphere_name = polyhedron.name + "_gaussian_sphere"
        # readonly hull
        hull = bmesh.new()
        hull.from_mesh(polyhedron.data)
        origin, ox, oy, oz, oc = bary_center(hull.verts)

        hull.verts.ensure_lookup_table()
        hull.edges.ensure_lookup_table()
        hull.faces.ensure_lookup_table()

        b = False
        min_vol = 0
        for e1 in hull.edges:
            for e2 in hull.edges:
                if e1.index == e2.index:
                    continue
                print("e1 " + str(e1.index) + " and " + " e2 " + str(e2.index) + " of " + str(len(hull.edges)))

                if sphere_name in bpy.data.objects:
                    to_delete = bpy.data.objects[sphere_name]
                    bpy.data.objects.remove(to_delete, do_unlink=True)
                sph = gaussian_sphere(sphere_name, polyhedron)

                b, min = compute_minima(polyhedron.name, sph, origin, e1, e2, hull.verts, min_vol)

                if b == True:
                    print("break")
            #                    break

            if b == True:
                print("break")
#                break