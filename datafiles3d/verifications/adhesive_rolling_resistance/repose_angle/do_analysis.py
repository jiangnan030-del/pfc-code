#=============================================================================
# do_analysis.py
#=============================================================================
import itasca
itasca.command("python-reset-state off")
fric_list  = [0.5]
rfric_list = [0.1]
# F0 is {0, 1, 5} times weight of single particle [N]
# D0 is 5% of avg. particle radius [m]
F0_list = [0.0, 2.2e-3, 1.1e-2]
D0_list = [1.5e-4]

for f in fric_list:
  for rf in rfric_list:
    for myF0 in F0_list:
      for myD0 in D0_list:
        itasca.command("""
                         model restore 'init'
                         [fric  = {0}]
                         [rfric = {1}]
                         [F0    = {2}]
                         [D0    = {3}]
                         program call 'move_container.p3dat'
                       """.format(f,rf,myF0,myD0)
        )

#=============================================================================
# eof: do_analysis.py