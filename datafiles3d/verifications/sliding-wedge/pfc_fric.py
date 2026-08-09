import itasca as it 
import math

fric_limit1 = 0.0
fric_limit2 = 90.

while True:

    it.command("""
    model new
    model restore \'ini.sav\'
    rblock attribute displacement 0
    rblock attribute velocity 0.
    rblock history name \'zdisp\' displacement-z id 6
    """)

    cycle_max = it.cycle() + 10000
  
    fric_angle = (fric_limit1 + fric_limit2)/2.
    it.command("""
                  [fric_angle = {}]
                  contact property fric [math.tan(fric_angle*math.pi/180.)])
                  model solve ratio-average 1e-6 cycles-total 10000
                  fish define isStable
                    isStable = false
                    if rblock.num == 4
                        if mech.cycle < 10000
                            isStable = true
                        endif
                    endif   
                  end
               """.format(fric_angle))
    
    if it.fish.call_function("isStable") is True: #stable
        fric_limit2 = fric_angle
        print("Stable for "+str(fric_angle) +" degrees")
        it.command("model save \'last_stable.sav\'")
    
    else : #unstable
        fric_limit1 = fric_angle
        print("Unstable for "+str(fric_angle) +" degrees")
        it.command("model save \'last_unstable.sav\'")
        
    #compute interval size
    min_interval = (fric_limit2 - fric_limit1)/2.
    if min_interval<0.001:
        break    
    
print("Last stable friction angle interval is ["
      + str("%.3f" % fric_limit1) +";"
      + str("%.3f" % fric_limit2)+"] (degrees)")
_error=abs(fric_limit2-fric_theory)/fric_theory*100.0
print("The error relative to the theoretical solution (" 
      + str("%.3f" % fric_theory)
      + ") is "+str("%.3f" % _error)+"%")
    