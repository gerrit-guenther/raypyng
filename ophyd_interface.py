from turtle import pos

class RayPySignal(Signal):

    """
    to get the pzNGObj, we could look and see how the 
    EpicsSignal class gets the prefix from the parent Device
    """

    def __init__(self, name):

        self._name = name
        # need somthing to get the pyNGObj

    def set(self, value):
        # return done immediately
        # should set the value of the parameter defined by self._name

    def get(self): 

        # should get the value of the parameter defined by self._name





class Dipole(Device):

    numberRays = Cpt(RayPySignal, name="numberRays")
    sourceWidth = Cpt(RayPySignal, name="sourceWidth")

# Its the job of the RayPySignal to update the rml file through the RayPyNG package, return done immediately

dipole = Dipole(pyNGObj, name= "dipole")

class Detector(Device):

    """
    When triggered run the simulation, then send a signal when complete
    When read the last value from the simulation is returned.
    """


    __init__(self, pos):
        _pos=pos

    fwhm_v = Cpt(RORayPySignal, name="fwhm_v")# important that this name maps to what pyRayNg knows for a detector
    fwhm_h = Cpt(RORayPySignal, name="fwhm_h")

    def trigger(self):

        """
        will not trigger the simulation to be run using the state of the rml
        file defined by the other ophyd devices. Instead that should be 
        handled by some other device which could be injected into the Msg stream
        by a preprocessor. The Msg will trigger the simulation and when done, 
        update the status object of each of the individual detectors.

        This method returns a status object which reports done and success
        """
    
    def read(self):

        """
        returns the last value from the simlation
        """



end_det=Detector(pyNgObj, name="end_det", pos=-1)
....
....

#we need some thing that will trigger the simulation after all the detectors
#are triggered
RE(sim_scan([end_det,det1,det2],dipole.energy, start,stop, num))

    """
    scan_sim is for each motor and args stepping through args, running sim, waiting for new value, then reading detectors and generating docs
    """