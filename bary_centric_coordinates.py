from mathutils import Vector

# C is the coordinate for which we want to determine the
# bary centric coordinate.
def mu(c, c1, c2):
    e1 = c1 - c
    e2 = c2 - c

    m = e1 - (e1.dot(e2) * e2 / e2.dot(e2))
    return m / m.dot(e1)

def in_bounds(c): return 1 >= c >= 0;

def bary_centric_coordinates(a, b, c, u):
    mu_a = mu(c, a, b)
    mu_b = mu(a, b, c)
    mu_g = mu(b, c, a)

    alpha = (u - c).dot(mu_a)
    beta = (u - a).dot(mu_b)
    gamma = (u - b).dot(mu_g)

    return alpha, beta, gamma

def is_point_inside_triangle(a, b, c, u):
    alpha, beta, gamma = bary_centric_coordinates(a, b, c, u)
    return in_bounds(alpha) and in_bounds(beta) and in_bounds(gamma)