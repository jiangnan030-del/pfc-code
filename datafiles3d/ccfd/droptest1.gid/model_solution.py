from math import sqrt, pi
from scipy.optimize import fminbound

r =  1e-2 / 2.0
rhof =  1260.0
rhop = 2500.0
mu =  1.5
g = 9.81

rep = lambda v : 2 * rhof * r * abs(v) / mu
cd  = lambda v : (0.63 + 4.8 / sqrt(rep(v))) ** 2

lhs = lambda v : 0.5 * pi * rhof * r **2 * cd(v) * v ** 2
rhs = lambda : 4.0 / 3.0 * pi * r**3 * (rhop - rhof) * g
residual = lambda v : abs(lhs(v) - rhs())

sol  = fminbound(residual, -1, -1e-5, xtol=1e-16)

print "Low Reynolds number model solution: {:.2e} m/s".format(sol)

rhof = 1000.0
mu = 1.004e-3
rhop = 2650
r = 1e-3 / 2.0

sol  = fminbound(residual, -1, -1e-5, xtol=1e-16)

print "Higher Reynolds number model solution: {:.2e} m/s".format(sol)
