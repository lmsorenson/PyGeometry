from mathutils import Vector

# C is the coordinate for which we want to determine the
# bary centric coordinate.
def mu(c, c1, c2):
    e1 = c1 - c
    e2 = c2 - c

    m = e1 - (e1.dot(e2) * e2 / e2.dot(e2))
    d = m.dot(e1)

    if d == 0:
        return None

    else:
        return m / d

def in_bounds(c): return 1 >= c >= 0;

def bary_centric_coordinates(a, b, c, u):
    mu_a = mu(c, a, b)
    mu_b = mu(a, b, c)
    mu_g = mu(b, c, a)

    if (mu_a == None or mu_b == None or mu_g == None):
        return -1, -1, -1

    alpha = (u - c).dot(mu_a)
    beta = (u - a).dot(mu_b)
    gamma = (u - b).dot(mu_g)

    return alpha, beta, gamma

def is_point_inside_triangle(a, b, c, u):
    alpha, beta, gamma = bary_centric_coordinates(a, b, c, u)
    return in_bounds(alpha) and in_bounds(beta) and in_bounds(gamma)