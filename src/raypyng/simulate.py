from .rml import RMLFile
from .rml import ObjectElement,ParamElement, BeamlineElement
import itertools
import os 
import numpy as np
#from collections.abc import MutableMapping,MutableSequence
from .runner import RayUIAPI,RayUIRunner
from .recipes import SimulationRecipe
from .multiprocessing import RunPool
from .postprocessing import PostProcess

################################################################
class SimulationParams():
    def __init__(self, rml=None, param_list=None,**kwargs) -> None:
        if rml is not None:
            if isinstance(rml,RMLFile):
                self._rml = rml
            else: # assume that parameter is the file name as required for RMLFile
                self._rml = RMLFile(rml,**kwargs)
        else:
            raise Exception("rml file must be defined")
        
        self.param = param_list
        
    @property 
    def rml(self):
        return self._rml

    @property
    def params(self):       
        return self.param

    @params.setter
    def params(self,value):
        # self.param must be a list
        if not isinstance(value, list) == True:
            raise AssertionError('params must be a list')
        # every element in the list must be a dictionary
        for d in value:
            if not isinstance(d, dict):
                raise AssertionError('The elements of params must be dictionaries')
        # the items permitted types are:
        # int,float,str,np.array
        # a list of the types above
        # the output of range, that I still did not understand what it is
        # in any case at the end we want to have either
        # a list or a numpy array
        for d in value:
            for k in d.keys():
                if not isinstance(k,ParamElement):
                    raise AssertionError('The keys of the dictionaries must be instance of ParamElement, while ', k, 'is a ', str(type(k)))
                if isinstance(d[k], (list)):
                    pass
                elif isinstance(d[k], (float, int, str)):
                    d[k] = [d[k]]
                else: # this works with range output, but I would like to capture the type..
                    try:
                        d[k] = list(d[k])
                    except TypeError:
                        raise Exception('The only permitted type are: int, float, str, list, range, np.array, check',d[k]) 
        self.param = value
  
    def _check_param(self):
        """Check that self.param is a list of dictionaries, and convert the 
        items of the dictionaries to lists, otherwise raise an exception.
        """        
        
    def _extract_param(self, verbose:bool=False):
        """Parse self.param and extract dependent and independent parameters

        Args:
            verbose (bool, optional): If True print the returned objects. Defaults to False.

        Returns:
            self.ind_param_values (list): indieendent parameter values
            self.ind_par (list): independent parameters
            self.dep_param_dependency (dict): dictionary of dependencies
            self.dep_value_dependency (list): dictionaries of dependent values
            self.dep_par (list): dependent parameters

        """                 
        self.ind_param_values = []
        self.ind_par = []
        self.dep_param_dependency = {}
        self.dep_value_dependency = []
        self.dep_par = []
        # loop over the list of dictionaries
        for par in self.param:
            keys_par = list(par.keys())
            # if there is more than one key, we have an indipendent parameter
            # and one or more dependent parameters
            # the dependent param are keys, value and dependency are stored
            if len(keys_par) > 1:
                index_param  = 0
                for dep_param in keys_par:
                    if dep_param != keys_par[0]:
                        if len(par[dep_param]) != len(par[keys_par[0]]):
                            dep_param_string = dep_param.get_full_path().lstrip("lab.beamline.")
                            indep_param_string = keys_par[0].get_full_path().lstrip("lab.beamline.")
                            raise AssertionError ('The parameter {} has {} values, but since it depends on {} it \
                                should have the same number of values, {}'.format(dep_param_string,
                                                                                len(par[dep_param]),
                                                                                indep_param_string,
                                                                                len(par[keys_par[0]])))
                        index_values = 0
                        self.dep_param_dependency[dep_param] = keys_par[0]
                        for dep_value in par[dep_param]:
                            if index_values == 0:
                                self.dep_value_dependency.append({par[keys_par[0]][index_values]:dep_value})
                            else:
                                self.dep_value_dependency[index_param][par[keys_par[0]][index_values]]=dep_value
                            index_values += 1
                        index_param += 1
            # here we deal with the indipendent parameters
            self.ind_param_values.append(par[keys_par[0]])
            self.ind_par.append(keys_par[0])
            self.dep_par = list(self.dep_param_dependency.keys())
        if verbose:
            print('###########################################')
            print('self.ind_param_values', self.ind_param_values)
            print('self.ind_par', self.ind_par)
            print('###########################################')
            print('self.dep_param_dependency', self.dep_param_dependency)
            print('self.dep_value_dependency',self.dep_value_dependency)
        return (self.ind_param_values,self.ind_par,self.dep_param_dependency,self.dep_value_dependency,self.dep_par)

    def _make_dictionary(self, keys, items):
        d = {}
        for v,k in enumerate(keys):
            # it follows a dirty little trick to ensure that all the dictionry keys
            # are different
            k.cdata=v+3987.3423421534563632
            d.update({k:items[v]})
        return d

    def params_list(self, obj=None):
        result = []
        for i in self.simulations_param_list:
            result.append(self._make_dictionary(self.param_to_simulate, i))
        return result

    def _calc_loop(self, verbose:bool=True):
        """Calculate the simulations loop

        Returns:
            self.param_to_simulate (list): idependent and dependent parameters
            self.simulations_param_list (list): parameters values for each simulation loop
        """                
        self.param_to_simulate = self.ind_par + self.dep_par
        self.simulations_param_list = []
        # here we arrange the indipendent parameters in a grid
        self.loop = list(itertools.product(*self.ind_param_values))
        
        # work out where are the parameters on which the dependent parameters depends
        # make a copy of the dependency dictionary and replace the items with the index in the second step
        self.dep_param_dependency_index = []
        for ind,par in enumerate(self.dep_param_dependency.values()):
            index_par = self.ind_par.index(par)
            self.dep_param_dependency_index.append(index_par)

        # here we add the dependent parameters
        for count, loop in enumerate(self.loop):
            for ind,par in enumerate(self.dep_param_dependency.keys()):
                to_add = (self.dep_value_dependency[ind][loop[self.dep_param_dependency_index[ind]]],)
                loop = loop + to_add
            self.simulations_param_list.append(loop)
        self.par = self.ind_par + self.dep_par
        if verbose:
            print('You have defined:')
            print(len(self.ind_par), ' independent parameters')
            print(len(self.ind_par), ' dependent parameters or set parameters')
            print(len(self.simulations_param_list), ' simulations')
        return (self.param_to_simulate, self.simulations_param_list)
    
    def _check_if_enabled(self, param):
        """Check if a parameter is enabled

        Args:
            param (RML object): an parameter to simulate

        Returns:
            (bool): True if the parameter is enabled, False otherwise
        """        
        return param.enabled=='T'
    
    def _enable_param(self, param):
        """Set enabled to True in a beamline object, and auto to False

        Args:
            param (RML object): beamline object
        """        
        if not self._check_if_enabled(param):
            param.enabled = 'T'
        try:
            param.auto = 'F'
        except AttributeError:
            pass


    def _write_value_to_param(self, param, value):
        """Write a value to a parameter, making sure enable is T 
        and auto is F

        Args:
            param (RML object): beamline object
            value (str,int,float): the value to set the beamline object to
        """        
        self._enable_param(param)
        if not isinstance(value,str):
            value = str(value)
        param.cdata = value

