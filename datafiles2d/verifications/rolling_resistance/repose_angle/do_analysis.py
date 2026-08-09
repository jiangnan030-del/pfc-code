#===========================================================================
# do_analysis.py
#===========================================================================
import itasca

fric  = [0.25,0.5]
rfric = [0.05,0.1,0.25,0.5,0.6]

for f in fric:
  for rf in rfric:
    itasca.command("""
                     model restore 'system_ini'
                     [fric  = {0}]
                     [rfric = {1}]
                     program call 'move_container.p2dat'
                   """.format(f,rf)
    )

#===========================================================================
# eof: do_analysis.py
