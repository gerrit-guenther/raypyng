#from RayPyNG.rml import RMLFile
from RayPyNG.simulate import Simulate
from RayPyNG.simulate import SimulationParams
import numpy as np



sim = Simulate('examples/rml/high_energy_branch_flux_1200.rml',template='examples/rml/high_energy_branch_flux_1200.rml', hide=True)

rml=sim.rml
elisa = sim.rml.beamline
sp = SimulationParams(rml) 



# define the values of the parameters to scan 
energy    = np.arange(200, 2001,200)
SlitSize  = np.array([0.1,0.05])
cff       = np.array([2.25])
nrays     = 10000

# define a list of dictionaries with the parameters to scan
params = [  
            # set two parameters: "alpha" and "beta" in a dependent way. 
            {elisa.Dipole.photonEnergy:energy}, 
            # set a range of  values 
            {elisa.ExitSlit.totalHeight:SlitSize},
            # set values 
            {elisa.PG.cFactor:cff},
            {elisa.Dipole.numberRays:nrays}
        ]
# set the paramters in the siumulationParams class
sp.params=params

#and then plug them into the Simulation class
sim.params=sp 


# sim.simulation_folder = '/home/simone/Documents/RAYPYNG/raypyng/test'
sim.simulation_name = 'test'

# repeat the simulations as many time as needed
sim.repeat = 1

#this is defined at the current working directory by default
#sim.path = '/home/simone/Documents/RAYPYNG/raypyng' 

# this is defined as RAYPy_simulation by default
#sim.prefix = 'asdasd_'


# by default analyze is set to True
sim.analyze = True
# This must be a list of dictionaries [{element1:export1},{element2:export1,export2}] 
sim.exports  =  [{elisa.Dipole:'ScalarBeamProperties'},
                {elisa.DetectorAtFocus:['ScalarElementProperties','ScalarBeamProperties']}
                ]

# params must be an instance of SimulationsParams
#sim.params=sp 

# create the rml files
sim.rml_list()

#uncomment to run the simulations
sim.run_mp(number_of_cpus=5,force=False)


# to run the script
# PYTHONPATH=. python tests/test_simulation.py


        