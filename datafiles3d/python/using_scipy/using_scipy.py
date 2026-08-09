

import matplotlib
matplotlib.use("QT5Agg")
matplotlib.rcParams['backend.qt5']='PySide2'
import pylab as plt
import numpy as np
from scipy.constants import inch

import itasca as it
it.command("python-reset-state false")
from itasca import ballarray as ba

r = 8.0  # beam radius [inches]
l = 200.0 # beam length [inches]
x = np.linspace(0, l, 100)
E = 1e4 # [ksi]
I = 0.25*np.pi*r**4 # moment of inertia.
f = 1.0 # [kip] force applied in the positive y direction



def analytical_deflection(x):
    "Return the analytical solution for y deflection at the x point(s)"
    return f * x**2 / 2.0 / E / I * ( l - x / 3.0)

def pfc_deflection(E_trial):
    """For a given parallel bond stiffness, return a tuple containing the
    ball x positions and the y displacements.

    calling this function cycles the PFC engine
    """
    n = 11 # number of pfc particles
    pb_kn = E_trial/l*(n-1)
    print ("calculating deflection with pb_kn = {} ... ".format(pb_kn),)
    it.command("""
    model new
    model random
    model domain ext -50 250 -50 50
    model cmat default model linearpbond
    """)

    for i in range(n):
        it.ball.create(10.0, (i*20.0, 0.0, 0.0))

    tip_ball = it.ball.find(n)
    tip_ball.set_force_app_y(f)

    it.command("""
    ball attribute dens=1000 damp 0.7
    ball property 'kn'=0 'ks'=0
    model clean
    contact method bond
    contact property pb_ten 1e5 pb_coh 1e5 pb_kn {kn} pb_ks 188 pb_rmul 0.8
    ball fix velocity-x velocity-y velocity-z ...
    spin-x spin-y spin-z range id=1
    model solve ratio-maximum 1e-4
    """.format(kn=pb_kn))

    pfc_x = ba.pos()[:,0]
    pfc_dy = ba.disp()[:,1]
    print ("done")
    return pfc_x, pfc_dy





pfc_x, pfc_dy = pfc_deflection(E)

plt.plot(x, analytical_deflection(x))
plt.plot(pfc_x, pfc_dy, "o")
plt.xlabel("Length along beam [inches]")
plt.ylabel("Beam vertical displacement [inches]")
plt.draw()
plt.savefig("p3d-opt_comp.png")



from scipy.optimize import fminbound

def residual(pb_kn):
    """Return the sum of squares of the residual. This is a scalar measure
       of the difference between the PFC solution and the analytical solution.
    """
    pfc_x, pfc_dy = pfc_deflection(pb_kn)
    a_dy = analytical_deflection(pfc_x)
    plt.close('all')
    plt.plot(x, analytical_deflection(x))
    plt.plot(pfc_x, pfc_dy, "o")
    plt.xlabel("Length along beam [inches]")
    plt.ylabel("Beam vertical displacement [inches]")
    plt.draw()

    return ((a_dy - pfc_dy)**2).sum()

E_opt =  fminbound(residual, 1e2, 5.5e4)


print ("""

E specified: {}
E calculated: {}""".format(E, E_opt))
plt.close('all')



