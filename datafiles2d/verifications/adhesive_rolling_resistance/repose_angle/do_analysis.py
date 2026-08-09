#=============================================================================
# do_analysis.py
#=============================================================================
import itasca
itasca.command("python-reset-state off")

fric_list  = [0.5]
rfric_list = [0.1]
# F0_list is {0, 1, 5} times weight of single particle [N]
# D0_list is 100% of avg. particle radius [m]
F0_list = [0.0,0.14,0.7]
D0_list = [1.5e-3]

for f in fric_list:
  for rf in rfric_list:
    for myF0 in F0_list:
      for myD0 in D0_list:
        itasca.command("""
                         model restore \'init\'
                         [fric  = {0}]
                         [rfric = {1}]
                         [F0    = {2}]
                         [D0    = {3}]
                         program call \'move_container.p2dat\'
                       """.format(f,rf,myF0,myD0)
        )

#=============================================================================
# eof: do_analysis.py