import itasca as it 
import math
import numpy as np
from vec import vec3 

it.command("""
    model new
    model restore \'ini.sav\'
    python-reset-state off
      """)

f1=it.dfn.fracture.find(1)
f2=it.dfn.fracture.find(2)


# find normals to the fractures 
n1=f1.normal()
n2=f2.normal()

#Normal orientated to the interior of the bloc
if f1.normal_z()<0:
    n1=-n1
if f2.normal_z()<0:
    n2=-n2

#Apply Goodman and Shi theory

#Active force vector
WW=348.074          #find inertial mass from rigid block python object ???
A=vec3((0,0,-WW))

#Calculating the sliding direction
n12=n1.cross(n2)
s12=n12/n12.mag()*np.sign(n12.dot(A))

#Normal forces 
N1=-(A.cross(n2)).dot(n12)/(n12.mag())**2
N2=-(A.cross(n1)).dot(-n12)/(n12.mag())**2
#Shear force
T12=A.dot(s12)

# Critical friction angle (if zero cohesion)
fric_theory=math.atan(T12/(N1+N2))*180./math.pi
print("Analytical critical friction angle is "+str(fric_theory)+" degrees")
