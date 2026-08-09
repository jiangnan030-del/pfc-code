

import itasca as it
it.command("python-reset-state false")
from itasca import ballarray as ba
from itasca import ball as balls
from itasca import contact as contacts
import numpy as np

it.command("""
model new
model domain extent -1 1 -1 1 -1 1
model cmat default model linearpbond property pb_ten 12.0e6 pb_coh 10.0e6 pb_fa 20.0 fric 0.5  ...
                   method deformability    emod 8.5e9 kratio 2.5                         ...
                   method pb_deformability emod 8.5e9 kratio 2.5                         ...
                   proximity 4e-4
""")



box_len = 38.1e-3
data = np.loadtxt("balls.txt",delimiter=",")
for datum in data:
    r, p, fix = datum[0],datum[1:4], datum[4]
    b = balls.create(r, p)
    if fix == 1.0:
        if b.pos_z() > 0.0:
            b.set_extra(1, 1)
        else:
            b.set_extra(1, 2)
    else:
        b.set_extra(1,0)




it.command("""
ball attribute density 2000.0 damp 0.6
model clean
contact method bond gap 4e-4
contact property lin_mode 1
model cmat default proximity 0.0
model clean all
""")

print ("This model has {} contacts".format(it.contact.count()))



for name, value in it.contact.find(it.BallBallContact, 1).props().items():
    print ("{:15}: {}".format(name, value))



vel = 1e-2
top_count = 0
bottom_count = 0
for b in balls.list():
    if b.extra(1) == 1:
        b.set_vel_z(-vel)
        b.set_fix(3, True)
        top_count += 1
    elif b.extra(1) == 2:
        b.set_vel_z(0)
        b.set_fix(3,True)
        bottom_count += 1

print ("{} top boundary particles and {} bottom boundary particles".format(top_count, bottom_count))



top_mask = np.array([b.extra(1) == 1 for b in balls.list()])
bottom_mask  = np.array([b.extra(1) == 2 for b in balls.list()])
boundary_mask = np.logical_or(top_mask, bottom_mask)



top_mask = np.array([b.extra(1) == 1 for b in balls.list()])
bottom_mask  = np.array([b.extra(1) == 2 for b in balls.list()])
boundary_mask = np.logical_or(top_mask, bottom_mask)

r"""Create some (empty) lists to store the time and unbalanced forces
during the UCS test. """

strain = []
stress = []



top_mask = np.array([b.extra(1) == 1 for b in balls.list()])
bottom_mask  = np.array([b.extra(1) == 2 for b in balls.list()])
boundary_mask = np.logical_or(top_mask, bottom_mask)

r"""Create some (empty) lists to store the time and unbalanced forces
during the UCS test. """

strain = []
stress = []

r"""We use the matplotlib.pylab module to create a plot of the stress versus strain response of the model
during the UCS test. """

import matplotlib.pylab as plt

area = box_len**2
plt.plot(strain, stress)
plt.title("Stress vs Strain")
plt.xlabel("Strain [%]")
plt.ylabel("Stress [MPa]")
plt.grid(True)
plt.draw()



def store_force(*args):
    """This function is called during |pfc| cycling to record the stress
    strain curve.
    """
    if it.cycle() % 100: return

    strain.append(vel*it.mech_age()*100.0/box_len)
    stress.append(abs(ba.force_unbal()[boundary_mask][:,2]).sum()/2.0/area/1e6)
    plt.gca().clear()
    plt.xlabel("Strain [%]")
    plt.ylabel("Stress [MPa]")
    plt.grid(True)
    plt.plot(strain, stress)
    plt.draw()

it.set_callback("store_force", 43.0)



it.command("model cycle 40000")



speak = np.amax(stress)
ipeak = np.argmax(stress)
epeak = strain[ipeak]/100.0
i50 = int(0.5*ipeak)
s50 = stress[i50]*1e6
e50 = strain[i50]/100.0
emod50 = s50 / e50 / 1e9

txtE = r'$E_{{50}}={:.1f} GPa$'.format(emod50)
txtS = r'$UCS = {:.1f} MPa$'.format(speak)

plt.text(0.25*100*e50,0.5*speak, txtE,fontsize=12)
plt.text(0.75*100*epeak,1.01*speak, txtS,fontsize=12)
plt.draw()
plt.savefig('p3d-test-ucs.png')
plt.close('all')