################################################################
class Simulate():
    """class to simulate 
    """
    def __init__(self, rml=None, hide=False,**kwargs) -> None:
        """_summary_

        Args:
            rml (_type_, optional): Rml file with the beamline template. Defaults to None.
            hide (bool, optional): force hiding of GUI leftovers. Defaults to False.

        Raises:
            Exception: _description_
        """
        if rml is not None:
            if isinstance(rml,RMLFile):
                self._rml = rml
            else: # assume that parameter is the file name as required for RMLFile
                self._rml = RMLFile(None,template=rml)
        else:
            raise Exception("rml file must be defined")
        self.path   = None
        self.prefix = 'RAYPy_Simulation'
        self._hide = hide
        self.analyze = True
        self._repeat = 1

    @property
    def possible_exports(self):
        self._possible_exports = ['AnglePhiDistribution',
                                'AnglePsiDistribution',
                                'BeamPropertiesPlotSnapshot',
                                'EnergyDistribution',
                                'FootprintAbsorbedRays',
                                'FootprintAllRays',
                                'FootprintOutgoingRays',
                                'FootprintPlotSnapshot',
                                'FootprintWastedRays',
                                'IntensityPlotSnapshot',
                                'IntensityX',
                                'IntensityYZ',
                                'PathlengthDistribution',
                                'RawRaysBeam',
                                'RawRaysIncoming',
                                'RawRaysOutgoing',
                                'ScalarBeamProperties',
                                'ScalarElementProperties'
                             ]
        return self._possible_exports
    
    @property
    def possible_exports_without_analysis(self):
        self._possible_exports_without_analysis = ['RawRaysIncoming',
                                'RawRaysOutgoing'
                             ]
        return self._possible_exports_without_analysis

    @property 
    def rml(self):
        return self._rml

    @property 
    def simulation_name(self):
        return self._simulation_name
    
    @simulation_name.setter
    def simulation_name(self,value):
        self._simulation_name = value

    @property 
    def analyze(self):
        return self._analyze
    
    @analyze.setter
    def analyze(self,value):
        if not isinstance(value, bool):
            raise ValueError ('Only bool are allowed')
        self._analyze = value
        
    @property 
    def repeat(self):
        return self._repeat
    
    @repeat.setter
    def repeat(self,value):
        if not isinstance(value, int):
            raise ValueError ('Only int are allowed')
        self._repeat = value

    @property 
    def path(self):
        return self._path

    @path.setter
    def path(self,value):
        if value == None:
            value=os.getcwd()
        if not isinstance(value, str):
            raise ValueError ('Only str are allowed')
        if not os.path.exists(value):
            raise ValueError('The path does not exist')
        self._path = value

    @property 
    def prefix(self):
        return self._prefix

    @prefix.setter
    def prefix(self,value):
        if not isinstance(value, str):
            raise ValueError ('Only str are allowed')
        self._prefix = value

    @property 
    def exports(self):
        return self._exports

    @exports.setter
    def exports(self,value):
        if not isinstance(value, list):
            raise AssertionError ('The exports must be a list, while it is a '+str(type(value)), value)
        for d in value:
            if not isinstance(d,dict):
                raise AssertionError('The element of the list must be dictionaries, while I found a '+str(type(d)), d)
            for k in d.keys():
                if not isinstance(k,ObjectElement):
                    raise AssertionError('The keys of the dictionaries must be instance of ObjectElement, while ', k, 'is a ', str(type(k)))
                if isinstance(d[k], str):
                    if self.analyze:
                        possible_exports = self.possible_exports
                    else: 
                        possible_exports = self.possible_exports_without_analysis
                    if d[k] not in possible_exports:
                        raise AssertionError('It is not possible to export {}, check the spelling. The possible files to exports are {}'.format(d[k],possible_exports))
                elif isinstance(d[k], list):
                    for dd in d[k]:
                        if dd not in self.possible_exports and self._analyze==True:
                            raise AssertionError('It is not possible to export this file. The possible files to exports are ', self.possible_exports)
                        elif dd not in self.possible_exports_without_analysis and self._analyze==False:
                            raise AssertionError('It is not possible to export this file. The possible files to exports are ', self.possible_exports)

        self._exports = value
        self._exports_list = self.compose_exports_list(value, verbose=False)
        
    @property
    def params(self):       
        return self.param

    @params.setter
    def params(self,value):
        if not isinstance(value, SimulationParams):
            #raise AssertionError('Params must be an instance of SimulationParams, while it is', type(params))
            sp = SimulationParams(self.rml)
            sp.params = value
            self.sp = sp
        else:
            self.sp = value
        _ = self.sp._extract_param(verbose=False)
        _ =self.sp._calc_loop()

    def rml_list(self):    
        result = []
        self.sim_list_path = []
        self.sim_path = os.path.join(self.path, self.prefix+'_'+self.simulation_name)
        # check if simulation folder exists, otherwise create it
        if not os.path.exists(self.sim_path):
            os.makedirs(self.sim_path)
        for r in range(0,self.repeat):
            sim_folder = os.path.join(self.sim_path,'round_'+str(r))
            if not os.path.exists(sim_folder):
                os.makedirs(sim_folder)
            for sim_n,param_set in enumerate(self.sp.params_list()):
                rml_path = os.path.join(sim_folder,str(sim_n)+'_'+self.simulation_name+'.rml')
                for param,value in param_set.items():
                    self.sp._write_value_to_param(param,value)
                self.rml.write(rml_path)
                self.sim_list_path.append(rml_path)
                # is this gonna create problems if I have millions of simulations?
                result.append(RMLFile(rml_path))

            # create csv file with simulations recap
            #print("DEBUG::",sim_folder)
            with open(os.path.join(sim_folder,'looper.csv'), 'w') as f:
                header = 'n '
                for par in self.sp.param_to_simulate:
                    #header = header + '\t'+str(par.id)#get_full_path().lstrip("lab.beamline."))
                    header = header + '\t'+str(par.get_full_path().lstrip("lab.beamline."))
                header += '\n'
                f.write(header)
                for ind,par in enumerate(self.sp.simulations_param_list):
                    line = ''
                    line += str(ind)+'\t'
                    for value in par:
                        line += str(value)+'\t'
                    f.write(line+'\n')  
        return result

    def compose_exports_list(self, exports_dict_list,/,verbose:bool=True):
        self.exports_list=[]
        for i, d in enumerate(self.exports):
                for obj in d.keys():
                    if isinstance(d[obj], str):
                        self.exports_list.append((obj.attributes().original()['name'], d[obj]))
                    elif isinstance(d[obj], list):
                        for l in d[obj]:
                            self.exports_list.append((obj.attributes().original()['name'], l))
                    else: 
                        raise ValueError('The exported param can be only str or list of str.')
        if verbose:
            print('The following will be exported:')
            for d in self.exports_list:
                print(d[0], d[1])

    def check_simulations(self,/,verbose:bool=True, force:bool=False):
        if force: return {k:v for k,v in enumerate(self.rml_list())}
        missing_simulations={}
        for ind,simulation in enumerate(self.rml_list()):
            folder = os.path.dirname(self.sim_list_path[ind])
            filename = os.path.basename(self.sim_list_path[ind])
            sim_number = filename.split("_")[0]
            for d in self.exports_list:
                export = sim_number+'_'+d[0]+'-'+d[1]+'.csv'
                csv = os.path.join(folder,export)
                if not os.path.exists(csv):
                    missing_simulations[ind]=simulation
                    break
        if verbose:
            print('I still have ', len(missing_simulations), 'simulations to do!')
            #print('missing_simulations',missing_simulations)
        return missing_simulations

    def run(self,recipe=None,/,multiprocessing=True, force=False):#, **kwargs):
        if recipe is not None:
            if isinstance(recipe,SimulationRecipe):
                self.params = recipe.params(self)
                self.exports = recipe.exports(self)
                self.simulation_name = recipe.simulation_name(self)
            else:
                raise TypeError("Unsupported type of the recipe!")

        filenames_hide_analyze = []
        exports = []
        missing_simulations= self.check_simulations(force=force).items()
        for ind,rml in missing_simulations:
            filenames_hide_analyze.append([rml.filename, self._hide, self._analyze])
            sim_index = ind%int(len(missing_simulations)/self.repeat)
            exports.append(self.generate_export_params(sim_index,self.sim_list_path[ind]))
            rml.write()
        with RunPool(multiprocessing) as pool:
            pool.map(run_rml_func,zip(filenames_hide_analyze,exports))
        if len(missing_simulations) != 0 and self.analyze==False:
            pp = PostProcess()
            pp.cleanup(self.sim_path, self.repeat, self.exports_list)

    def generate_export_params(self,simulation_index,rml):
        folder = os.path.dirname(rml)
        #filename = os.path.basename(rml)
        #sim_number = filename.split("_")[0]
        return [ (d[0], d[1], folder, str(simulation_index)+'_') for d in self.exports_list]


    def beamwaist_simulation(self, energy:float,/,source:ObjectElement=None,nrays:int=None,sim_folder:str=None, force:bool=False):
        if not isinstance(energy, (int,float)):
           raise TypeError('The energy_range must be an a ragne or a numpy array, while it is a', type(energy_range))
        params = []
        # find source and add to param with defined user energy range
        found_source = False
        if source == None:
            for oe in self.rml.beamline._children:
                for par in oe:
                    try:
                        params.append({par.photonEnergy:energy})
                        if nrays != None:
                            params.append({par.numberRays:nrays})
                        found_source = True
                        break
                    except:
                        pass
        else:
            params.append({source.photonEnergy:energy})
            if nrays != None:
                params.append({source.numberRays:nrays})
            found_source = True
        if found_source!=True:
            raise AttributeError('I did not find the source')
        
        # turn reflectivity of all elements off, grating eff to 100%
        for oe in self.rml.beamline._children:
                for par in oe:
                    try:
                        params.append({par.reflectivityType:0})
                    except:
                        pass
        sp = SimulationParams(self.rml)
        sp.params=params
        self.params=sp
        self.analyze = False
        # make a list of optical elements
        # exlude screens, that do not have misalignment param
        oe_list=[]
        for oe in self.rml.beamline._children:
            for par in oe:
                try:
                    par.alignmentError
                    oe_list.append(oe)
                except AttributeError:
                    pass
        exports = []
        for oe in oe_list:
            exports.append({oe:'RawRaysOutgoing'})
            # print('DEBUG:: exported oe', oe.name)
        self.exports = exports
        if sim_folder is None:
            self.simulation_name = 'Beamwaist'
        else: 
            self.simulation_name = sim_folder
        self.repeat = 1

        self.rml_list()
        self.run_mp(number_of_cpus=1,force=force)
         
def run_rml_func(_tuple):
    filenames_hide_analyze,exports = _tuple
    rml_filename = filenames_hide_analyze[0]
    hide         = filenames_hide_analyze[1]
    analyze      = filenames_hide_analyze[2]
    runner = RayUIRunner(hide=hide)
    api    = RayUIAPI(runner)
    pp     = PostProcess()
    runner.run()
    api.load(rml_filename)
    api.trace(analyze=analyze)
    for e in exports:
        api.export(*e)
        if analyze==False:
            pp.postprocess_RawRays(e[0], e[1], e[2], e[3])
    #time.sleep(0.1) # testing file creation issue
    try: 
        api.quit()
    except Exception as e:
        print("WARNING! Got exception while quitting ray, the error was:",e)
        pass
    #time.sleep(1) # testing file creation issue
    runner.kill()
    return None
