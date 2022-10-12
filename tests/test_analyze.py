from raypyng import Simulate, multiprocessing
import numpy as np
import os

this_file_dir=os.path.dirname(os.path.realpath(__file__))
rml_file = os.path.join(this_file_dir,'rml/high_energy_branch_flux_1200.rml')

sim = Simulate(rml_file, hide=True)

rml=sim.rml
elisa = sim.rml.beamline
#sp = SimulationParams(rml) 



# define the values of the parameters to scan 
energy    = np.arange(200, 10201,1000)
SlitSize  = np.array([0.1])
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
#sp.params=params

#and then plug them into the Simulation class
sim.params=params

# sim.simulation_folder = '/home/simone/Documents/RAYPYNG/raypyng/test'
sim.simulation_name = 'test_noAnalyze'

# repeat the simulations as many time as needed
sim.repeat = 1

sim.analyze = True
## This must be a list of dictionaries
sim.exports  =  [{elisa.Dipole:'ScalarBeamProperties'},
                {elisa.DetectorAtFocus:['ScalarElementProperties','ScalarBeamProperties']}
                ]


# create the rml files
#sim.rml_list()

#uncomment to run the simulations
#sim.run(multiprocessing=5, force=True)
sim.run(multiprocessing=5, force=False)
#sim.run(force=True)



        