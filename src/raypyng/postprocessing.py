from importlib.resources import path
import numpy as np
import os
import warnings
from natsort import natsorted, ns

from .rml import RMLFile


class PostProcess():
    """class to post-process the data. 
    At the moment works only if the exported data are RawRaysOutgoing
    """
    def __init__(self) -> None:
        self.format_saved_files = '.dat'
        self.source = None
        pass

    def _list_files(self,dir_path:str, end_filename:str):
        """List all the files in dir_path ending with end_filename

        Args:
            dir_path (str): path to a folder
            end_filename (str): the listed files end with end_filename

        Returns:
            res (list): list of files in dir_path ending eith end_filename
        """        
        # list to store files
        res = []
        for file in os.listdir(dir_path):
            # check only text files
            if file.endswith(end_filename):
                res.append(os.path.join(dir_path,file))
        return natsorted(res, alg=ns.IGNORECASE)

    def _extract_bandwidth_fwhm(self,rays_bw:np.array):
        """calculate the fwhm of the rays_bw.

        Args:
            rays_bw (np:array): the energy of the x-rays

        Returns:
            float: fwhm
        """        
        return 2.3555*np.std(rays_bw)

    def _extract_focus_fwhm(self,rays_pos:np.array):
        """calculate the fwhm of rays_pos

        Args:
            rays_pos (np.array): contains positions of the x-rays

        Returns:
            float: fwhm
        """        
        return 2.3555*np.std(rays_pos)

    def _extract_intensity(self,rays:np.array):
        """calculate how many rays there are

        Args:
            rays (np.array): contains rays information
        """        
        return(rays.shape[0])
    
    def _save_file(self, filename:str, array:np.array, header:str=None):
        """This function is used to save files, 

        Args:
            filename (str): file name(path)
            array (np.array): array to save 
            header (str): header for the file
        """        
        if header != None:
            np.savetxt(filename+self.format_saved_files,array, header=header)
        else:
            np.savetxt(filename+self.format_saved_files,array)

    def _load_file(self,filepath):
        """Load a .npy file and returns the array

        Args:
            filepath (str): the path to the file to load

        Returns:
            arr (np.array): The loaded numpy array
        """        
        arr = np.loadtxt(filepath)
        return arr
    
    def extract_nrays_from_source(self, rml_filename):
        """Extract photon flux from rml file, find source automatically

        Args:
            rml_filename (str): the rml file to use to extract the photon flux

        Returns:
            str: the photon flux
        """        
        s = RMLFile(rml_filename)
        for oe in s.beamline.children():
                if hasattr(oe,"photonFlux"):
                    self.source = oe
                    break
        return self.source.photonFlux.cdata, self.source.numberRays.cdata
    
    def postprocess_RawRays(self,exported_element:str=None, exported_object:str=None, dir_path:str=None, sim_number:str=None, rml_filename:str=None):
        """The method looks in the folder dir_path for a file with the filename:
        filename = os.path.join(dir_path,sim_number+exported_element + '-' + exported_object+'.csv')
        for each file it calculates the number of rays, the bandwidth, and the horizontal and vertical focus size,
        it saves it in an array that is composed by [n_rays,bandwidth,hor_focus,vert_focus], that is then saved to
        os.path.join(dir_path, sim_number+exported_element+'_analyzed_rays.npy')
        Args:
            exported_element (list, optional): a list of containing the exported elements name as str. Defaults to None.
            exported_object (str, optional): the exported opbject, tested only with RawRaysOutgoing. Defaults to None.
            dir_path (str, optional): the folder where the file to process is located. Defaults to None.
            sim_number (str, optional): the prefix of the file, that is the simulation number with a _prepended, ie "0_". Defaults to None.
        """        
        source_photon_flux, source_n_rays  = self.extract_nrays_from_source(rml_filename)
        
        source_photon_flux = float(source_photon_flux)
        source_n_rays      = float(source_n_rays)
        filename = os.path.join(dir_path,sim_number+exported_element + '-' + exported_object+'.csv')
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            rays = np.loadtxt(filename, skiprows=2)
        ray_properties = np.zeros((7,1))
        if rays.shape[0]==0: # if no rays survived
            # source photon flux
            ray_properties[0] = source_photon_flux
            pass
        elif rays.shape[0]==15: # if only one ray survived
            # source photon flux
            ray_properties[0] = source_photon_flux
            # number of rays reaching the oe
            ray_properties[1] = 1
            # percentage of survived photons
            ray_properties[2] = ray_properties[1]/source_n_rays*100
            # photon flux reaching the oe
            ray_properties[3] = source_photon_flux/100*ray_properties[2]
            # bandwidth of the rays reaching the OE
            ray_properties[4] = self._extract_bandwidth_fwhm(rays[9])
            # horizontal focus
            ray_properties[5] = self._extract_focus_fwhm(rays[3])
            # vertical focus
            ray_properties[6] = self._extract_focus_fwhm(rays[4])
        else:
            # source photon flux
            ray_properties[0] = source_photon_flux
            # number of rays reaching the oe
            ray_properties[1] = self._extract_intensity(rays)
            # percentage of survived photons
            ray_properties[2] = ray_properties[1]/source_n_rays*100
            # photon flux reaching the oe
            ray_properties[3] = source_photon_flux/100*ray_properties[2]
            # bandwidth of the rays reaching the oe
            ray_properties[4] = self._extract_bandwidth_fwhm(rays[:,9])
            # horizontal focus
            ray_properties[5] = self._extract_focus_fwhm(rays[:,3])
            # vertical focus
            ray_properties[6] = self._extract_focus_fwhm(rays[:,4])
        
        new_filename = os.path.join(dir_path, sim_number+exported_element+'_analyzed_rays')
        self._save_file(new_filename, ray_properties)
        return 

    def cleanup(self,dir_path:str=None, repeat:int=1, exp_elements:list=None):
        """This functions reads all the temporary files created by self.postptocess_RawRays()
        saves one file for each exported element in dir_path, and deletes the temporary files.
        If more than one round of simulations was done, the values are averaged.

        Args:
            dir_path (str, optional): The path to the folder to cleanup. Defaults to None.
            repeat (int, optional): number of rounds of simulations. Defaults to 1.
            exp_elements (list, optional): the exported elements names as str. Defaults to None.
        """        
        header = "SourcePhotonFlux\t\t NumberRaysSurvived\t\t  PercentageRaysSurvived   PhotonFlux\t\t\t\tBandwidth\t\t\t\t HorizontalFocusFWHM\t  VerticalFocusFWHM"
        for d in exp_elements:
            for r in range(repeat):
                dir_path_round=os.path.join(dir_path,"round_"+str(r))
                files = self._list_files(dir_path_round, d[0]+"_analyzed_rays"+self.format_saved_files)
                for f_ind, f in enumerate(files):
                    if r == 0 and f_ind==0:
                        analyzed_rays = self._load_file(f)
                        analyzed_rays = np.reshape(analyzed_rays,(1,analyzed_rays.shape[0]))
                    elif r==0 and f_ind!=0:
                        tmp=self._load_file(f)
                        tmp = np.reshape(tmp,(1,tmp.shape[0]))
                        analyzed_rays = np.concatenate((analyzed_rays, tmp), axis=0)
                    elif r>=1:
                        tmp=self._load_file(f)
                        tmp=tmp.reshape((tmp.shape[0]))
                        analyzed_rays[f_ind,:] += tmp
                    else:
                        pass
            fn = os.path.join(dir_path, d[0])
            analyzed_rays = analyzed_rays/repeat
            self._save_file(fn,analyzed_rays,header=header)



