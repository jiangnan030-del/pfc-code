from math import exp, log10, pi, sqrt
from scipy.optimize import fminbound

r =  1.25e-3
rhof =  998.23
mu =  1.004e-3
e =  1 - pi/6.0        # porosity
VOL = 1e-6             # element volume
gradp = 1.0e2/.1       # applied pressure gradient

rep = lambda v : 2 * rhof * r * abs(v) / mu
cd  = lambda v : (0.63 + 4.8 / sqrt(rep(v)))**2;

f0 = lambda v : 0.5 * cd(v) * rhof * pi * r**2 * v**2
chi = lambda v : 3.7 - 0.65 * exp(-(1.5 - log10(rep(v)))**2 / 2.0);

fpuv = lambda v:  4**3 * f0(v) * e**-chi(v) / VOL;

residual = lambda v : abs(fpuv(v) - gradp*e)
sol  = fminbound(residual, 0.1e-3, 10.0e-2, xtol=1e-16)

print "Model solution fluid velocity {:.4e} m/s.".format(sol)
print "Model solution drag force sum {:.4e} N.".format(fpuv(sol)*VOL)
