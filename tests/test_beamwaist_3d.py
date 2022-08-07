from RayPyNG.simulate import Simulate
from RayPyNG.beamwaist import PlotBeamwaist 


sim = Simulate('examples/rml/high_energy_branch_flux_1200_test_beamwaist.rml',
                template='examples/rml/high_energy_branch_flux_1200_test_beamwaist.rml', 
                hide=True)
sim_folder = 'Beamwaist_test'

bw = PlotBeamwaist(sim_folder, sim)

energy = 500
nrays = 10000
bw.simulate_beamline(energy,nrays=nrays, force=False)


bw.plot_3d()

