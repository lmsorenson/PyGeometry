from mathutils import Vector

# C is the coordinate for which we want to determine the
# bary centric coordinate.
def mu(c, c1, c2):
    e1 = c1 - c
    e2 = c2 - c

    m = e1 - (e1.dot(e2) * e2 / e2.dot(e2))
    d = m.dot(e1)

    if d == 0:
        raise Exception("d is 0: ", " e1 ", e1, " e2 ", e2, " m ", m)

    return m / d

def in_bounds(c):
    if c is not None: return 1 >= c >= 0;
    else: return None

def bary_centric_coordinates(a, b, c, u):
    try:
        mu_a = mu(c, a, b)
        mu_b = mu(a, b, c)
        mu_g = mu(b, c, a)

    except Exception as e:
        print (e)
        return None, None, None

    if mu_a is None or mu_b is None or mu_g is None:
        return -1, -1, -1

    alpha = (u - c).dot(mu_a)
    beta = (u - a).dot(mu_b)
    gamma = (u - b).dot(mu_g)

    return alpha, beta, gamma

def is_point_inside_triangle(a, b, c, u):
    if (b - a).length == 0 or (c - a).length == 0 or (c - b).length == 0:
        return None

    alpha, beta, gamma = bary_centric_coordinates(a, b, c, u)
    if alpha is not None and beta is not None and gamma is not None:
        return in_bounds(alpha) and in_bounds(beta) and in_bounds(gamma)
    else:
        return None