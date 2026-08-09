import utils
import matplotlib.pyplot as plt
fric  = [0.2,0.6]
rfric = [0.1,0.2,0.4,0.6,0.8]

val = []
conf = []
leg = []
for f in fric:
  ra = []
  ci = []
  for rf in rfric:
    p,c = utils.fit_cone('system_final-fric{0}-rfric{1}.p3sav'.format(f,rf))
    ra += [p]
    ci += [c]  
  val += [ra]
  conf += [ci] 
  leg += [r'$\mu={0}$'.format(f)]
  
plt.close('all')
for i, v in enumerate(val):
  plt.errorbar(rfric , val[i],yerr=ci[i])
plt.legend(leg,loc=2)
plt.title("Repose Angle vs Rolling Friction Coefficient")
plt.xlabel("Rolling Friction Coef. [-]")
plt.ylabel("Angle of Repose [$^{\circ}$]")
plt.axis([0, 0.9, 0, 40])
plt.grid(True)
plt.draw()
