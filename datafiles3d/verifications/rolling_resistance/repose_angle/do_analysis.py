import itasca

fric  = [0.2,0.6]
rfric = [0.1,0.2,0.4,0.6,0.8]

for f in fric:
  for rf in rfric:
    itasca.command("""
                     model restore \'system_ini\'
                     [fric  = {0}]
                     [rfric = {1}]
                     program call \'move_container\' suppress
                   """.format(f,rf)
    )