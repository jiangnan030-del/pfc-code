

import itasca as it
it.command("python-reset-state false")
from itasca import ballarray as ba
import numpy as np




dim = 2.5e-2
rad = dim / 20.0
it.command("""
model new
model domain extent -5e-2 6e-2 -6e-2 5e-2 -5e-2 5e-2
model cmat default model linear property kn 1e1 dp_nratio 0.2
ball generate cubic box -{xdim} {xdim} -{ydim} {ydim} -{xdim} {xdim} rad {rad}
ball attribute dens 2600
""".format(xdim=dim-rad, ydim=2*dim-rad, rad=rad))



radii = ba.radius()



radii



assert type(radii) is np.ndarray
print (radii.shape)
print (it.ball.count(),)



radii *= 0.75
ba.set_radius(radii)
radii = ba.radius()



radii



positions = ba.pos()



positions



force = -5e-3 * (positions.T/np.linalg.norm(positions,axis=1)).T



force



ba.set_force_app(force)




x, y, z = positions.T




y



y>0



radii[y>0] /= 0.75
ba.set_radius(radii)



from vec import vec

nballs = 100000
rmin = 8.0e-4
rmax = 1.2e-3
dom_lo = vec((-5e-2,-6e-2,-5e-2))
dom_hi = vec(( 6e-2, 5e-2, 5e-2))

brad = rmin + np.random.rand(nballs) *(rmax-rmin)
bpos = dom_lo + np.random.rand(nballs,3) *(dom_hi-dom_lo)

ba.create(brad,bpos)



it.command("ball delete")
ba.create(brad,bpos,density=1000.0,damp=0.7)



bdens = np.full_like(brad,1000.0)
x,y,z = bpos.T
bdens[x<0] *= 2.0
it.command("ball delete")
ba.create(brad,bpos,density=bdens,damp=0.7)



it.command("ball delete")
ba.create(brad,bpos,density=bdens,damp=0.7,props={'kn':1e4,'ks':1e4})

it.command("ball delete")
kn = np.full_like(brad,1.0e4)
kn[z<0] = 2e4
ba.create(brad,bpos,density=bdens,damp=0.7,props={'kn':kn,'ks':1e4,'myprop':'george'})


