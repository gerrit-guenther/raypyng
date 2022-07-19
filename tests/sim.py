from RayPyNG.rml import RMLFile
from RayPyNG.simulate import Simulate
from RayPyNG.simulate import SimulationParams
import numpy as np

sim = Simulate('examples/rml/high_energy_branch_flux_1200.rml',template='examples/rml/high_energy_branch_flux_1200.rml', hide=True)
rml = sim.rml
sp = SimulationParams(rml) # epxands to rml_list/params_list, now aware of runner


params = [  
            # set two parameters: "alpha" and "beta" in a dependent way. 
            {rml.beamline.M1.grazingIncAngle:np.array([1,2]), rml.beamline.M1.longRadius:[0,180], rml.beamline.Dipole.photonEnergy:[1000,2000]}, 
            # set a range of  values - in independed way
            {rml.beamline.M1.exitArmLengthMer:range(19400,19501, 100)},
            # set a value - in independed way
            {rml.beamline.M1.exitArmLengthSag:np.array([100])}
        ]



params = [  
            # set two parameters: "alpha" and "beta" in a dependent way. 
            {rml.beamline.Dipole.photonEnergy:np.arange(100,2000,100)}, 
            # set a range of  values - in independed way
            {rml.beamline.ExitSlit.totalHeight:0.05},
            # set a value - in independed way
            {rml.beamline.Dipole.numberRays:5000}
        ]


sp.params=params

# sim.simulation_folder = '/home/simone/Documents/RAYPYNG/raypyng/test'
sim.simulation_name = 'test'

# repeat the simulations as many time as needed
sim.repeat = 1

#this is defined at the current working directory by default
#sim.path = '/home/simone/Documents/RAYPYNG/raypyng' 

# this is defined as RAYPy_simulation by default
#sim.prefix = 'asdasd_'

# analyze:
# sim.analyze = True
# # This must be a list of dictionaries
# sim.exports  =  [{rml.beamline.Dipole:'ScalarBeamProperties'},
#                  {rml.beamline.DetectorAtFocus:['ScalarElementProperties','ScalarBeamProperties']}
#                 ]


sim.analyze = False
# This must be a list of dictionaries
sim.exports  =  [{rml.beamline.Dipole:'RawRaysOutgoing'},
                 {rml.beamline.DetectorAtFocus:['RawRaysOutgoing']}
                ]

# params must be an instance of SimulationsParams
sim.params=sp 

# create the rml files
sim.rml_list()


#sim.check_simulations(force=True)

#uncomment to run the simulations
#sim.run(force=True)
#uncomment to run the simulations
sim.run_mp(number_of_cpus=1,force=False)





# test resolving power simulations
#sim._RP_simulation(rml.beamline.Dipole, np.arange(1000,1101,50), rml.beamline.DetectorAtFocus)

# to run the script
# PYTHONPATH=. python tests/sim.py


        