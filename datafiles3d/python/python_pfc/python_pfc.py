
import itasca as it



it.command("python-reset-state false")



it.command("""
model new
model domain extent -5e-2 6e-2 -6e-2 5e-2 -5e-2 5e-2
model cmat default model linear property kn 1e1 dp_nratio 0.2
ball generate cubic box -0.02375 0.02375 rad 1.25e-3
ball attr dens 2600
""")



it.ball.count()



ball = it.ball.find(1)
print(ball)



ball.radius()



radius_sum = 0.0
for b in it.ball.list():
  radius_sum += b.radius()



print(radius_sum)
print(ball.radius() * it.ball.count())



it.command("model cycle 1")



b = it.ball.near((0,0,0))



b.pos()



len(b.contacts())



for c in b.contacts():
    print("contact with id: {} at {}".format(c.id(), c.pos()))



c = b.contacts()[0]



c.force_global()



c.props()



c.props()['fric']




c.prop('fric')



c.set_prop('fric', 0.5)
print(c.prop('fric'))



print(c.end1())
print(c.end2())




print(c.end1() == b)
print(c.end2() == b)



neighbor_list = [c.end1() if c.end2() == b else c.end2() for c in b.contacts()]

print("central ball id: {}, position: {}".format(b.id(), b.pos()))
print
for i, neighbor in enumerate(neighbor_list):
    print("neighbor ball {} id: {}, position: {}".format(i,
                                                         neighbor.id(),
                                                         neighbor.pos()))



it.command("""
model new
model domain extent -1 1 -1 1 -1 1
model cmat default model linear property kn 1e1 dp_nratio 0.2
""")

from vec import vec

origin = vec((0.0, 0.0, 0.0))
rad = 0.1
eps = 0.001

b1 = it.ball.create(rad, origin)
b2 = it.ball.create(rad, origin + (rad-eps, 0, 0))
# create a third ball close enough to generate a virtual contact
b3 = it.ball.create(rad, origin + (rad*3 + eps, 0, 0))

it.command("""
ball attribute density 1200
wall create vertices  ...
   -{rad} -{rad} -{rad} ...
   {rad} -{rad} -{rad} ...
   {rad} {rad} -{rad}
model cycle 1
""".format(rad=rad))



for c in it.contact.list():
    print(c)



for c in it.contact.list(all=True):
    print(c)



c1, c2, c3, c4 = tuple(it.contact.list(all=True))

print(type(c1) is it.BallBallContact)
print(type(c1) is it.BallFacetContact)
print(type(c3) is it.BallFacetContact)



for c in it.contact.list(type=it.BallBallContact, all=True):
    print(c)



i=0
def my_callback(*args):
    global i
    i += 1
    print("in Python callback function.")

it.set_callback("my_callback", -1)
it.command("model cycle 5")
print("The Python callback function was called {} times".format(i))

it.remove_callback("my_callback",-1)
i=0
it.command("model cycle 5")
print("The Python callback function was called {} times".format(i))



