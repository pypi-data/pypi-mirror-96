# -*- coding: utf-8 -*-
global sourcedir
sourcedir = None

import os
import sys
import numpy as np
import glob
import netCDF4 as nc
import exoplasim.gcmt
import exoplasim.randomcontinents
import exoplasim.makestellarspec
import platform

smws = {'mH2': 2.01588,
        'mHe': 4.002602,
        'mN2': 28.0134,
        'mO2': 31.9988,
        'mCO2':44.01,
        'mAr': 39.948,
        'mNe': 20.1797,
        'mKr': 83.798,
        'mH2O':18.01528}

gases_default = {'pH2': 0.0,
                'pHe': 5.24e-6,
                'pN2': 0.78084,
                'pO2': 0.20946,
                'pCO2':330.0e-6,
                'pAr': 9.34e-3,
                'pNe': 18.18e-6,
                'pKr': 1.14e-6,
                'pH2O':0.01}

def _noneparse(text,dtype):
    if text=="None" or text=="none":
        return None
    else:
        return dtype(text)
    
#def readsourcepath():
    #with open("sourcepath","r") as sf:
        #spth = sf.read()
        #if spth.strip()=="None":
            #sourcedir=None
        #else:
            #sourcedir=spth.strip()
            
    #return sourcedir

class Model(object):
    """Create an ExoPlaSim model in a particular directory.
            
    Initialize an ExoPlaSim model in a particular directory. 
    If the necessary executable does not yet exist, compile it.

    Parameters
    ----------
    resolution : str, optional
        The resolution of the model. Options are T21, T42, T63, T85, 
        T106, T127, and T170, corresponding to 32, 64, 96, 128, 160, 
        192, and 256 latitudes respectively, and twice as many 
        longitudes. ExoPlaSim has been tested and validated most 
        extensively at T21 and T42. Higher resolutions will take 
        considerable time to run.
    layers : int, optional
        The number of vertical layers in the model atmosphere. The default
        is 10, but PlaSim has been used with 5 layers in many studies.
        More layers are supported, but not recommended except at higher
        resolutions.
    ncpus : int, optional
        The number of MPI processes to use, typically the number of cores
        available. If ncpus=1, MPI will not be used.
    precision : int, optional
        Either 4 or 8--specifies the number of bytes for a Fortran real.
    debug : bool, optional
        If True, compiler optimizations are disabled
        and the code is compiled with debugging flags enabled that will
        allow line-by-line tracebacks if ExoPlaSim crashes. Only use for
        development purposes.
    inityear : int, optional
        The number to use for the initial model year (default 0).
    recompile : bool, optional
        True/False flag used to force a recompile. Cannot force the 
        model to skip compilation if the executable does not exist or
        compilation-inducing flags are set.
    optimization : str, optional
        Fortran compiler arguments for optimization. ANY compiler
        flags can be passed here, but it's intended for optimization
        flags. Setting this will trigger a recompile.
    mars : bool, optional
        True/False. If True, will use Mars-specific routines.
    workdir : str, optional
        The directory in which to construct the model.
    source : str, optional
        The directory in which to look for executables, namelists, 
        boundary conditions, etc. If not set, will default to exoplasim/plasim/run/.        
    modelname : str, optional 
        The name to use for the model and its output files when finished.
        
    Returns
    -------
    Model
        An instantiated Model object that resides in a directory with the namelists
        and executable necessary to run ExoPlaSim.
        
    Examples
    --------

    >>> import exoplasim as exo
    >>> mymodel = exo.Model(workdir="mymodel_testrun",modelname="mymodel",resolution="T21",layers=10,ncpus=8)
    >>> mymodel.configure()
    >>> mymodel.exportcfg()
    >>> mymodel.run(years=100,crashifbroken=True)
    >>> mymodel.finalize("mymodel_output")

    In this example, we initialize a model that will run in the directory
    "mymodel_testrun", and has the name "mymodel", which will be used to
    label output and error logs. The model has T21 resolution, or 32x64,
    10 layers, and will run on 8 CPUs. By default, the compiler will use
    8-byte precision. 4-byte may run slightly faster, but possibly at the
    cost of reduced stability. If there are machine-specific optimization
    flags you would like to use when compiling, you may specify them as a
    string to the optimization argument, e.g. ``optimization='mavx'``. ExoPlaSim
    will check to see if an appropriate executable has already been created,
    and if not (or if flags indicating special compiler behavior such as 
    debug=True or an optimization flag are set) it will compile one. We then
    configure the model with all the default parameter choices, which means
    we will get a model of Earth. We then export the model configurations
    to a ``.cfg`` file (named automatically after the model), which will allow
    the model configuration to be recreated exactly by other users. We 
    run the model for 100 years, with error-handling enabled. Finally, we 
    tell the model to clean up after itself. It will take the most recent 
    output files and rename them after the model name we chose, and delete 
    all the intermediate output and configuration files.
    

    """
    def __init__(self,resolution="T21",layers=10,ncpus=4,precision=8,debug=False,inityear=0,
                recompile=False,optimization=None,mars=False,workdir="most",source=None,
                modelname="MOST_EXP"):
        
        global sourcedir
        
        if not sourcedir: #This means we haven't run yet, and have some post-install work to do
            os.system('spth=$(python%s -c "import exoplasim as exo; print(exo.__path__)") && echo $spth>sourcepath'%sys.version[0])
            with open("sourcepath","r") as spf:
                sourcedir = spf.read().strip()
                if sourcedir[0]=="[":
                    sourcedir=sourcedir[1:]
                if sourcedir[-1]=="]":
                    sourcedir=sourcedir[:-1]
                if sourcedir[0]=="'":
                    sourcedir=sourcedir[1:]
                if sourcedir[-1]=="'":
                    sourcedir=sourcedir[:-1]
            os.system("rm sourcepath")
            with open("%s/__init__.py"%sourcedir,"r") as sourcef:
                sourcecode = sourcef.read().split('\n')
            sourcecode[2] = 'sourcedir = "%s"'%sourcedir
            sourcecode = '\n'.join(sourcecode)
            #os.system("cp %s/__init__.py %s/preinit.py"%(sourcedir,sourcedir))
            try:
                with open("%s/__init__.py"%sourcedir,"w") as sourcef:
                    sourcef.write(sourcecode)
                cwd = os.getcwd()
                os.chdir(sourcedir)
                os.system("./configure.sh")
                os.system("nc-config --version > ncversion.tmp")
                with open("ncversion.tmp","r") as ncftmpf:
                    version = float('.'.join(ncftmpf.read().split()[1].split('.')[:2]))
                if version>4.2:
                    os.system("cd postprocessor && ./build_init.sh || ./build_init_compatibility.sh")
                else:
                    os.system("cd postprocessor && rm burn7.x && make")
                os.chdir(cwd)
            except PermissionError:
                raise PermissionError("\nHi! Welcome to ExoPlaSim. It looks like this is the first "+
                                    "time you're using this program since installing, and you "+
                                    "may have installed it to a location that needs root "+
                                    "privileges to modify. This is not ideal! If you want to "+
                                    "use the program this way, you will need to run python code"+
                                    " that uses ExoPlaSim with sudo privileges; i.e. sudo "+
                                    "python3 myscript.py. If you did this because pip install "+
                                    "breaks without sudo privileges, then try using \n\n\tpip "+ "install --user exoplasim \n\ninstead. It is generally a "+
                                    "very bad idea to install things with sudo pip install.")
        
        self.runscript=None
        self.otherargs = {}
        self.pgases = {}
        self.modelname=modelname
        self.cleaned=False
        self.recursecheck=False
        
        if debug or optimization: #There is no need to set these for precompiled binaries
            recompile=True
        
        self.ncpus = ncpus
        if self.ncpus>1:
            self._exec = "mpiexec -np %d "%self.ncpus
        else:
            self._exec = "./"
        self.layers = layers
        
        self.odir = os.getcwd()
        if workdir[0]!="/":
            workdir = self.odir+"/"+workdir
        self.workdir = workdir
        if os.path.isfile(self.workdir): #Linux can't have file and directory of same name
            self.workdir += "_dir"
        os.system("mkdir %s/"%self.workdir)
        self.currentyear=inityear
        
        # Depending on how the user has entered the resolution, set the appropriate number
        # of spectral modes and latitudes
        if resolution=="T21" or resolution=="t21" or resolution==21 or resolution==32:
            self.nsp=21
            self.nlats=32
        elif resolution=="T42" or resolution=="t42" or resolution==42 or resolution==64:
            self.nsp=42
            self.nlats=64
        elif resolution=="T63" or resolution=="t63" or resolution==63 or resolution==96:
            self.nsp=63
            self.nlats=96
        elif resolution=="T85" or resolution=="t85" or resolution==85 or resolution==128:
            self.nsp=85
            self.nlats=128
        elif resolution=="T106" or resolution=="T106" or resolution==106 or resolution==160:
            self.nsp=106
            self.nlats=160
        elif resolution=="T127" or resolution=="t127" or resolution==127 or resolution==192:
            self.nsp=127
            self.nlats=192
        elif resolution=="T170" or resolution=="t170" or resolution==170 or resolution==256:
            self.nsp=170
            self.nlats=256
        else:
            raise ValueError("Resolution unsupported. ExoPlaSim supports T21, T42, T63, T85, "+
                            "T106, T127, and T170 (32, 64, 96, 128, 160, 192, and 256 "+
                            "latitudes respectively")
        
        # If the executable does not exist, then regardless of whether we've been asked
        # to recompile, we'll have to recompile
        
        if not source:
            source = "%s/plasim/run"%sourcedir
        
        self.executable = source+"/most_plasim_t%d_l%d_p%d.x"%(self.nsp,self.layers,ncpus)
        
        burnsource = "%s/postprocessor"%sourcedir
        
        print("Checking for %s...."%self.executable)
        
        if recompile or not os.path.exists(self.executable):
            extraflags = ""
            if debug:
                extraflags+= "-d "
            if optimization:
                extraflags+= "-O %s"%optimization
            if mars:
                extraflags+= "-m "
            os.system("cwd=$(pwd) && "+
                    "cd %s && ./compile.sh -n %d -p %d -r T%d -v %d "%(sourcedir,self.ncpus,
                                                                        precision,self.nsp,
                                                                        self.layers)+
                    extraflags+" &&"+
                    "cd $cwd")
        
        os.system("cp %s/* %s/"%(source,self.workdir))
        os.system("cp %s/burn7.x %s/"%(burnsource,self.workdir))
        
        #Copy the executable to the working directory, and then CD there
        os.system("cp %s %s"%(self.executable,self.workdir))
        #os.chdir(self.workdir)
        
        self.executable = self.executable.split("/")[-1] #Strip off all the preceding path
        
        os.chdir(self.workdir)
        os.chdir("..")
        self.crashdir = os.getcwd()+"/"+self.modelname
        self.secondarydir = None
        os.chdir(self.odir)
    
        
    def run(self,**kwargs):
        """Run the Model's designated run routine.

        This may have been passed as runscript when the model was
        created, or it could be the model's internal ._run() routine. 
        That method takes the following arguments:

        Parameters
        ----------
        years : int, optional
            Number of years to run    
        postprocess : bool, optional
            True/False. Whether or not NetCDF files should be produced on-the-fly
        crashifbroken : bool, optional
            True/False. If True, use Pythonic error handling    
        clean : bool, optional
            True/False. If True, delete raw output files once NetCDF files are made
            
        """
        if not self.runscript:
            self._run(**kwargs)
        else:
            try:
                self.runscript(self,**kwargs) #runscript MUST accept a Model object as the first arg
            except Exception as e:
                print(e)
                self._crash()
    
    def _checktimes(self):
        """Get list of durations for each year computed so far."""
        diagfiles = sorted(glob.glob(self.workdir+"/*DIAG*"))
        times = []
        for df in diagfiles:
            with open(df,"r") as diagf:
                diag = diagf.read().split("\n")
            elapsed=1.0e6 #Assume a large value so we stop if there's a problem.
            found=False
            for ln in range(len(diag)-1,-1,-1):
                if "Seconds per sim year" in diag[ln]:
                    elapsed = float(diag[ln].split(":")[1].split("*")[0].strip()) #seconds
                    found=True
                    break
            if not found:
                for ln in range(len(diag)-1,-1,-1):
                    if "Minutes per sim year" in diag[ln]:
                        try:
                            elapsed =diag[ln].split('year')
                            elapsed = elapsed[1].split("*")
                            elapsed = elapsed[0].strip()
                            elapsed = float(elapsed)*60.0 
                                                                                #seconds
                        except:
                            raise 
                        found=True
                        break
                
            times.append(elapsed/60.0)
        return times
            
    
    def _checktime(self,year=-1):
        """Get walltime duration for a given year of output."""
        diagfiles = sorted(glob.glob(self.workdir+"/*DIAG*"))
        recent = diagfiles[year]
        with open(recent,"r") as diagf:
            diag = diagf.read().split("\n")
        elapsed=1.0e6 #Assume a large value so we stop if there's a problem.
        found=False
        for ln in range(len(diag)-1,-1,-1):
            if "Seconds per sim year" in diag[ln]:
                elapsed = float(diag[ln].split(":")[1].split("*")[0].strip()) #seconds
                found=True
                break
        if not found:
            for ln in range(len(diag)-1,-1,-1):
                if "Minutes per sim year" in diag[ln]:
                    elapsed = float(diag[ln].split(":")[1].split("*")[0].strip())*60.0 
                                                                            #seconds
                    found=True
                    break
        return elapsed/60.0 #convert to minutes
        
        
    def runtobalance(self,threshold = None,baseline=50,maxyears=300,minyears=75,
                    timelimit=None,crashifbroken=True,clean=True):
        """ Run the model until energy balance equilibrium is reached at the top and surface.
            
        Parameters
        ----------
        threshold : float, optional
            If specified, overrides the threshold set by ``.config()``. The model will run
            until the energy balance at the top and surface drifts by less than this
            amount per year over a given baseline.
        baseline : int, optional
            The number of years over which to evaluate energy balance drift. Default 50
        maxyears : int, optional
            The maximum number of years to run before returning. Default 300. This is
            useful if you are running on a scratch disk with limited space.
        minyears : int, optional
            The minimum number of years to run before determining that the model is in
            equilibrium.
        timelimit : float, optional
            If set, maxyears will be revised each year based on the average minutes
            per year thus far, to try to avoid going over the time limit, which should
            be given in minutes.
        crashifbroken : bool, optional
            True/False. If True, Pythonic error handling is enabled. Default True.
        clean : bool, optional
            True/False. If True, raw output is deleted once postprocessed. Default True.

        Returns
        -------
        bool
            True if the model reached equilibrium, False if not.
        """
        runlimit = self.currentyear+maxyears
        if threshold:
            self.threshold = threshold
        ogrunlimit = runlimit
        ogminyears = minyears
        runstart = self.currentyear
        if os.getcwd()!=self.workdir:
            os.chdir(self.workdir)
        os.system("mkdir snapshots")
        if self.highcadence["toggle"]:
            os.system("mkdir highcadence")
        os.system("rm %s/runtimes.log"%self.workdir) #We only want runtimes for this run
            
            
        #Not balanced, but have run more than minyears: (True+False)*True= True
        #Not balanced, have run less than minyears:     (True+True)*True = True
        #Not balanced, but ran more than runlimit:      (True+False)*False=False
        #Balanced, but run fewer than minyears:         (False+True)*True= True
        #Balanced, and ran more than minyears:          (False+False)*True=False
        while (not self._isbalanced(threshold=self.threshold,baseline=baseline) \
                or self.currentyear<minyears) and self.currentyear<runlimit:
            dataname="MOST.%05d"%self.currentyear
            snapname="MOST_SNAP.%05d"%self.currentyear
            hcname  ="MOST_HC.%05d"%self.currentyear
            diagname="MOST_DIAG.%05d"%self.currentyear
            restname="MOST_REST.%05d"%self.currentyear
            snowname="MOST_SNOW.%05d"%self.currentyear
            stormname="MOST.%05d.STORM"%self.currentyear
            
            #Run ExoPlaSim
            os.system(self._exec+self.executable)
            
            #Sort, categorize, and arrange the various outputs
            os.system("[ -e restart_dsnow ] && rm restart_dsnow")
            print("[ -e restart_dsnow ] && rm restart_dsnow")
            os.system("[ -e restart_xsnow ] && rm restart_xsnow")
            print("[ -e restart_xsnow ] && rm restart_xsnow")
            os.system("[ -e Abort_Message ] && exit 1")
            print("[ -e Abort_Message ] && exit 1")
            os.system("[ -e plasim_output ] && mv plasim_output "+dataname)
            print("[ -e plasim_output ] && mv plasim_output "+dataname)
            os.system("[ -e plasim_snapshot ] && mv plasim_snapshot "+snapname)
            print("[ -e plasim_snapshot ] && mv plasim_snapshot "+snapname)
            if self.highcadence["toggle"]:
                os.system("[ -e plasim_hcadence ] && mv plasim_hcadence "+hcname)
                print("[ -e plasim_hcadence ] && mv plasim_hcadence "+hcname)
            os.system("[ -e plasim_diag ] && mv plasim_diag "+diagname)
            print("[ -e plasim_diag ] && mv plasim_diag "+diagname)
            os.system("[ -e plasim_status ] && cp plasim_status plasim_restart")
            print("[ -e plasim_status ] && cp plasim_status plasim_restart")
            os.system("[ -e plasim_status ] && mv plasim_status "+restname)
            print("[ -e plasim_status ] && mv plasim_status "+restname)
            os.system("[ -e restart_snow ] && mv restart_snow "+snowname)
            print("[ -e restart_snow ] && mv restart_snow "+snowname)
            os.system("[ -e hurricane_indicators ] && mv hurricane_indicators "+stormname)
            print("[ -e hurricane_indicators ] && mv hurricane_indicators "+stormname)
            
            #Do any additional work
            timeavg=0
            snapsht=0
            highcdn=0
            try:
                timeavg=self.postprocess(dataname,"example.nl",
                                        log="burnout",crashifbroken=crashifbroken)
                snapsht=self.postprocess(snapname,"snapshot.nl",
                                        log="snapout",crashifbroken=crashifbroken)
                os.system("mv %s.nc snapshots/"%snapname)
                if self.highcadence["toggle"]:
                    highcdn=self.postprocess(hcname  ,"snapshot.nl",
                                            log="hcout"  ,crashifbroken=crashifbroken)
                    os.system("mv %s.nc highcadence/"%hcname)
            except Exception as e:
                print(e)
                self._crash()
            if clean:
                if timeavg:
                    os.system("rm %s"%dataname)
                if snapsht:
                    os.system("rm %s"%snapname)
                if highcdn:
                    os.system("rm %s"%hcname)
                   
            if os.path.exists("Abort_Message"): #We need to stop RIGHT NOW
                self._crash() 
                
            if crashifbroken: #Check to see that we aren't throwing NaNs
                try:
                    check=self.integritycheck(dataname+".nc")
                except Exception as e:
                    print(e)
                    self._crash()
            
            print("Finished Year %d With No Problems"%self.currentyear)
            self.currentyear += 1
            sb = self.getbalance("hfns")
            tb = self.getbalance("ntr")
            os.system("echo '%02.6f  %02.6f'>>%s/balance.log"%(sb,tb,self.workdir))
            
            if timelimit:
                avgyear = self._checktimes() #get how long it took to run each year
                os.system("echo '%1.3f minutes'>>%s/runtimes.log"%(avgyear[-1],self.workdir))
                currentyears = np.loadtxt("%s/runtimes.log"%self.workdir,usecols=[0,]) 
                     #^Get how long it took to run each year of the current run
                currentavgyear = np.nanmean(currentyears) 
                     #^Average walltime per year for this run
                runlimit = min(runstart + int(timelimit//currentavgyear),ogrunlimit)
                crunlimit = min(int(timelimit//currentavgyear),ogrunlimit-runstart)
                            #options for the runlimit are N0+T/tau, where tau is avg year
                os.system("echo 'limit to %d years total; %d years this run'>>%s/limits.log"%(runlimit,crunlimit,self.workdir))
                minyears = min(ogminyears,runlimit)
            
            
        bott = self.gethistory(key="hfns")
        topt = self.gethistory(key="ntr")
        with open("%s/shistory.pso"%self.workdir,"a+") as f:
            text='\n'+'\n'.join(bott.astype(str))
            f.write(text)
        with open("%s/toahistory.pso"%self.workdir,"a+") as f:
            text='\n'+'\n'.join(topt.astype(str))
            f.write(text)
        finished = self._isbalanced(threshold=self.threshold,baseline=baseline)
        finished *= (self.currentyear>ogminyears) #Must be both
        if not finished:
            return False
        return True
    
            
    def getbalance(self,key,year=-1):
        """Return the global annual mean of a given variable for a given year
            
        Parameters
        ----------
        key : str
            The output variable string to return
        year : int, optional
            Which year to go to for output
            
        Returns
        -------
        float
            Global annual mean of requested quantity
        """
        var = self.inspect(key,savg=True,tavg=True,year=year)
        return var
    
    def gethistory(self,key="ts",mean=True,layer=-1):
        """Return the an array of global annual means of a given variable for each year
            
        Parameters
        ----------
        key : str, optional
            The output variable string to return
        mean : bool, optional
            Toggle whether we return the mean or the sum
        year : int, optional
            Which year to go to for output
            
        Returns
        -------
        numpy.ndarray
            1-D Array of global annual means
        """
        files = sorted(glob.glob("%s/MOST*.nc"%self.workdir))
        dd=np.zeros(len(files))
        for n in range(0,len(files)):
            ncd = nc.Dataset(files[n])
            variable = ncd.variables[key][:]
            lon = ncd.variables['lon'][:]
            lat = ncd.variables['lat'][:]
            if len(variable.shape)>3:
                variable = variable[:,layer,:,:]
            dd[n] = gcmt.spatialmath(variable,lon=lon,lat=lat,
                                    mean=mean,radius=self.radius)
            ncd.close()
        return dd
    
    
    def _isbalanced(self,threshold = 5.0e-4,baseline=50):
        """Return whether or not the model is in energy balance equilibrium

        Parameters
        ----------
        threshold : float, optional
            The maximum annual energetic drift allowed on the given baseline in W/m\ :math:`^2`
        baseline : int, optional
            The number of years over which to assess energy balance
            
        Returns
        -------
        bool
            Whether or not the model is in energy balance equilibrium
        """
        nfiles = len((glob.glob("%s/MOST*.nc"%self.workdir)))
        if nfiles==0: #For when the run restarts and there are no netcdf files yet
            return False
        prior=False
        if len(glob.glob(self.workdir+"/toahistory.ps*"))>0:
            try:
                toahistory = np.loadtxt(self.workdir+"/toahistory.pso")
                nfiles+=len(toahistory)
                shistory = np.loadtxt(self.workdir+"/shistory.pso")
                prior=True
            except:
                pass
        sbalance = np.zeros(nfiles)
        toabalance=np.zeros(nfiles)
        nstart=0
        if prior:
            sbalance[:len(toahistory)] = shistory[:]
            toabalance[:len(toahistory)] = toahistory[:]
            nstart = len(toahistory)
        if self.currentyear < baseline: #Run for minimum of baseline years
            return False
        else:
            for n in range(nstart,self.currentyear):
                topt = self.getbalance("ntr",year=n)
                bott = self.getbalance("hfns",year=n)
                sbalance[n] = bott
                toabalance[n] = topt
            savgs = []
            tavgs = []
            for n in range(9,len(sbalance)):
                savgs.append(abs(np.mean(sbalance[n-9:n+1]))) #10-year average energy balance
                tavgs.append(abs(np.mean(toabalance[n-9:n+1])))
            sslopes = []
            tslopes = []
            for n in range(4,len(savgs)): #5-baseline slopes in distance from energy balance
                sslopes.append(np.polyfit(np.arange(5)+1,savgs[n-4:n+1],1)[0])
                tslopes.append(np.polyfit(np.arange(5)+1,tavgs[n-4:n+1],1)[0])
            savgslope = abs(np.mean(sslopes[-30:])) #30-year average of 5-year slopes  
            tavgslope = abs(np.mean(tslopes[-30:]))
            os.system("echo '%02.8f  %02.8f'>>%s/slopes.log"%(savgslope,tavgslope,self.workdir))
            if savgslope<threshold and tavgslope<threshold: #Both TOA and Surface are changing at average 
                return True                                  # of <0.5 mW/m^2/yr on 45-year baselines
            else:
                return False
        
    def _run(self,years=1,postprocess=True,crashifbroken=False,clean=True):
        """Run the model for a set number of years.

        Parameters
        ----------
        years : int, optional
            Number of years to run    
        postprocess : bool, optional
            True/False. Whether or not NetCDF files should be produced on-the-fly
        crashifbroken : bool, optional
            True/False. If True, use Pythonic error handling    
        clean : bool, optional
            True/False. If True, delete raw output files once NetCDF files are made
            

        """
        if os.getcwd()!=self.workdir:
            os.chdir(self.workdir)
        os.system("mkdir snapshots")
        if self.highcadence["toggle"]:
            os.system("mkdir highcadence")
        for year in range(years):
            dataname="MOST.%05d"%self.currentyear
            snapname="MOST_SNAP.%05d"%self.currentyear
            hcname  ="MOST_HC.%05d"%self.currentyear
            diagname="MOST_DIAG.%05d"%self.currentyear
            restname="MOST_REST.%05d"%self.currentyear
            snowname="MOST_SNOW.%05d"%self.currentyear
            stormname="MOST.%05d.STORM"%self.currentyear
            
            #Run ExoPlaSim
            os.system(self._exec+self.executable)
            
            #Sort, categorize, and arrange the various outputs
            os.system("[ -e restart_dsnow ] && rm restart_dsnow")
            os.system("[ -e restart_xsnow ] && rm restart_xsnow")
            os.system("[ -e Abort_Message ] && exit 1")
            os.system("[ -e plasim_output ] && mv plasim_output "+dataname)
            os.system("[ -e plasim_snapshot ] && mv plasim_snapshot "+snapname)
            if self.highcadence["toggle"]:
                os.system("[ -e plasim_hcadence ] && mv plasim_hcadence "+hcname)
            os.system("[ -e plasim_diag ] && mv plasim_diag "+diagname)
            os.system("[ -e plasim_status ] && cp plasim_status plasim_restart")
            os.system("[ -e plasim_status ] && mv plasim_status "+restname)
            os.system("[ -e restart_snow ] && mv restart_snow "+snowname)
            os.system("[ -e hurricane_indicators ] && mv hurricane_indicators "+stormname)
            
            #Do any additional work
            timeavg=0
            snapsht=0
            highcdn=0
            if postprocess:
                try:
                    timeavg=self.postprocess(dataname,"example.nl",
                                            log="burnout",crashifbroken=crashifbroken)
                    snapsht=self.postprocess(snapname,"snapshot.nl",
                                            log="snapout",crashifbroken=crashifbroken)
                    os.system("mv %s.nc snapshots/"%snapname)
                    if self.highcadence["toggle"]:
                        highcdn=self.postprocess(hcname  ,"snapshot.nl",
                                                log="hcout"  ,crashifbroken=crashifbroken)
                        os.system("mv %s.nc highcadence/"%hcname)
                except Exception as e:
                    print(e)
                    self._crash()
            if clean:
                if timeavg:
                    os.system("rm %s"%dataname)
                if snapsht:
                    os.system("rm %s"%snapname)
                if highcdn:
                    os.system("rm %s"%hcname)
                    
            if os.path.exists("Abort_Message"): #We need to stop RIGHT NOW
                self._crash()
                
            if crashifbroken: #Check to see that we aren't throwing NaNs
                try:
                    check=self.integritycheck(dataname+".nc")
                except Exception as e:
                    print(e)
                    self._crash()
                
            self.currentyear += 1
    
    def postprocess(self,inputfile,namelist,log="postprocess.log",crashifbroken=False):
        """    Produce NetCDF output from an input file, using a specified postprocessing namelist. 

        Parameters
        ----------
        inputfile : str
            The raw output file to be processed
        namelist : str 
            The burn7 namelist to use
        log : str, optional
            The log file to which burn7 should output standard output and errors
        crashifbroken : bool, optional 
            True/False. If True, exoplasim will run .integritycheck() on the file.

        Returns
        -------
        int
            1 if successful, 0 if not
        """
        stat=os.system("./burn7.x -n<%s>%s %s %s.nc"%(namelist,log,inputfile,inputfile))
        if stat==0:
            print("NetCDF output written to %s.nc; log written to %s"%(inputfile,log))
            self.recursecheck=False
            return 1
        else:
            if crashifbroken:
                if not self.recursecheck:
                    if self.integritycheck("%s.nc"%inputfile):
                        self.recursecheck=True
                        print("burn7 threw some errors; may want to check %s"%log)
                    else:
                        raise RuntimeError("Error writing output to %s.nc; "%inputfile +
                                            "log written to %s"%log)
                else:
                    raise RuntimeError("An error was encountered, likely with the postprocessor. ExoPlaSim was unable to investigate further due to a recursion trap.")
            else:
                print("Error writing output to %s.nc; log written to %s"%(inputfile,log))
                raise RuntimeError("Going to stop here just in case......")
            return 0
        
    def integritycheck(self,ncfile): #MUST pass a NetCDF file that contains surface temperature
        """    Check an output file to see it contains the expected variables and isn't full of NaNs.
            
        If the file does not exist, exoplasim will attempt to create it using the postprocessor.
        If the file does not have the expected variables or is full of trash, an exception will
        be raised. If the file is fine, this function returns a 1. If the file did not exist and
        cannot be created, this function will return a 0. 
            
        Parameters
        ----------
        ncfile : str 
            The output file to check.
            
        Returns
        -------
        int
            0 or 1 depending on failure or success respectively
        """
        if os.getcwd()!=self.workdir:
            os.chdir(self.workdir)
        ioe=1
        if not os.path.exists(ncfile): #If the specified output file does not exist, create it
            if not self.recursecheck:
                ioe = self.postprocess(ncfile[:-3],"example.nl",crashifbroken=False)
                self.recursecheck=True
        if ioe:
            ncd = nc.Dataset(ncfile,"r")
            try:
                ts = ncd.variables["ts"][:]
            except:
                raise RuntimeError("Output is missing surface temperature; check logs for errors")
            if np.sum(np.isnan(ts))+np.sum(np.isinf(ts)) > 0.5:
                raise RuntimeError("Non-finite values found in surface temperature")
            self.recursecheck=False
            return 1
        else:
            return 0
                
    def finalize(self,outputdir,allyears=False,keeprestarts=False,clean=True):
        """Move outputs and optionally restarts to a specified output directory. 
            
        If more than the final year of output is being kept, a folder will be created in the output directory using the model name. Otherwise, finalized files will be renamed using the model name.

        Parameters
        ----------
        outputdir : str
            Directory in which to put output.
        allyears : bool, optional
            True/False. If True, output from all years will be kept, in a directory in
            outputdir named with the model name. Otherwise, the most recent year will be
            kept in outputdir, using the model name. Default False.
        keeprestarts : bool, optional
            True/False: If True, restart files will be kept as well as output files.
            Default False.
        clean : bool, optional
            True/False. If True, the original working directory will be deleted after files
            are moved. Default True.

        """
        
        if outputdir[0]!="/" and outputdir[0]!="~":
            cwd = os.getcwd()
            os.chdir(self.workdir)
            os.chdir("..")
            nwd = os.getcwd()
            outputdir = nwd+"/"+outputdir
            os.chdir(cwd)
        if not os.path.isdir(outputdir):
            os.system("mkdir %s"%outputdir)
        if allyears:
            os.chdir(outputdir)
            os.system("mkdir %s"%self.modelname)
            os.system("cp %s/MOST*.nc %s/"%(self.workdir,self.modelname))
            if self.snapshots:
                os.system("cp -r %s/snapshots %s/snapshots"%(self.workdir,self.modelname))
            if self.highcadence['toggle']:
                os.system("cp -r %s/highcadence %s/highcadence"%(self.workdir,self.modelname))
            os.system("cp %s/MOST*DIAG* %s/"%(self.workdir,self.modelname))
            if keeprestarts:
                os.system("cp %s/MOST_REST* %s/"%(self.workdir,self.modelname))
            #else:
            #    restarts = sorted(glob.glob("%s/MOST_REST*"%self.workdir))
            #    os.system("cp %s %s/%s_restart"%(restarts[-1],
            #                                        self.modelname,self.modelname))
            newworkdir = os.getcwd()+"/"+self.modelname
        else:
            outputs = sorted(glob.glob("%s/MOST*.nc"%self.workdir))
            os.chdir(outputdir)
            os.system("cp %s %s.nc"%(outputs[-1],self.modelname))
            diags = sorted(glob.glob("%s/MOST*DIAG*"%self.workdir))
            os.system("cp %s %s.DIAG"%(diags[-1],self.modelname))
            if self.snapshots:
                snps = sorted(glob.glob("%s/snapshots/*.nc"%self.workdir))
                os.system("cp %s %s_snapshot.nc"%(snps[-1],self.modelname))
            if self.highcadence["toggle"]:
                hcs = sorted(glob.glob("%s/highcadence/MOST*.nc"%self.workdir))
                os.system("cp %s %s_highcadence.nc"%(hcs[-1],self.modelname))
            if keeprestarts:
                rsts = sorted(glob.glob("%s/MOST_REST*"%self.workdir))
                os.system("cp %s %s_restart"%(rsts[-1],self.modelname))
            if clean:
                newworkdir = os.getcwd()
                self.cleaned=True
        os.system("cp %s/*.cfg %s/"%(self.workdir,outputdir))
        if clean:
            os.system("rm -rf %s"%self.workdir)
            self.workdir = newworkdir
                
    
    def get(self,year,snapshot=False,highcadence=False):
        """Return an open NetCDF data object for the given year. Defaults is to return time-averaged output.

        Parameters
        ----------
        year : int 
            Integer year of output to return
        snapshot: bool, optional
            True/False. If True, return the snapshot version.
        highcadence: bool, optional
            True/False. If True, return the high-cadence version.

        Returns
        -------
        netCDF4.Dataset
            An open netCDF4 data opject
        """
        #Note: if the work directory has been cleaned out, only the final year will be returned.
        if snapshot and not highcadence:
            name = "snapshots/MOST_SNAP.%05d.nc"%year
        elif highcadence and not snapshot:
            name = "highcadence/MOST_HC.%05d.nc"%year
        else:
            name = "MOST.%05d.nc"%year
        if self.cleaned:
            if snapshot and not highcadence:
                name = "%s_snapshot.nc"%self.modelname
            elif highcadence and not snapshot:
                name = "%s_highcadence.nc"%self.modelname
            else:
                name = "%s.nc"%self.modelname
        if os.path.exists(self.workdir+"/"+name):
            ncd = nc.Dataset(self.workdir+"/"+name,"r")
            return ncd
        else:
            raise RuntimeError("Output file %s not found."%(self.workdir+"/"+name))
    
    def inspect(self,variable,year=-1,ignoreNaNs=True,snapshot=False,
                highcadence=False,savg=False,tavg=False,layer=None):
        """Return a given output variable from a given year, with optional averaging parameters.

        Parameters
        ----------
        variable : str
            The name of the variable to return.
        year : int, optional
            Which year of output to return. Year indexing follows Pythonic rules. If the model
            has been finalized, only the final year of output will be returned.
        ignoreNaNs : bool, optional
            True/False. If True, use NaN-tolerant numpy functions.
        snapshot : bool, optional
            True/False. If True, use snapshot output instead of time-averaged.
        highcadence : bool, optional
            True/False. If True, use high-cadednce output instead of time-averaged.
        savg : bool, optional
            True/False. If True, compute the spatial average. Default False
        tavg : bool, optional
            True/False. If True, compute the annual average. Default False
        layer : int, optional
            If specified and data has 3 spatial dimensions, extract the specified layer. If
            unspecified and data has 3 spatial dimensions, the vertical dimension will be
            preserved (even if spatial averages are being computed).

        Returns
        -------
        float or numpy.ndarray
            The requested data, averaged if that was requested.

        """
        #Note: if the work directory has been cleaned out, only the final year will be returned.
        if snapshot and not highcadence:
            pattern = "snapshots/MOST_SNAP"
        elif highcadence and not snapshot:
            pattern = "highcadence/MOST_HC"
        else:
            pattern = "MOST"
        
        if ignoreNaNs:
            meanop = np.nanmean
        else:
            meanop = np.mean
        
        if year<0:
            #nfiles = len(glob.glob(self.workdir+"/"+pattern+"*.nc"))
            #year = nfiles+year
            year += self.currentyear #year=-1 should give the most recent year
    
        ncd = self.get(year,snapshot=snapshot,highcadence=highcadence)
        
        var = ncd.variables[variable][:]
        
        if variable!="lat" and variable!="lon" and variable!="lev" and variable!="time":
            lon = ncd.variables['lon'][:]
            lat = ncd.variables['lat'][:]
            lev = ncd.variables['lev'][:]
            if not savg and not tavg:
                if type(layer)!=type(None) and len(var.shape)==4:
                    return var[:,layer,:,:]
                return var
            elif tavg and not savg:
                if type(layer)!=type(None) and len(var.shape)==4:
                    return meanop(var[:,layer,:,:],axis=0)
                return meanop(var,axis=0)
            elif tavg and savg:
                if type(layer)!=type(None) and len(var.shape)==4: #3D spatial array, plus time
                #We're going to get a scalar; user has specified a level
                    return gcmt.spatialmath(var,lat=lat,lon=lon,ignoreNaNs=ignoreNaNs,lev=layer)
                elif type(layer)==type(None) and len(var.shape)==4:
                    #We're going to get a 1D vertical profile where each layer is a spatial avg
                    output = np.zeros(lev.shape)
                    for l in range(len(lev)):
                        output[l] = gcmt.spatialmath(var,lat=lat,lon=lon,
                                                    ignoreNaNs=ignoreNaNs,lev=l)
                    return output
                elif len(var.shape)==3: #2D spatial array, plus time
                    return gcmt.spatialmath(var,lat=lat,lon=lon,ignoreNaNs=ignoreNaNs)
            else:
                if type(layer)!=type(None) and len(var.shape)==4: #3D spatial array, plus time
                #We're going to get a 1D array; user has specified a level
                    output = np.zeros(var.shape[0])
                    for t in range(len(output)):
                        output[t] = gcmt.spatialmath(var,lat=lat,lon=lon,ignoreNaNs=ignoreNaNs,
                                                    lev=layer,time=t)
                    return output
                elif type(layer)==type(None) and len(var.shape)==4:
                    #We're going to get a 1D vertical profile plus time
                    output = np.zeros((var.shape[0],len(lev)))
                    for t in range(var.shape[0]):
                        for l in range(len(lev)):
                            output[t,l] = gcmt.spatialmath(var,lat=lat,lon=lon,time=t,
                                                    ignoreNaNs=ignoreNaNs,lev=l)
                    return output
                elif len(var.shape)==3: #2D spatial array, plus time
                    #We're going to get a 1D array
                    output = np.zeros(var.shape[0])
                    for t in range(len(output)):
                        output[t] = gcmt.spatialmath(var,lat=lat,lon=lon,
                                                    time=t,ignoreNaNs=ignoreNaNs)
                    return output
                else:
                    return -1
        else:
            return var
                
    
    def _crash(self):
        """Crash and burn. But gracefully."""
        os.chdir(self.workdir)
        os.chdir("..")
        os.system("mkdir %s_crashed"%self.crashdir)
        if self.secondarydir:
            os.system("mv %s/* %s_crashed/"%(self.secondarydir,self.crashdir))
        os.system("mv %s/* %s_crashed/"%(self.workdir,self.crashdir))
        raise RuntimeError("ExoPlaSim has crashed or begun producing garbage. All working files have been moved to %s_crashed/"%(os.getcwd()+"/"+self.modelname))
        
    def emergencyabort(self):
        """A problem has been encountered by an external script, and the model needs to crash gracefully"""
        self._crash()
    
    def configure(self,noutput=True,flux=1367.0,startemp=None,starspec=None,pH2=None,
            pHe=None,pN2=None,pO2=None,pCO2=None,pAr=None,pNe=None,
            pKr=None,pH2O=None,gascon=None,pressure=None,pressurebroaden=True,
            vtype=0,rotationperiod=1.0,synchronous=False,substellarlon=180.0,
            year=None,glaciers={"toggle":False,"mindepth":2.0,"initialh":-1.0},
            restartfile=None,gravity=9.80665,radius=1.0,eccentricity=None,
            obliquity=None,lonvernaleq=None,fixedorbit=False,orography=None,
            seaice=True,co2weathering=False,evolveco2=False,physicsfilter=None,
            filterkappa=8.0,filterpower=8,filterLHN0=15.0,diffusionwaven=None,
            qdiffusion=None,tdiffusion=None,zdiffusion=None,ddiffusion=None,
            diffusionpower=None,erosionsupplylimit=None,outgassing=50.0,snowicealbedo=None,
            twobandalbedo=False,maxsnow=None,soilalbedo=None,oceanalbedo=None,
            oceanzenith="ECHAM-3",wetsoil=False,soilwatercap=None,aquaplanet=False,
            desertplanet=False,soilsaturation=None,drycore=False,ozone=True,
            cpsoil=None,soildepth=1.0,mldepth=50.0,tlcontrast=0.0,desync=0.0,
            writefrequency=None,modeltop=None,stratosphere=False,top_restoretime=None,
            tropopause=None,timestep=45.0,runscript=None,columnmode=None,runsteps=None,
            highcadence={"toggle":0,"start":320,"end":576,"interval":4},
            snapshots=None,resources=[],landmap=None,stormclim=False,nstorms=4,
            stormcapture={"VITHRESH":0.145,"GPITHRESH":0.37,"VMXTHRESH":33.0,
                            "LAVTHRESH":1.2e-5,"VRMTHRESH":0.577,"MINSURFTEMP":298.15,
                            "MAXSURFTEMP":373.15,"WINDTHRESH":33.0,"SWINDTHRESH":20.5,
                            "SIZETHRESH":30,"ENDTHRESH":16,"MINSTORMLEN":256,
                            "MAXSTORMLEN":1024,"NKTRIGGER":0,"toggle":0},
            topomap=None,threshold=5.0e-4,otherargs={}):
        """Configure the model's namelists and boundary conditions.
        
        The defaults here are appropriate for an Earth model.
                
    **Model Operation**
    
            noutput : bool, optional 
               True/False. Whether or not model output should be written.
               restartfile: Path to a restart file to use for initial conditions. Can be None.
            writefrequency : int, optional 
               How many times per day ExoPlaSim should write output. Ignored by
               default--default is to write time-averaged output once every 5 days.
            timestep : float, optional 
               Model timestep. Defaults to 45 minutes.
            runscript : function , optional
               A Python function that accepts a Model object as its first argument. This
               is the routine that will be run when you issue the Model.run() command.
               Any keyword arguments passed to run() will be forwarded to the specified
               function. If not set, the default internal routine will be used.
            snapshots : int, optional 
               How many timesteps should elapse between snapshot outputs. If not set,
               no snapshots will be written.
            highcadence : dict, optional 
               A dictionary containing the following arguments:
               
                ``'toggle'`` : {0,1}
                    Whether or not high-cadence output should be written (1=yes).
                ``'start'`` : int
                    Timestep at which high-cadence output should begin.
                ``'end'`` : int
                    Timestep at which high-cadence output should end.
                ``'interval'`` : int
                    How many timesteps should elapse between high-cadence outputs.
            threshold : float, optional 
               Energy balance threshold model should run to, if using :py:func:`runtobalance() <exoplasim.Model.runtobalance>`.
               Default is <0.05 W/m\ :math:`^2`\ /yr average drift in TOA and surface energy balance
               over 45-year timescales.
            resources : list, optional 
               A list of paths to any additional files that should be available in the
               run directory.
            runsteps : integer, optional
               The number of timesteps to run each 'year'. By default, this is tuned to 360 Earth days. If set, this will override other controls setting the length of each modelled year.
            otherargs : dict, optional 
               Any namelist parameters not included by default in the configuration options.
               These should be passed as a dictionary, with "PARAMETER@namelist" as the
               form of the dictionary key, and the parameter value passed as a string.
               e.g. ``otherargs={"N_RUN_MONTHS@plasim_namelist":'4',"NGUI@plasim_namelist:'1'}``
              
    **Model Dynamics**
    
            columnmode : {None,"-","clear","static","static|clear","clear|static"}, optional 
               The inclusion of 'static' will disable horizontal advection, forcing ExoPlaSim
               into a column-only mode of operation. The inclusion of 'clear' will disable
               the radiative effects of clouds.
            drycore : bool, optional 
               True/False. If True, evaporation is turned off, and a dry atmosphere will
               be used.
            physicsfilter : str, optional
               If not an empty string, specifies the physics filter(s) to be used. Filters
               can be used during the transform from gridpoint to spectral (``"gp"``), and/or
               during the transform from spectral to gridpoint (``"sp"``). Filter types are
               "none", "cesaro", "exp", or "lh" (see the Notes for more details).
               Combinations of filter types and times should be combined with a ``|``,
               e.g. ``physicsfilter="gp|exp|sp"`` or ``physicsfilter="gp|cesaro"``.
            filterkappa : float, optional 
               A constant to be used with the exponential filter. Default is 8.0.
            filterpower : int, optional 
               A constant integer to be used with the exponential filter. Default is 8.
            filterLHN0 : float, optional 
               The constant used in the denominator of the Lander-Hoskins Filter. Default
               is 15; typically chosen so f(N)=0.1.
            diffusionwaven : int, optional 
               The critical wavenumber beyond which hyperdiffusion is applied. Default
               is 15 for T21.
            qdiffusion : float, optional 
               Timescale for humidity hyperdiffusion in days. Default for T21 is 0.1.
            tdiffusion : float, optional
               Timescale for temperature hyperdiffusion in days. Default for T21 is 5.6.
            zdiffusion : float, optional
               Timescale for vorticity hyperdiffusion in days. Default for T21 is 1.1.
            ddiffusion : float, optional
               Timescale for divergence hyperdiffusion in days.. Default for T21 is 0.2.
            diffusionpower : int, optional
               integer exponent used in hyperdiffusion. Default is 2 for T21.
                
    **Radiation**
    
            flux : float, optional
               Incident stellar flux in W/m\ :math:`^2`\ . Default 1367 for Earth.
            startemp : float, optional
               Effective blackbody temperature for the star. Not used if not set.
            starspec : str, optional
               Spectral file for the stellar spectrum. Should have two columns and 965 rows,
               with wavelength in the first column and radiance or intensity in the second.
               A similarly-named file with the "_hr.dat" suffix must also exist and have 
               2048 wavelengths. Appropriately-formatted files can be created with :py:mod:`makestellarspec.py <exoplasim.makestellarspec>`.
            twobandalbedo : bool, optional
               True/False. If True, separate albedos will be calculated for each of the
               two shortwave bands. If False (default), a single broadband albedo will be
               computed and used for both.
            synchronous : bool, optional
               True/False. If True, the Sun is fixed to one longitude in the sky.
            desync : float, optional
               The rate of drift of the substellar point in degrees per minute. May be positive or negative.
            substellarlon : float, optional
               The longitude of the substellar point, if synchronous==True. Default 180°
            pressurebroaden : bool, optional 
               True/False. If False, pressure-broadening of absorbers no longer depends
               on surface pressure. Default is True
            ozone : bool, optional
               True/False. Whether or not forcing from stratospheric ozone should be included.
            snowicealbedo : float, optional
               A uniform albedo to use for all snow and ice.
            soilalbedo : float, optional
               A uniform albedo to use for all land.
            wetsoil : bool, optional
               True/False. If True, land albedo depends on soil moisture (wet=darker).
            oceanalbedo : float, optional
               A uniform albedo to use for the ocean.
            oceanzenith : {"ECHAM-3","ECHAM-6","Lambertian}, optional
               The zenith-angle dependence to use for blue-light reflectance from the ocean.
               Can be ``'Lambertian'``/``'uniform'``, ``'ECHAM-3'``/``'plasim'``/``'default'``, or ``'ECHAM-6'``.
               The default is ``'ECHAM-3'`` (synonymous with ``'plasim'`` and ``'default'``), which is
               the dependence used in the ECHAM-3 model.
                                 
    **Orbital Parameters**
    
            year : float, optional
              Number of 24-hour days in a sidereal year. Not necessary if eccentricity and 
              obliquity are zero. Defaults if not set to ~365.25 days
            rotationperiod : float, optional
              Planetary rotation period, in days. Default is 1.0.
            eccentricity : float, optional
              Orbital eccentricity. If not set, defaults to Earth's (0.016715)
            obliquity : float, optional
              Axial tilt, in degrees. If not set, defaults to Earth's obliquity (23.441°).
            lonvernaleq : float, optional
              Longitude of periapse, measured from vernal equinox, in degrees. If 
              not set, defaults to Earth's (102.7°).
            fixedorbit : bool, optional
              True/False. If True, orbital parameters do not vary over time. If False,
              variations such as Milankovich cycles will be computed by PlaSim.
                
    **Planet Parameters**
    
            gravity : float, optional 
              Surface gravity, in m/s\ :math:`^2`\ . Defaults to 9.80665 m/s\ :math:`^2`\ .
            radius : float, optional 
              Planet radius in Earth radii. Default is 1.0.
            orography : float, optional 
              If set, a scaling factor for topographic relief. If ``orography=0.0``, topography
              will be zeroed-out.
            aquaplanet : bool, optional 
              True/False. If True, the surface will be entirely ocean-covered.
            desertplanet : bool, optional 
              True/False. If True, the surface will be entirely land-covered.
            tlcontrast : float, optional
              The initial surface temperature contrast between fixedlon and the anterior point. Default is 0.0 K.
            seaice : bool, optional 
              True/False. If False, disables radiative effects of sea ice (although sea ice 
              itself is still computed).
            landmap : str, optional 
              Path to a ``.sra`` file containing a land mask for the chosen resolution.
            topomap : str, optional 
              Path to a ``.sra`` file containing geopotential height map. Must include landmap.
                
    **Atmosphere**
    
            gascon : float, optional
               Effective gas constant. Defaults to 287.0 (Earth), or the gas constant
               corresponding to the composition specified by partial pressures.
            vtype : {0,1,2,3,4,5}, optional
               Type of vertical discretization. Can be:
               0   Pseudolinear scaling with pressure that maintains resolution near the ground.
               1   Linear scaling with pressure.
               2   Logarithmic scaling with pressure (resolves high altitudes)
               3   Pseudologarithmic scaling with pressure that preserves resolution near the ground.
               4   Pseudolinear scaling with pressure, pinned to a specified top pressure.
               5   If >10 layers, bottom 10 as if ``vtype=4``, and upper layers as if ``vtype=2``.
            modeltop : float, optional
               Pressure of the top layer
            tropopause : float, optional
               If stratosphere is being included, pressure of the 10th layer (where scheme
               switches from linear to logarithmic).
            stratosphere : bool, optional
               True/False. If True, vtype=5 is used, and model is discretized to include
               a stratosphere.
            pressure: float, optional
                  Surface pressure in bars, if not specified through partial pressures.
                
    **Gas Partial Pressures**
        
    Partial pressures of individual gases can be specified. If pressure and gascon are not explicitly set, these will determine surface pressure, mean molecular weight, and effective gas constant. Note however that Rayleigh scattering assumes an Earth-like composition, and the only absorbers explicitly included in the radiation scheme are CO2 and H2O.
            
            pH2 : float, optional   
                H2 partial pressure in bars.
            pHe : float, optional   
                He partial pressure in bars.
            pN2 : float, optional  
                N2 partial pressure in bars.
            pO2 : float, optional  
                O2 partial pressure in bars.
            pH2 : float, optional  
                H2 partial pressure in bars.
            pAr : float, optional  
                Ar partial pressure in bars.
            pNe : float, optional  
                Ne partial pressure in bars.
            pKr : float, optional  
                Kr partial pressure in bars.
            pCO2 : float, optional  
                CO2 partial pressure in bars. This gets translated into a ppmv concentration, so if you want to specify/vary CO2 but don't need the other gases, specifying pCO2, pressure, and gascon will do the trick. In most use cases, however, just specifying pN2 and pCO2 will give good enough behavior.
            pH2O : float, optional  
                H2O partial pressure in bars. This is only useful in setting the gas constant and surface pressure; it will have no effect on actual moist processes.
                    
    **Surface Parameters**
    
        mldepth : float, optional
           Depth of the mixed-layer ocean. Default is 50 meters.
        soildepth : float, optional
           Scaling factor for the depth of soil layers (default total of 12.4 meters)
        cpsoil : float, optional
           Heat capacity of the soil, in J/m^3/K. Default is 2.4*10^6.
        soilwatercap : float, optional
           Water capacity of the soil, in meters. Defaults to 0.5 meters
        soilsaturation : float, optional
           Initial fractional saturation of the soil. Default is 0.0 (dry).
        maxsnow : float, optional
           Maximum snow depth (Default is 5 meters; set to -1 to have no limit).
                
    **Additional Physics**
        
        Carbon-Silicate Weathering
           co2weathering : bool, optional
              True/False. Toggles whether or not carbon-silicate weathering should be
              computed. Default is False.   
           evolveco2 : bool, optional
              True/False. If co2weathering==True, toggles whether or not the CO2 partial
              pressure should be updated every year. Usually the change in pCO2 will be 
              extremely small, so this is not necessary, and weathering experiments try
              to estimate the average weathering rate for a given climate in order to 
              interpolate timescales between climates, rather than modelling changes in CO2
              over time directly.
           outgassing : float, optional 
              The assumed CO2 outgassing rate in units of Earth outgassing. Default is 1.0.
           erosionsupplylimit : float, optional
              If set, the maximum CO2 weathering rate per year permitted by
              erosion, in ubars/year. This is not simply a hard cutoff, but follows
              Foley 2015 so high weathering below the cutoff is also reduced.
        
    See [1]_ for details on the implementation of supply-limited weathering.
        
        Glaciology
           glaciers : dict, optional 
              A dictionary containing the following arguments:
              toggle : bool
                   True/False. Whether or not glaciers should be allowed to grow or shrink in thickness, or be formed from persistent snow on land.
              mindepth : float 
                   The minimum snow depth in meters of liquid water equivalent that must persist year-round before the grid cell is considered glaciated. Default is 2 meters.
              initialh : float 
                   If >=0, covers the land surface with ice sheets of a height given in meterss. If -1, no initial ice sheets are assumed.
           
        Storm Climatology
           stormclim : bool, optional 
              True/False. Toggles whether or not storm climatology (convective available
              potential energy, maximum potential intensity, ventilation index, etc)
              should be computed. If True, output fields related to storm climatology 
              will be added to standard output files. Enabling this mode currently roughly
              doubles the computational cost of the model. This may improve in future 
              updates. Refer to Paradise, et al 2021 for implementation description. 
              
           stormcapture : dict, optional
              A dictionary containing arguments controlling when high-cadence output
              is triggered by storm activity. This dictionary must contain 'toggle', which
              can be either 1 or 0 (yes or no). It may also contain any namelist
              parameters accepted by hurricanemod.f90, including the following:
              
              toggle : {0,1}
                   Whether (1) or not (0) to write high-cadence output when storms occur
              NKTRIGGER : {0,1}, optional 
                   (0/1=no/yes). Whether or not to use the Komacek, et al 2020 conditions for hurricane cyclogenesis as the output trigger. Default is no.
              VITHRESH : float, optional
                   (nktrigger) Ventilation index threshold for nktrigger output. Default 0.145
              VMXTHRESH : float, optional 
                   (nktrigger) Max potential intensity threshold for nktrigger output.Default 33 m/s
              LAVTHRESH : float, optional 
                   (nktrigger) Lower-atmosphere vorticity threshold for nktrigger output. Default 1.2*10^-5 s^-1
              VRMTHRESH : float, optional 
                   (unused) Ventilation-reduced maximum intensity threshold. Default 0.577
              GPITHRESH : float, optional  
                   (default) Genesis Potential Index threshold. Default 0.37.
              MINSURFTEMP : float, optional  
                   (default) Min. surface temperature for storm activity. Default 25C
              MAXSURFTEMP : float, optional  
                   (default) Max. surface temperature for storm activity. Default 100C
              WINDTHRESH : float, optional   
                   (default) Lower-atmosphere maximum wind threshold for storm activity.  Default 33 m/s
              SWINDTHRESH : float, optional  
                   (default) Minimum surface windspeed for storm activity. Default 20.5 m/s
              SIZETHRESH : float, optional  
                   (default) Minimum number of cells that must trigger to start outputDefault 30
              ENDTHRESH : float, optional  
                   (default) Minimum number of cells at which point storm output ends.Default 16
              MINSTORMLEN : float, optional  
                   (default) Minimum number of timesteps to write output. Default 256
              MAXSTORMLEN : float, optional  
                   (default) Maximum number of timesteps to write output. Default 1024
           
    Note that actual number of writes will be stormlen/interval, as set in highcadence. This interval defaults to 4, so 64 writes minimum, 256 max. For more details on the storm climatology factors considered here, see [5]_.
        
Notes
-----
        In some cases, it may be necessary to include physics filters. This typically becomes 
        necessary when sharp features are projected on the model's smallest spectral modes, causing
        Gibbs "ripples". Earth-like models typically do not require filtering, but tidally-locked
        models do. Filtering may be beneficial for Earth-like models at very high resolutions as well,
        or if there is sharp topography. 
        
        Three filter functional forms are included in ExoPlaSim: Cesaro, exponential, and Lander-Hoskins. Their functional forms are given below, where `n` is the wavenumber, and `N` is the
        truncation wavenumber (e.g. 21 for T21):
        
        Cesaro: :math:`f(n)=1-\\frac{n}{N+1}` [2]_
        
        Exponential: :math:`f(n)=\exp\left[-\kappa\left(\\frac{n}{N}\\right)^\gamma\\right]` [3]_
        
        Lander-Hoskins: :math:`f(n)=\exp\left[-\left(\\frac{n(n+1)}{n_0(n_0+1}\\right)^2\\right]` [3]_ [4]_
        
        :math:`\kappa` is exposed to the user through ``filterkappa``, 
        :math:`\gamma` is exposed through ``filterpower``, and :math:`n_0` is
        exposed through ``filterLHN0``.
        
        Physics filters can be applied at two different points; either at the transform from gridpoint
        to spectral, or the reverse. We find that in most cases, the ideal usage is to use both. 
        Generally, a filter at the gridpoint->spectral transform is good for dealing with oscillations
        caused by sharp jumps and small features in the gridpoint tendencies. Conversely, a filter
        at the spectral->gridpoint transform is good for dealing with oscillations that come from
        small-scale features in the spectral fields causing small-scale features to appear in the
        gridpoint tendencies [3]_. Since we deal with climate systems where everything is coupled, 
        any oscillations not removed by one filter will be amplified through physical feedbacks if not 
        suppressed by the other filter.
        
See Also
--------
    :py:func:`modify <exoplasim.Model.modify>` : Change model configuration after it has been initialized
        
References
----------
        .. [1] Foley, B. J. (2015). The Role of Plate Tectonic-Climate Coupling and Exposed Land Area in the Development of Habitable Climates on Rocky Planets. The Astrophysical Journal, 812(1), 36. https://doi.org/10.1088/0004-637X/812/1/36
        
        .. [2] Navarra, A., Stern, W. F., & Miyakoda, K. (1994). Reduction of the Gibbs Oscillation in Spectral Model Simulations. Journal of Climate, 7(8), 1169–1183. https://doi.org/10.1175/1520-0442(1994)007<1169:ROTGOI>2.0.CO;2
        
        .. [3] Lander, J., & Hoskins, B. J. (1997). Believable Scales and Parameterizations in a Spectral Transform Model. Monthly Weather Review, 125(2), 292–303. https://doi.org/10.1175/1520-0493(1997)125<0292:BSAPIA>2.0.CO;2
        
        .. [4] Scinocca, J. F., McFarlane, N. A., Lazare, M., Li, J., & Plummer, D. (2008). Technical Note: The CCCma third generation AGCM and its extension into the middle atmosphere. Atmospheric Chemistry and Physics, 8(23), 7055–7074. https://doi.org/10.5194/acp-8-7055-2008
        
        .. [5] Komacek, T. D., Chavas, D. R., & Abbot, D. S. (2020). Hurricane Genesis is Favorable on Terrestrial Exoplanets Orbiting Late-type M Dwarf Stars. The Astrophysical Journal, 898(2), 115. https://doi.org/10.3847/1538-4357/aba0b9
        
        """
        self._edit_namelist("plasim_namelist","NOUTPUT",str(noutput*1))
        self.noutput = noutput
        self._edit_namelist("planet_namelist","GSOL0",str(flux))
        self.flux = flux
        if startemp:
            self._edit_namelist("radmod_namelist","NSTARTEMP","1")
            self._edit_namelist("radmod_namelist","STARBBTEMP",str(startemp))
        self.startemp = startemp
        if starspec:
            if starspec[-4:]==".dat":
                starspec=starspec[:-4]
            self._edit_namelist("radmod_namelist","NSTARFILE","1")
            self._edit_namelist("radmod_namelist","STARFILE","'%s'"%starspec)
            self._edit_namelist("radmod_namelist","STARFILEHR","'%s_hr.dat'"%(starspec)[:-4])
        self.starspec = starspec
        
        if pH2:
            self.pgases["pH2"]=pH2
        if pHe:
            self.pgases["pHe"]=pHe
        if pN2:
            self.pgases["pN2"]=pN2
        if pO2:
            self.pgases["pO2"]=pO2
        if pCO2:
            self.pgases["pCO2"]=pCO2
        if pAr:
            self.pgases["pAr"]=pAr
        if pNe:
            self.pgases["pNe"]=pNe
        if pKr:
            self.pgases["pKr"]=pKr
        if pH2O:
            self.pgases["pH2O"]=pH2O
        
        if len(self.pgases)==0:
            if not pressure:
                #self.pgases=gases_default
                #self.pressure=0.0
                #for gas in self.pgases:
                    #self.pressure+=self.pgases[gas] #in bars
                self.pressure = 1.011
            else:
                self.pressure = pressure
        
        else:
            self.pressure=0.0
            for gas in self.pgases:
                self.pressure+=self.pgases[gas]
        
        gasesvx = {}
        for gas in self.pgases:
            gasesvx[gas[1:]] = self.pgases[gas]/self.pressure
        self.mmw = 0
        for gas in gasesvx:
            self.mmw += gasesvx[gas]*smws['m'+gas]
        if self.mmw==0:
            self.mmw = 28.970253
        self.gascon = 8314.46261815324 / self.mmw
        
        if gascon:
            self.gascon=gascon
            self.mmw = 8314.46261815324/self.gascon
        
        print('Mean Molecular Weight set to %1.4f g/mol'%self.mmw)
        
        if pressure:
            if pressure != self.pressure:  #User has specified a different pressure than sum of gas pressures
                self.pressure = pressure
        
        self.CO2ppmv = 0.0
        if 'pCO2' in self.pgases:
            self.CO2ppmv = self.pgases['pCO2']/self.pressure * 1.0e6 #ppmv
        
        self._edit_namelist("radmod_namelist","CO2",str(self.CO2ppmv))
        self._edit_namelist("plasim_namelist","PSURF",str(self.pressure*1.0e5)) #Pa
        self._edit_namelist("planet_namelist","GASCON",str(self.gascon))
        self._edit_namelist("radmod_namelist","NPBROADEN",str(pressurebroaden*1))
        self.pressurebroaden=pressurebroaden
        self._edit_namelist("plasim_namelist","NEQSIG",str(vtype))
        self.vtype=vtype
        
        self._edit_namelist("plasim_namelist","MPSTEP",str(timestep))
        self._edit_namelist("plasim_namelist","NSTPW",str(int(7200//int(timestep))))
        self.timestep=timestep
        
        if year:
            self._edit_namelist("planet_namelist","N_DAYS_PER_YEAR",str(int(year)))
            self._edit_namelist("planet_namelist","SIDEREAL_YEAR",str(year*86400.0))
        self.sidyear=year
        if rotationperiod!=1.0:
            self._edit_namelist("planet_namelist","ROTSPD",str(1.0/float(rotationperiod)))
            self._edit_namelist("plasim_namelist","N_DAYS_PER_YEAR",
                                str(max(int(360.0/float(rotationperiod)/12+0.5),1)*12))
            #if rotationperiod>80.0 and type(top_restoretime)==type(None):
                #top_restoretime = 1.0 #If we have a long rotation period, apply top-layer forcing
            nsteps = max(1,int(round(360.0*1440.0/self.timestep+0.49999)))
            self._edit_namelist("plasim_namelist","N_RUN_STEPS",str(nsteps))
        if runsteps is not None:
            self._edit_namelist("plasim_namelist","N_RUN_STEPS",str(runsteps))
        self.runsteps = runsteps
        self.rotationperiod=rotationperiod
        if synchronous:
            self._edit_namelist("radmod_namelist","NFIXED","1")
            self._edit_namelist("plasim_namelist","FIXEDLON",str(substellarlon))
        self.synchronous=synchronous
        self.substellarlon=substellarlon
        self._edit_namelist("radmod_namelist","DESYNC",str(desync))
        self.desync=desync
        self._edit_namelist("plasim_namelist","DTTL",str(tlcontrast))
        self.tlcontrast=tlcontrast
        if top_restoretime:
            #self._edit_namelist("plasim_namelist","RESTIM","%f,%d*0.0"%(top_restoretime,self.layers-1))
            self._edit_namelist("plasim_namelist","NSPONGE","1")
            self._edit_namelist("plasim_namelist","DAMPSP","%f"%top_restoretime)
        self.top_restoretime = top_restoretime
        
        if restartfile:
            os.system("cp %s %s/plasim_restart"%(restartfile,self.workdir))
        else:
            os.system("rm %s/plasim_restart"%self.workdir)
        self.restartfile=restartfile
        
        self._edit_namelist("planet_namelist","GA",str(gravity))
        self._edit_postnamelist("example.nl","gravity",str(gravity))
        self._edit_postnamelist("snapshot.nl","gravity",str(gravity))
        self.gravity=gravity
        
        self._edit_namelist("planet_namelist","PLARAD",str(radius*6371220.0))
        self._edit_postnamelist("example.nl","radius",str(radius*6371220.0))
        self._edit_postnamelist("snapshot.nl","radius",str(radius*6371220.0))
        self.radius=radius
        
        if type(eccentricity)!=type(None):
            self._edit_namelist("planet_namelist","ECCEN",str(eccentricity))
        self.eccentricity=eccentricity
        
        if type(obliquity)!=type(None):
            self._edit_namelist("planet_namelist","OBLIQ",str(obliquity))
        self.obliquity=obliquity
        
        if type(lonvernaleq)!=type(None):
            self._edit_namelist("planet_namelist","MVELP",str(lonvernaleq))
        self.lonvernaleq=lonvernaleq
        
        self._edit_namelist("planet_namelist","NFIXORB",str(fixedorbit*1))
        self.fixedorbit=fixedorbit
        
        if type(orography)!=type(None):
            self._edit_namelist("landmod_namelist","OROSCALE",str(orography))
            self._edit_namelist("glacier_namelist","NGLACIER","1")
        self.orography=orography
                
        self._edit_namelist("radmod_namelist","NRADICE",str(seaice*1))
        self.seaice=seaice
        
        self._edit_namelist("carbonmod_namelist","NCARBON",str(co2weathering*1))
        self._edit_namelist("carbonmod_namelist","NCO2EVOLVE",str(evolveco2*1))
        self.co2weathering=co2weathering
        self.evolveco2=evolveco2
        if type(erosionsupplylimit)!=type(None):
            self._edit_namelist("carbonmod_namelist","NSUPPLY","1")
            self._edit_namelist("carbonmod_namelist","WMAX",str(erosionsupplylimit))
        self.erosionsupplylimit=erosionsupplylimit
        self._edit_namelist("carbonmod_namelist","VOLCANCO2",str(outgassing))
        self.outgassing=outgassing
        
        if physicsfilter:
            vals = physicsfilter.split("|")
            if "gp" in vals:
                self._edit_namelist("plasim_namelist","NGPTFILTER","1")
            if "sp" in vals:
                self._edit_namelist("plasim_namelist","NSPVFILTER","1")
            if "none" in vals:
                self._edit_namelist("plasim_namelist","NFILTER","0")
            if "cesaro" in vals:
                self._edit_namelist("plasim_namelist","NFILTER","1")
            if "exp" in vals:
                self._edit_namelist("plasim_namelist","NFILTER","2")
            if "lh" in vals:
                self._edit_namelist("plasim_namelist","NFILTER","3")
        self.physicsfilter=physicsfilter
        self._edit_namelist("plasim_namelist","FILTERKAPPA",str(filterkappa))
        self.filterkappa=filterkappa
        self._edit_namelist("plasim_namelist","NFILTEREXP",str(filterpower))
        self.filterpower=filterpower
        self._edit_namelist("plasim_namelist","LANDHOSKN0",str(filterLHN0))
        self.filterLHN0=filterLHN0
        if diffusionwaven:
            self._edit_namelist("plasim_namelist","NHDIFF",str(diffusionwaven))
        self.diffusionwaven=diffusionwaven
        if qdiffusion:
            self._edit_namelist("plasim_namelist","TDISSQ","%d*%f"%(self.layers,qdiffusion))
        self.qdiffusion=qdiffusion
        if tdiffusion:
            self._edit_namelist("plasim_namelist","TDISST","%d*%f"%(self.layers,tdiffusion))
        self.tdiffusion=tdiffusion
        if zdiffusion:
            self._edit_namelist("plasim_namelist","TDISSZ","%d*%f"%(self.layers,zdiffusion))
        self.zdiffusion=zdiffusion
        if ddiffusion:
            self._edit_namelist("plasim_namelist","TDISSD","%d*%f"%(self.layers,ddiffusion))
        self.ddiffusion=ddiffusion
        if diffusionpower:
            self._edit_namelist("plasim_namelist","NDEL","%d*%d"%(self.layers,diffusionpower))
        self.diffusionpower=diffusionpower
        
        self.glaciers=glaciers
        self._edit_namelist("glacier_namelist","NGLACIER",str(self.glaciers["toggle"]*1))
        self._edit_namelist("glacier_namelist","GLACELIM",str(self.glaciers["mindepth"]))
        self._edit_namelist("glacier_namelist","ICESHEETH",str(self.glaciers["initialh"]))
        if self.glaciers["initialh"]>0:
            os.system("rm %s/*174.sra %s/*1740.sra %s/*210.sra %s/*232.sra"%([self.workdir,]*4))
        
        if type(snowicealbedo)!=type(None):
            alb = str(snowicealbedo)
            self._edit_namelist("seamod_namelist","ALBICE",alb)
            self._edit_namelist("seamod_namelist","DICEALBMN","%s,%s"%(alb,alb))
            self._edit_namelist("seamod_namelist","DICEALBMX","%s,%s"%(alb,alb))
            self._edit_namelist("landmod_namelist","DSNOWALBMN","%s,%s"%(alb,alb))
            self._edit_namelist("landmod_namelist","DSNOWALBMN","%s,%s"%(alb,alb))
            self._edit_namelist("landmod_namelist","DGLACALBMN","%s,%s"%(alb,alb))
            self._edit_namelist("landmod_namelist","DSNOWALB","%s,%s"%(alb,alb))
        self.snowicealbedo=snowicealbedo
        
        self._edit_namelist("radmod_namelist","NSIMPLEALBEDO",str((not twobandalbedo)*1))
        self.twobandalbedo=twobandalbedo
        
        if maxsnow:
            self._edit_namelist("landmod_namelist","DSMAX",str(maxsnow))
        self.maxsnow=maxsnow
        
        if type(soilalbedo)!=type(None):
            alb = str(soilalbedo)
            os.system("rm %s/*0174.sra"%self.workdir)
            self._edit_namelist("landmod_namelist","ALBLAND",alb)
            self._edit_namelist("landmod_namelist","DGROUNDALB","%s,%s"%(alb,alb))
        self.soilalbedo=soilalbedo
        
        if type(oceanalbedo)!=type(None):
            alb = str(oceanalbedo)
            self._edit_namelist("seamod_namelist","ALBSEA",alb)
            self._edit_namelist("seamod_namelist","DOCEANALB","%s,%s"%(alb,alb))
        self.oceanalbedo=oceanalbedo
        
        if oceanzenith=="lambertian" or oceanzenith=="Lambertian" or oceanzenith=="uniform":
            self._edit_namelist("radmod_namelist","NECHAM","0")
            self._edit_namelist("radmod_namelist","NECHAM6","0")
        if oceanzenith=="default" or oceanzenith=="plasim" or oceanzenith=="ECHAM-3":
            self._edit_namelist("radmod_namelist","NECHAM","1")
            self._edit_namelist("radmod_namelist","NECHAM6","0")
        if oceanzenith=="ECHAM-6":
            self._edit_namelist("radmod_namelist","NECHAM","0")
            self._edit_namelist("radmod_namelist","NECHAM6","1")
        self.oceanzenith=oceanzenith
        
        self._edit_namelist("landmod_namelist","NWETSOIL",str(wetsoil*1))
        self.wetsoil=wetsoil
        if soilwatercap:
            self._edit_namelist("landmod_namelist","WSMAX",str(soilwatercap))
            os.system("rm %s/*0229.sra"%self.workdir)
        if desertplanet:
            self._edit_namelist("plasim_namelist","NDESERT","1")
            self._edit_namelist("landmod_namelist","NWATCINI","1")
            self._edit_namelist("landmod_namelist","DWATCINI","0.0")
            os.system("rm %s/*.sra"%self.workdir)
        if type(soilsaturation)!=type(None):
            self._edit_namelist("landmod_namelist","NWATCINI","1")
            self._edit_namelist("landmod_namelist","DWATCINI",str(soilsaturation))
            os.system("rm %s/*0229.sra"%self.workdir)
        if aquaplanet:
            self._edit_namelist("plasim_namelist","NAQUA","1")
            os.system("rm %s/*.sra"%self.workdir)
        self.soilwatercap=soilwatercap
        self.soilsaturation=soilsaturation
        self.desertplanet=desertplanet
        self.aquaplanet=aquaplanet
        
        if drycore:
            self._edit_namelist("fluxmod_namelist","NEVAP","0")
        self.drycore=drycore
        
        if columnmode:
            parts = columnmode.split("|")
            if "static" in parts:
                self._edit_namelist("plasim_namelist","NADV","0")
            if "clear" in parts:
                self._edit_namelist("radmod_namelist","NCLOUDS","0")
                self._edit_namelist("radmod_namelist","ACLLWR","0.0")
        self.columnmode=columnmode
        
        self._edit_namelist("radmod_namelist","NO3",str(ozone*1))
        self.ozone=ozone
        
        if cpsoil:
            self._edit_namelist("landmod_namelist","SOILCAP",str(cpsoil))
        self.cpsoil = cpsoil
        
        self.dzsoils = np.array([0.4, 0.8, 1.6, 3.2, 6.4])*soildepth
        self._edit_namelist("landmod_namelist","DSOILZ",",".join(self.dzsoils.astype(str)))
        self.soildepth=soildepth
        
        self._edit_namelist("oceanmod_namelist","MLDEPTH",str(mldepth))
        self.mldepth=mldepth
        
        if writefrequency:
            self._edit_namelist("plasim_namelist","NWPD",str(writefrequency))
        self.writefrequency=writefrequency
        
        if stratosphere:
            self._edit_namelist("plasim_namelist","NEQSIG","5")
            if modeltop:
                self._edit_namelist("plasim_namelist","PTOP2",str(modeltop*100.0)) #convert hPa->Pa
            if tropopause:
                self._edit_namelist("plasim_namelist","PTOP",str(tropopause*100.0))
        else:
            if modeltop:
                self._edit_namelist("plasim_namelist","PTOP",str(modeltop*100.0)) #convert hPa->Pa
        self.stratosphere=stratosphere
        self.modeltop=modeltop
        self.tropopause=tropopause
        
        self.runscript=runscript
        
        self._edit_namelist("plasim_namelist","NHCADENCE",str(highcadence["toggle"]))
        self._edit_namelist("plasim_namelist","HCSTARTSTEP",str(highcadence["start"]))
        self._edit_namelist("plasim_namelist","HCENDSTEP",str(highcadence["end"]))
        self._edit_namelist("plasim_namelist","HCINTERVAL",str(highcadence["interval"]))
        self.highcadence=highcadence
        
        if snapshots:
            self._edit_namelist("plasim_namelist","NSNAPSHOT","1")
            self._edit_namelist("plasim_namelist","NSTPS",str(snapshots))
        self.snapshots=snapshots
        
        if len(resources)>0:
            for res in resources:
                os.system("cp %s %s/"%(res,self.workdir))
        self.resources=resources
        
        if landmap or topomap:
            os.system("rm %s/*.sra"%self.workdir)
        if landmap:
            os.system("cp %s %s/N%03d_surf_0172.sra"%(landmap,self.workdir,self.nlats))
        if topomap:
            os.system("cp %s %s/N%03d_surf_0129.sra"%(topomap,self.workdir,self.nlats))
        self.landmap=landmap
        self.topomap=topomap
        
        if stormclim:
            self._edit_namelist("hurricane_namelist","NSTORMDIAG","1")
            self._add_postcodes("example.nl",[322,323,324,325,326,327,328,329])
            self._add_postcodes("snapshot.nl",[322,323,324,325,326,327,328,329])
        self.stormclim=stormclim
        self._edit_namelist("hurricane_namelist","NSTORMS",str(int(nstorms)))
        self.nstorms=nstorms
        if stormcapture["toggle"]:
            self._edit_namelist("hurricane_namelist","HC_CAPTURE","1")
            for param in stormcapture:
                if param!="toggle":
                    self._edit_namelist("hurricane_namelist",param,str(stormcapture[param]))
        self.stormcapture=stormcapture
        self.threshold = threshold
        if len(otherargs)>0:
            for key in otherargs:
                value = otherargs[key]
                destination=key.split("@")
                field=destination[0]
                namelist=destination[1]
                self._edit_namelist(namelist,field,value)
                self.otherargs[key]=value
    
    def loadconfig(self,configfile):
        """    Load a previously-exported configuration file and configure the model accordingly.
        
        Parameters
        ----------
        configfile : str 
            Path to the configuration file to load
            
        See Also
        --------
        :py:func:`exportcfg <exoplasim.Model.exportcfg>` : Export model configuration to a text file.
    
        """
        with open(configfile,"r") as cfgf:
            cfg = cfgf.read().split("\n")
        noutput=bool(int(cfg[0]))
        flux=float(cfg[1])
        startemp=_noneparse(cfg[2],float)
        starspec=_noneparse(cfg[3],str)
        gases = cfg[4].split("&")
        for gas in gases:
            species = gas.split("|")
            amt = float(species[1])
            species = species[0]
            self.pgases[species] = amt
        gascon = float(cfg[5])
        pressure = _noneparse(cfg[6],float)
        pressurebroaden = bool(int(cfg[7]))
        vtype = int(cfg[8])
        rotationperiod = float(cfg[9])
        synchronous = bool(int(cfg[10]))
        substellarlon = float(cfg[11])
        restartfile = _noneparse(cfg[12],str)
        gravity = float(cfg[13])
        radius = float(cfg[14])
        eccentricity = _noneparse(cfg[15],float)
        obliquity = _noneparse(cfg[16],float)
        lonvernaleq = _noneparse(cfg[17],float)
        fixedorbit = bool(int(cfg[18]))
        orography = _noneparse(cfg[19],float)
        seaice = bool(int(cfg[20]))
        co2weathering = bool(int(cfg[21]))
        evolveco2 = bool(int(cfg[22]))
        physicsfilter = _noneparse(cfg[23],str)
        filterkappa = float(cfg[24])
        filterpower = int(cfg[25])
        filterLHN0 = float(cfg[26])
        diffusionwaven = _noneparse(cfg[27],int)
        qdiffusion = _noneparse(cfg[28],float)
        tdiffusion = _noneparse(cfg[29],float)
        zdiffusion = _noneparse(cfg[30],float)
        ddiffusion = _noneparse(cfg[31],float)
        diffusionpower = _noneparse(cfg[32],int)
        erosionsupplylimit = _noneparse(cfg[33],float)
        outgassing = float(cfg[34])
        snowicealbedo = _noneparse(cfg[35],float)
        twobandalbedo = bool(int(cfg[36]))
        maxsnow = _noneparse(cfg[37],float)
        soilalbedo = _noneparse(cfg[38],float)
        oceanalbedo = _noneparse(cfg[39],float)
        oceanzenith = cfg[40]
        wetsoil = bool(int(cfg[41]))
        soilwatercap = _noneparse(cfg[42],float)
        aquaplanet = bool(int(cfg[43]))
        desertplanet = bool(int(cfg[44]))
        soilsaturation = _noneparse(cfg[45],float)
        drycore = bool(int(cfg[46]))
        ozone = bool(int(cfg[47]))
        cpsoil = _noneparse(cfg[48],float)
        soildepth = float(cfg[49])
        mldepth = float(cfg[50])
        writefrequency = _noneparse(cfg[51],int)
        modeltop = _noneparse(cfg[52],float)
        stratosphere = bool(int(cfg[53]))
        tropopause = _noneparse(cfg[54],float)
        timestep = float(cfg[55])
        runscript = _noneparse(cfg[56],str)
        columnmode = _noneparse(cfg[57],str)
        hcdict = cfg[58].split("&")
        highcadence = {}
        for hc in hcdict:
            parts = hc.split("|")
            highcadence[parts[0]] = int(parts[1])
        snapshots = _noneparse(cfg[59],int)
        resources = []
        reslist = cfg[60].split("&")
        if len(reslist)>0 and reslist[0]!='':
            for res in reslist:
                resources.append(res)
        landmap = _noneparse(cfg[61],str)
        topomap = _noneparse(cfg[62],str)
        stormclim = bool(int(cfg[63]))
        nstorms = int(cfg[64])
        stormcapture = {}
        stormdict = cfg[65].split("&")
        for item in stormdict:
            parts = item.split("|")
            if parts[0]=="toggle" or parts[0]=="NKTRIGGER" or parts[0]=="SIZETHRESH" \
            or parts[0]=="ENDTHRESH" or parts[0]=="MINSTORMLEN" or parts[0]=="MAXSTORMLEN":
                stormcapture[parts[0]] = int(parts[1])
            else:
                stormcapture[parts[0]] = float(parts[1])
        otherargs = {}
        otherdict = cfg[66].split("&")
        if len(otherdict)>1 or otherdict[0]!='':
            print(otherdict)
            for item in otherdict:
                parts = item.split("~")
                if parts[1]=="f":
                    dtype=float
                elif parts[1]=="i":
                    dtype=int
                elif parts[1]=="s":
                    dtype=str
                parts = parts[0].split("|")
                otherargs[parts[0]] = dtype(parts[1])
        year = _noneparse(cfg[67],float)
        glaciers = {}
        glacdict = cfg[68].split("&")
        glaciers["toggle"] = bool(int(glacdict[0]))
        glaciers["mindepth"] = float(glacdict[1])
        glaciers["initialh"] = float(glacdict[2])
        threshold = float(cfg[69])
        #PAST THIS POINT ALL ADDITIONAL LOADS SHOULD BE IN TRY-EXCEPT FOR BACKWARDS COMPAT.
        try:
            tlcontrast = float(cfg[70])
        except:
            tlcontrast = 0.0
            
        try:
            restim = float(cfg[71])
        except:
            restim = None
            
        try:
            runsteps = _noneparse(cfg[72],int)
        except:
            runsteps = None
            
        try:
            desync = float(cfg[73])
        except:
            desync = 0.0
        
        self.configure(noutput=noutput,flux=flux,startemp=startemp,starspec=starspec,
                    gascon=gascon,pressure=pressure,pressurebroaden=pressurebroaden,
                    vtype=vtype,rotationperiod=rotationperiod,synchronous=synchronous,
                    year=year,top_restoretime=restim,runsteps=runsteps,
                    substellarlon=substellarlon,restartfile=restartfile,gravity=gravity,
                    radius=radius,eccentricity=eccentricity,obliquity=obliquity,
                    lonvernaleq=lonvernaleq,fixedorbit=fixedorbit,orography=orography,
                    seaice=seaice,co2weathering=co2weathering,evolveco2=evolveco2,
                    physicsfilter=physicsfilter,filterkappa=filterkappa,
                    filterpower=filterpower,filterLHN0=filterLHN0,diffusionwaven=diffusionwaven,
                    qdiffusion=qdiffusion,tdiffusion=tdiffusion,zdiffusion=zdiffusion,
                    ddiffusion=ddiffusion,diffusionpower=diffusionpower,desync=desync,
                    erosionsupplylimit=erosionsupplylimit,outgassing=outgassing,
                    snowicealbedo=snowicealbedo,twobandalbedo=twobandalbedo,maxsnow=maxsnow,
                    soilalbedo=soilalbedo,oceanalbedo=oceanalbedo,oceanzenith=oceanzenith,
                    wetsoil=wetsoil,soilwatercap=soilwatercap,aquaplanet=aquaplanet,
                    desertplanet=desertplanet,soilsaturation=soilsaturation,
                    drycore=drycore,ozone=ozone,cpsoil=cpsoil,soildepth=soildepth,
                    mldepth=mldepth,writefrequency=writefrequency,modeltop=modeltop,
                    stratosphere=stratosphere,tropopause=tropopause,timestep=timestep,
                    runscript=runscript,columnmode=columnmode,highcadence=highcadence,
                    snapshots=snapshots,resources=resources,landmap=landmap,stormclim=stormclim,
                    nstorms=nstorms,stormcapture=stormcapture,topomap=topomap,tlcontrast=tlcontrast,
                    otherargs=otherargs,glaciers=glaciers,threshold=threshold)       
    
    def modify(self,**kwargs):
        """Modify any already-configured parameters. All parameters accepted by :py:func:`configure() <exoplasim.Model.configure>` can be passed as arguments.
        
        See Also
        --------
        :py:func:`configure <exoplasim.Model.configure>` : Set model parameters and boundary conditions
              
        """
        setgas=False
        setgascon=False
        setpressure=False
        changeatmo=False
        changeland=False
        slowrotator=False
        restim=False
        oldpressure = 0.0
        for gas in self.pgases:
            oldpressure += self.pgases[gas]
        if oldpressure==0.0:
            oldpressure = self.pressure
            
        
        if "timestep" in kwargs.keys():
            self.timestep=kwargs["timestep"]
            self._edit_namelist("plasim_namelist","MPSTEP",str(self.timestep))
            self._edit_namelist("plasim_namelist","NSTPW",
                                str(int(7200//int(self.timestep))))
            
        for key,value in kwargs.items():
            if key=="noutput":
                self._edit_namelist("plasim_namelist","NOUTPUT",str(value*1))
                self.noutput = value
            if key=="flux":
                self._edit_namelist("planet_namelist","GSOL0",str(value))
                self.flux = value
            if key=="startemp":
                startemp=value
                if startemp:
                    self._edit_namelist("radmod_namelist","NSTARTEMP","1")
                    self._edit_namelist("radmod_namelist","STARBBTEMP",str(startemp))
                self.startemp = startemp
            if key=="starspec":
                starspec=value
                if starspec[-4:]==".dat":
                    starspec=starspec[:-4]
                if starspec:
                    self._edit_namelist("radmod_namelist","NSTARFILE","1")
                    self._edit_namelist("radmod_namelist","STARFILE","'%s'"%starspec)
                    self._edit_namelist("radmod_namelist","STARFILEHR","'%s_hr.dat'"%(starspec)[:-4])
                self.starspec = starspec
            if key=="pH2":
                setgas=True
                if type(value)!=type(None):
                    self.pgases["pH2"]=value
                else:
                    self.pgases["pH2"]=0.0
            if key=="pHe":
                setgas=True
                if type(value)!=type(None):
                    self.pgases["pHe"]=value
                else:
                    self.pgases["pHe"]=0.0
            if key=="pN2":
                setgas=True
                if type(value)!=type(None):
                    self.pgases["pN2"]=value
                else:
                    self.pgases["pN2"]=0.0
            if key=="pO2":
                setgas=True
                if type(value)!=type(None):
                    self.pgases["pO2"]=value
                else:
                    self.pgases["pO2"]=0.0
            if key=="pCO2":
                setgas=True
                if type(value)!=type(None):
                    self.pgases["pCO2"]=value
                else:
                    self.pgases["pCO2"]=0.0
            if key=="pAr":
                setgas=True
                if type(value)!=type(None):
                    self.pgases["pAr"]=value
                else:
                    self.pgases["pAr"]=0.0
            if key=="pNe":
                setgas=True
                if type(value)!=type(None):
                    self.pgases["pNe"]=value
                else:
                    self.pgases["pNe"]=0.0
            if key=="pKr":
                setgas=True
                if type(value)!=type(None):
                    self.pgases["pKr"]=value
                else:
                    self.pgases["pKr"]=0.0
            if key=="pH20":
                setgas=True
                if type(value)!=type(None):
                    self.pgases["pH2O"]=value
                else:
                    self.pgases["pH2O"]=0.0
            if key=="pressure":
                pressure=value
                setpressure=True
            if key=="gascon":
                setgascon=True
                gascon=value
            if key=="pressurebroaden":
                self.pressurebroaden=value
                self._edit_namelist("radmod_namelist","NPBROADEN",str(self.pressurebroaden*1))
            if key=="vtype":
                self.vtype=value
                self._edit_namelist("plasim_namelist","NEQSIG",str(self.vtype))
            if key=="year":
                self.sidyear=year
                if self.sidyear:
                    self._edit_namelist("plasim_namelist","N_DAYS_PER_YEAR",
                                        str(int(self.sidyear)))
                    self._edit_namelist("planet_namelist","SIDEREAL_YEAR",
                                        str(self.sidyear*86400.0))
            if key=="rotationperiod":
                self.rotationperiod=value
                if self.rotationperiod!=1.0:
                    self._edit_namelist("planet_namelist","ROTSPD",
                                        str(1.0/float(self.rotationperiod)))
                    self._edit_namelist("plasim_namelist","N_DAYS_PER_YEAR",
                                        str(max(int(360.0/float(self.rotationperiod)/12+0.5),1)*12))
                    #if value>80.0:
                        #slowrotator=True
                    if "runsteps" in kwargs.keys():
                        if kwargs["runsteps"] is None:
                            nsteps = max(1,int(round(360.0*1440.0/self.timestep+0.49999)))
                            self._edit_namelist("plasim_namelist","N_RUN_STEPS",str(nsteps))
                    else:
                        nsteps = max(1,int(round(360.0*1440.0/self.timestep+0.49999)))
                        self._edit_namelist("plasim_namelist","N_RUN_STEPS",str(nsteps))
            if key=="runsteps":
                self.runsteps=value
                if self.runsteps is not None:
                    self._edit_namelist("plasim_namelist","N_RUN_STEPS",str(self.runsteps))
            if key=="top_restoretime":
                restim=True
                self.top_restoretime=value
            if key=="synchronous":
                self.synchronous=value
                self._edit_namelist("radmod_namelist","NFIXED",str(self.synchronous*1))
            if key=="substellarlon":
                self.substellarlon=value
                self._edit_namelist("plasim_namelist","FIXEDLON",str(self.substellarlon))
            if key=="desync":
                self.desync=value 
                self._edit_namelist("radmod_namelist","DESYNC",str(self.desync))
            if key=="tlcontrast":
                self.tlcontrast=value
                self._edit_namelist("plasim_namelist","DTTL",str(self.tlcontrast))
            if key=="restartfile":
                self.restartfile=value
                if self.restartfile:
                    os.system("cp %s %s/plasim_restart"%(self.restartfile,self.workdir))
                else:
                    os.system("rm %s/plasim_restart"%self.workdir)
            if key=="gravity":
                self.gravity=value
                self._edit_namelist("planet_namelist","GA",str(self.gravity))
                self._edit_postnamelist("example.nl","gravity",str(self.gravity))
                self._edit_postnamelist("snapshot.nl","gravity",str(self.gravity))
            if key=="radius":
                self.radius=value
                self._edit_namelist("planet_namelist","PLARAD",str(self.radius*6371220.0))
                self._edit_postnamelist("example.nl","radius",str(self.radius*6371220.0))
                self._edit_postnamelist("snapshot.nl","radius",str(self.radius*6371220.0))
            if key=="eccentricity":
                self.eccentricity=value
                self._edit_namelist("planet_namelist","ECCEN",str(self.eccentricity))
            if key=="obliquity":
                self.obliquity=value
                self._edit_namelist("planet_namelist","OBLIQ",str(self.obliquity))
            if key=="lonvernaleq":
                self.lonvernaleq=value
                self._edit_namelist("planet_namelist","MVELP",str(self.lonvernaleq))
            if key=="fixedorbit":
                self.fixedorbit=value
                self._edit_namelist("planet_namelist","NFIXORB",str(self.fixedorbit*1))
                
            if key=="orography":
                self.orography=value
                self._edit_namelist("landmod_namelist","OROSCALE",str(self.orography))
                self._edit_namelist("glacier_namelist","NGLACIER",str((self.orography!=1)*1))
            if key=="seaice":
                self.seaice=value
                self._edit_namelist("radmod_namelist","NRADICE",str(self.seaice*1))
            if key=="co2weathering":
                self.co2weathering=value
                self._edit_namelist("carbonmod_namelist","NCARBON",str(self.co2weathering*1))
            if key=="evolveco2":
                self.evolveco2=value
                self._edit_namelist("carbonmod_namelist","NCO2EVOLVE",str(self.evolveco2*1))
            if key=="erosionsupplylimit":
                self.erosionsupplylimit=value
                flag = bool(self.erosionsupplylimit)*1
                self._edit_namelist("carbonmod_namelist","NSUPPLY",str(flag))
                self._edit_namelist("carbonmod_namelist","WMAX",
                                        str(self.erosionsupplylimit*flag+1.0*(1-flag)))
            if key=="outgassing":
                self.outgassing=value
                self._edit_namelist("carbonmod_namelist","VOLCANCO2",str(self.outgassing))
                
            if key=="physicsfilter":
                self.physicsfilter=value
                if self.physicsfilter:
                    vals = self.physicsfilter.split("|")
                    if "gp" in vals:
                        self._edit_namelist("plasim_namelist","NGPTFILTER","1")
                    if "sp" in vals:
                        self._edit_namelist("plasim_namelist","NSPVFILTER","1")
                    if "none" in vals:
                        self._edit_namelist("plasim_namelist","NFILTER","0")
                    if "cesaro" in vals:
                        self._edit_namelist("plasim_namelist","NFILTER","1")
                    if "exp" in vals:
                        self._edit_namelist("plasim_namelist","NFILTER","2")
                    if "lh" in vals:
                        self._edit_namelist("plasim_namelist","NFILTER","3")
                else:
                    self._edit_namelist("plasim_namelist","NGPTFILTER","0")
                    self._edit_namelist("plasim_namelist","NSPVFILTER","0")
            if key=="filterkappa":
                self.filterkappa=value
                self._edit_namelist("plasim_namelist","FILTERKAPPA",str(self.filterkappa))
            if key=="filterpower":
                self.filterpower=value
                self._edit_namelist("plasim_namelist","NFILTEREXP",str(self.filterpower))
            if key=="filterLHN0":
                self.filterLHN0=value
                self._edit_namelist("plasim_namelist","LANDHOSKN0",str(self.filterLHN0))
            if key=="diffusionwaven":
                self.diffusionwaven=value
                if value:
                    self._edit_namelist("plasim_namelist","NHDIFF",str(self.diffusionwaven))
                else:
                    self._rm_namelist_param("plasim_namelist","NHDIFF")
            if key=="qdiffusion":
                self.qdiffusion=value
                if value:
                    self._edit_namelist("plasim_namelist","TDISSQ","%d*%f"%(self.layers,
                                                                        self.qdiffusion))
                else:
                    self._rm_namelist_param("plasim_namelist","TDISSQ")
            if key=="tdiffusion":
                self.tdiffusion=value
                if value:
                    self._edit_namelist("plasim_namelist","TDISST","%d*%f"%(self.layers,
                                                                        self.tdiffusion))
                else:
                    self._rm_namelist_param("plasim_namelist","TDISST")
            if key=="zdiffusion":
                self.zdiffusion=value
                if value:
                    self._edit_namelist("plasim_namelist","TDISSZ","%d*%f"%(self.layers,
                                                                        self.zdiffusion))
                else:
                    self._rm_namelist_param("plasim_namelist","TDISSZ")
            if key=="ddiffusion":
                self.ddiffusion=value
                if value:
                    self._edit_namelist("plasim_namelist","TDISSD","%d*%f"%(self.layers,
                                                                        self.ddiffusion))
                else:
                    self._rm_namelist_param("plasim_namelist","TDISSD")
            if key=="diffusionpower":
                self.diffusionpower=value
                if value:
                    self._edit_namelist("plasim_namelist","NDEL","%d*%d"%(self.layers,
                                                                    self.diffusionpower))
                else:
                    self._rm_namelist_param("plasim_namelist","NDEL")
                    
            if key=="glaciers":
                self.glaciers=value
                self._edit_namelist("glacier_namelist","NGLACIER",
                                    str(self.glaciers["toggle"]*1))
                self._edit_namelist("glacier_namelist","GLACELIM",
                                    str(self.glaciers["mindepth"]))
                self._edit_namelist("glacier_namelist","ICESHEETH",
                                    str(self.glaciers["initialh"]))
                if self.glaciers["initialh"]>0:
                    os.system("rm %s/*174.sra %s/*1740.sra "+
                            "%s/*210.sra %s/*232.sra"%([self.workdir,]*4))
                
            if key=="snowicealbedo":
                self.snowicealbedo=value
                if type(self.snowicealbedo)!=type(None):
                    alb = str(self.snowicealbedo)
                    self._edit_namelist("seamod_namelist","ALBICE",alb)
                    self._edit_namelist("seamod_namelist","DICEALBMN","%s,%s"%(alb,alb))
                    self._edit_namelist("seamod_namelist","DICEALBMX","%s,%s"%(alb,alb))
                    self._edit_namelist("landmod_namelist","DSNOWALBMN","%s,%s"%(alb,alb))
                    self._edit_namelist("landmod_namelist","DSNOWALBMN","%s,%s"%(alb,alb))
                    self._edit_namelist("landmod_namelist","DGLACALBMN","%s,%s"%(alb,alb))
                    self._edit_namelist("landmod_namelist","DSNOWALB","%s,%s"%(alb,alb))
                else:
                    self._rm_namelist_param("seamod_namelist","ALBICE")
                    self._rm_namelist_param("seamod_namelist","DICEALBMN")
                    self._rm_namelist_param("seamod_namelist","DICEALBMX")
                    self._rm_namelist_param("landmod_namelist","DSNOWALBMN")
                    self._rm_namelist_param("landmod_namelist","DSNOWALBMN")
                    self._rm_namelist_param("landmod_namelist","DGLACALBMN")
                    self._rm_namelist_param("landmod_namelist","DSNOWALB")
            if key=="twobandalbedo":
                self.twobandalbedo=value
                self._edit_namelist("radmod_namelist","NSIMPLEALBEDO",
                                    str((not self.twobandalbedo)*1))
            if key=="maxsnow":
                self.maxsnow=value
                if maxsnow:
                    self._edit_namelist("landmod_namelist","DSMAX",str(self.maxsnow))
                else:
                    self._rm_namelist_param("landmod_namelist","DSMAX")
            if key=="soilalbedo":
                self.soilalbedo=value
                if type(self.soilalbedo)!=type(None):
                    alb = str(self.soilalbedo)
                    os.system("rm %s/*0174.sra"%self.workdir)
                    self._edit_namelist("landmod_namelist","ALBLAND",alb)
                    self._edit_namelist("landmod_namelist","DGROUNDALB","%s,%s"%(alb,alb))
                else:
                    self._rm_namelist_param("landmod_namelist","ALBLAND")
                    self._rm_namelist_param("landmod_namelist","DGROUNDALB")
            
            if key=="oceanalbedo":
                self.oceanalbedo=value
                if type(self.oceanalbedo)!=type(None):
                    alb = str(self.oceanalbedo)
                    self._edit_namelist("seamod_namelist","ALBSEA",alb)
                    self._edit_namelist("seamod_namelist","DOCEANALB","%s,%s"%(alb,alb))
                else:
                    self._rm_namelist_param("seamod_namelist","ALBSEA")
                    self._rm_namelist_param("seamod_namelist","DOCEANALB")
                
            if key=="oceanzenith":
                self.oceanzenith=value
                if self.oceanzenith=="lambertian" or self.oceanzenith=="Lambertian" or self.oceanzenith=="uniform":
                    self._edit_namelist("radmod_namelist","NECHAM","0")
                    self._edit_namelist("radmod_namelist","NECHAM6","0")
                if self.oceanzenith=="default" or self.oceanzenith=="plasim" or self.oceanzenith=="ECHAM-3":
                    self._edit_namelist("radmod_namelist","NECHAM","1")
                    self._edit_namelist("radmod_namelist","NECHAM6","0")
                if self.oceanzenith=="ECHAM-6":
                    self._edit_namelist("radmod_namelist","NECHAM","0")
                    self._edit_namelist("radmod_namelist","NECHAM6","1")
                
            if key=="wetsoil":
                self.wetsoil=value
                self._edit_namelist("landmod_namelist","NWETSOIL",str(self.wetsoil*1))
            if key=="soilwatercap":
                self.soilwatercap=value
                if self.soilwatercap:
                    self._edit_namelist("landmod_namelist","WSMAX",str(self.soilwatercap))
                    os.system("rm %s/*0229.sra"%self.workdir)
                else:
                    self._rm_namelist_param("landmod_namelist","WSMAX")
            if key=="soilsaturation":
                self.soilsaturation=value
                if type(self.soilsaturation)!=type(None):
                    self._edit_namelist("landmod_namelist","NWATCINI","1")
                    self._edit_namelist("landmod_namelist","DWATCINI",str(self.soilsaturation))
                    os.system("rm %s/*0229.sra"%self.workdir)
                else:
                    self._edit_namelist("landmod_namelist","NWATCINI","0")
                    self._rm_namelist_param("landmod_namelist","DWATCINI")
            if key=="desertplanet":
                self.desertplanet=value
                if self.desertplanet:
                    self._edit_namelist("plasim_namelist","NDESERT","1")
                    if "soilsaturation" in kwargs.keys():
                        if kwargs["soilsaturation"] is None:
                            self._edit_namelist("landmod_namelist","NWATCINI","1")
                            self._edit_namelist("landmod_namelist","DWATCINI","0.0")
                    else:
                        self._edit_namelist("landmod_namelist","NWATCINI","1")
                        self._edit_namelist("landmod_namelist","DWATCINI","0.0")
                    os.system("rm %s/*.sra"%self.workdir)
                else:
                    self._edit_namelist("landmod_namelist","NDESERT","0")
                    self._rm_namelist_param("landmod_namelist","NWATCINI")
                    self._rm_namelist_param("landmod_namelist","DWATCINI")
            if key=="aquaplanet":
                self.aquaplanet=value
                if self.aquaplanet:
                    self._edit_namelist("plasim_namelist","NAQUA","1")
                    os.system("rm %s/*.sra"%self.workdir)
                else:
                    self._edit_namelist("plasim_namelist","NAQUA","0")

            if key=="drycore":
                self.drycore=value
                self._edit_namelist("fluxmod_namelist","NEVAP",str((not self.drycore)*1))
        
            if key=="columnmode":
                self.columnmode=value
                if self.columnmode:
                    parts = self.columnmode.split("|")
                    if "static" in parts:
                        self._edit_namelist("plasim_namelist","NADV","0")
                    else:
                        self._edit_namelist("plasim_namelist","NADV","1")
                    if "clear" in parts:
                        self._edit_namelist("radmod_namelist","NCLOUDS","0")
                        self._edit_namelist("radmod_namelist","ACLLWR","0.0")
                    else:
                        self._edit_namelist("radmod_namelist","NCLOUDS","1")
                        self._rm_namelist_param("radmod_namelist","ACLLWR")
                else:
                    self._rm_namelist_param("plasim_namelist","NADV")
                    self._rm_namelist_param("radmod_namelist","NCLOUDS")
                    self._rm_namelist_param("radmod_namelist","ACLLWR")
                    
            if key=="ozone":
                self.ozone=value
                self._edit_namelist("radmod_namelist","NO3",str(self.ozone*1))
                
            if key=="cpsoil":
                self.cpsoil=value
                if self.cpsoil:
                    self._edit_namelist("landmod_namelist","SOILCAP",str(self.cpsoil))
                else:
                    self._rm_namelist_param("landmod_namelist","SOILCAP")
                
            if key=="soildepth":
                self.soildepth=value
                self.dzsoils = np.array([0.4, 0.8, 1.6, 3.2, 6.4])*soildepth
                self._edit_namelist("landmod_namelist",
                                    "DSOILZ",",".join(self.dzsoils.astype(str)))
                
            if key=="mldepth":
                self.mldepth=value
                self._edit_namelist("oceanmod_namelist","MLDEPTH",str(self.mldepth))
                
            if key=="writefrequency":
                self.writefrequency=value
                if self.writefrequency:
                    self._edit_namelist("plasim_namelist","NWPD",str(self.writefrequency))
                else:
                    self._rm_namelist_param("plasim_namelist","NWPD")
                
            if key=="modeltop":
                changeatmo=True
                self.modeltop=value
            if key=="stratosphere":
                changeatmo=True
                self.stratosphere=value
            if key=="tropopause":
                changeatmo=True
                self.tropopause=value
            
            if key=="runscript":
                self.runscript=value
                
            if key=="highcadence":
                self.highcadence=value
                self._edit_namelist("plasim_namelist","NHCADENCE",
                                    str(self.highcadence["toggle"]))
                self._edit_namelist("plasim_namelist","HCSTARTSTEP",
                                    str(self.highcadence["start"]))
                self._edit_namelist("plasim_namelist","HCENDSTEP",
                                    str(self.highcadence["end"]))
                self._edit_namelist("plasim_namelist","HCINTERVAL",
                                    str(self.highcadence["interval"]))
                
            if key=="snapshots":
                self.snapshots=value
                if self.snapshots:
                    self._edit_namelist("plasim_namelist","NSNAPSHOT","1")
                    self._edit_namelist("plasim_namelist","NSTPS",str(self.snapshots))
                else:
                    self._rm_namelist_param("plasim_namelist","NSTPS")
                    self._edit_namelist("plasim_namelist","NSNAPSHOT","0")
                    
            if key=="resources":
                self.resources=value
                if len(self.resources)>0:
                    for res in self.resources:
                        os.system("cp %s %s/"%(res,self.workdir))
                
            if key=="landmap":
                self.landmap=value
                changeland=True
            if key=="topomap":
                self.topomap=value
                changeland=True
                
            if key=="stormclim":
                self.stormclim=value
                if self.stormclim:
                    self._edit_namelist("hurricane_namelist","NSTORMDIAG","1")
                    self._add_postcodes("example.nl",[322,323,324,325,326,327,328,329])
                    self._add_postcodes("snapshot.nl",[322,323,324,325,326,327,328,329])
                else:
                    self._edit_namelist("hurricane_namelist","NSTORMDIAG","0")
                    self._rm_postcodes("example.nl",[322,323,324,325,326,327,328,329])
                    self._rm_postcodes("snapshot.nl",[322,323,324,325,326,327,328,329])
            if key=="nstorms":
                self.nstorms=value
                self._edit_namelist("hurricane_namelist","NSTORMS",str(self.int(nstorms)))
            if key=="stormcapture":
                self.stormcapture=value
                if self.stormcapture["toggle"]:
                    self._edit_namelist("hurricane_namelist","HC_CAPTURE","1")
                    for param in self.stormcapture:
                        if param!="toggle":
                            self._edit_namelist("hurricane_namelist",param,
                                                str(self.stormcapture[param]))
                else:
                    self._edit_namelist("hurricane_namelist","HC_CAPTURE","0")
            
            if key=="threshold":
                self.threshold = value
            
            if key=="otherargs":
                otherargs=value
                if len(otherargs)>0:
                    for key in otherargs:
                        destination=key.split("@")
                        value=otherargs[key]
                        field=destination[0]
                        namelist=destination[1]
                        self._edit_namelist(namelist,field,value)
                        self.otherargs[key]=value
                
        if setgas:
            
            if setpressure:
                newpressure=pressure
            
            pressure=0.0
            for gas in self.pgases:
                pressure+=self.pgases[gas]
            
            pscalef = pressure/oldpressure
            
            gasesvx = {}
            for gas in self.pgases:
                gasesvx[gas[1:]] = self.pgases[gas]/pressure
            self.mmw = 0
            for gas in gasesvx:
                self.mmw += gasesvx[gas]*smws['m'+gas]
            self.gascon = 8314.46261815324 / self.mmw
            
            if setgascon:
                self.gascon=gascon
                self.mmw = 8314.46261815324/self.gascon
            
            print('Mean Molecular Weight set to %1.4f g/mol'%self.mmw)
            if setpressure:
                self.pressure=newpressure
            else:
                self.pressure *= pscalef
            print("Surface Pressure set to %1.6f bars"%self.pressure)
            self._edit_namelist("plasim_namelist","PSURF",str(self.pressure*1.0e5))
            self._edit_namelist("planet_namelist","GASCON",str(self.gascon))
            
                
            if 'pCO2' in self.pgases:
                self.CO2ppmv = self.pgases['pCO2']/self.pressure * 1.0e6 #ppmv
                self._edit_namelist("radmod_namelist","CO2",self.CO2ppmv)
        
        else:
            if setpressure:
                self.pressure=pressure
                self._edit_namelist("plasim_namelist","PSURF",str(self.pressure))
            
        if restim:
            #self._edit_namelist("plasim_namelist","RESTIM","%f,%d*0.0"%(self.top_restoretime,self.layers-1))
            self._edit_namelist("plasim_namelist","NSPONGE","1")
            self._edit_namelist("plasim_namelist","DAMPSP","%"%self._top_restoretime)
        elif not restim and slowrotator:
            #self._edit_namelist("plasim_namelist","RESTIM","%f,%d*0.0"%(1.0,self.layers-1))
            self._edit_namelist("plasim_namelist","NSPONGE","1")
            self._edit_namelist("plasim_namelist","DAMPSP","1.0")
            self.top_restoretime=1.0
            
        
        if changeatmo:
            
            if self.stratosphere:
                self._edit_namelist("plasim_namelist","NEQSIG","5")
                if self.modeltop:
                    self._edit_namelist("plasim_namelist","PTOP2",str(self.modeltop*100.0)) 
                        #convert hPa->Pa
                if self.tropopause:
                    self._edit_namelist("plasim_namelist","PTOP",str(self.tropopause*100.0))
            else:
                if self.modeltop:
                    self._edit_namelist("plasim_namelist","PTOP",str(self.modeltop*100.0)) 
                        #convert hPa->Pa
                    
        if changeland:
            if self.landmap or self.topomap:
                os.system("rm %s/*.sra"%self.workdir)
            if self.landmap:
                os.system("cp %s %s/N%03d_surf_0172.sra"%(self.landmap,self.workdir,self.nlats))
            if self.topomap:
                os.system("cp %s %s/N%03d_surf_0129.sra"%(self.topomap,self.workdir,self.nlats))
    
    def save(self,filename=None):
        """Save the current Model object to a NumPy save file. 

        The model object can then be reinstantiated using ``numpy.load(savefile).item()``. 

        Parameters
        ----------
        filename : str, optional
            Filename to save to. If unspecified, will default to <modelname>.npy.

        Notes
        -----
        Note that these files are often not portable between versions of Python or machine architectures, so their use is only recommended internally. For sharing with other
        users, it is recommended that you use the :py:func:`exportcfg <exoplasim.Model.exportcfg>` function.

        See Also
        --------
        :py:func:`exportcfg <exoplasim.Model.exportcfg>` : Export model configuration to a portable text file.

"""
        if not filename:
            filename=self.workdir+"/model.npy"
        else:
            if filename[0]!="/" and filename[0]!="~":
                cwd = os.getcwd()
                os.chdir(self.workdir)
                os.chdir("..")
                nwd = os.getcwd()
                filename = nwd+"/"+filename
                os.chdir(cwd)
        try:
            np.save(filename,self,allow_pickle=True)
        except:
            np.save(filename,self)
            
    def exportcfg(self,filename=None):
        """Export model configuration to a text file that can be used as configuration input

        Write the current model configuration to a text file. This file can be shared and used by
        other users to recreate your model configuration.
            
        Parameters
        ----------
        filename : str, optional 
            Path to the file that should be written. If None (default), <modelname>.cfg
            will be created in the working directory.
            
        See Also
        --------
        :py:func:`loadconfig <exoplasim.Model.loadconfig>` : Load a saved configuration.
"""
        if not filename:
            filename = self.workdir+"/"+self.modelname+".cfg"
        cfg = []
        
        cfg.append(str(self.noutput*1))
        cfg.append(str(self.flux))
        cfg.append(str(self.startemp))
        cfg.append(str(self.starspec))#=_noneparse(cfg[3],str)
        gases = []
        for gas in self.pgases:
            gases.append(gas+"|"+str(self.pgases[gas]))
        gases = "&".join(gases)
        cfg.append(gases)# = cfg[4].split("&")
        cfg.append(str(self.gascon))# = float(cfg[5])
        cfg.append(str(self.pressure))# = float(cfg[6])
        cfg.append(str(self.pressurebroaden*1))# = bool(int(cfg[7]))
        cfg.append(str(self.vtype))# = int(cfg[8])
        cfg.append(str(self.rotationperiod))# = float(cfg[9])
        cfg.append(str(self.synchronous*1))# = bool(int(cfg[10]))
        cfg.append(str(self.substellarlon))# = float(cfg[11])
        cfg.append(str(self.restartfile))# = _noneparse(cfg[12],str)
        cfg.append(str(self.gravity))# = float(cfg[13])
        cfg.append(str(self.radius))# = float(cfg[14])
        cfg.append(str(self.eccentricity))# = _noneparse(cfg[15],float)
        cfg.append(str(self.obliquity))# = _noneparse(cfg[16],float)
        cfg.append(str(self.lonvernaleq))# = _noneparse(cfg[17],float)
        cfg.append(str(self.fixedorbit*1))# = bool(int(cfg[18]))
        cfg.append(str(self.orography))# = _noneparse(cfg[19],float)
        cfg.append(str(self.seaice*1))# = bool(int(cfg[20]))
        cfg.append(str(self.co2weathering*1))# = bool(int(cfg[21]))
        cfg.append(str(self.evolveco2*1))# = bool(int(cfg[22]))
        cfg.append(str(self.physicsfilter))# = _noneparse(cfg[23],str)
        cfg.append(str(self.filterkappa))# = float(cfg[24])
        cfg.append(str(self.filterpower))# = int(cfg[25])
        cfg.append(str(self.filterLHN0))# = float(cfg[26])
        cfg.append(str(self.diffusionwaven))# = _noneparse(cfg[27],int)
        cfg.append(str(self.qdiffusion))# = _noneparse(cfg[28],float)
        cfg.append(str(self.tdiffusion))# = _noneparse(cfg[29],float)
        cfg.append(str(self.zdiffusion))# = _noneparse(cfg[30],float)
        cfg.append(str(self.ddiffusion))# = _noneparse(cfg[31],float)
        cfg.append(str(self.diffusionpower))# = _noneparse(cfg[32],int)
        cfg.append(str(self.erosionsupplylimit))# = _noneparse(cfg[33],float)
        cfg.append(str(self.outgassing))# = float(cfg[34])
        cfg.append(str(self.snowicealbedo))# = _noneparse(cfg[35],float)
        cfg.append(str(self.twobandalbedo*1))# = bool(int(cfg[36]))
        cfg.append(str(self.maxsnow))# = _noneparse(cfg[37],float)
        cfg.append(str(self.soilalbedo))# = _noneparse(cfg[38],float)
        cfg.append(str(self.oceanalbedo))# = _noneparse(cfg[39],float)
        cfg.append(str(self.oceanzenith))# = cfg[40]
        cfg.append(str(self.wetsoil*1))# = bool(int(cfg[41]))
        cfg.append(str(self.soilwatercap))# = _noneparse(cfg[42],float)
        cfg.append(str(self.aquaplanet*1))# = bool(int(cfg[43]))
        cfg.append(str(self.desertplanet*1))# = bool(int(cfg[44]))
        cfg.append(str(self.soilsaturation))# = _noneparse(cfg[45],float)
        cfg.append(str(self.drycore*1))# = bool(int(cfg[46]))
        cfg.append(str(self.ozone*1))# = bool(int(cfg[47]))
        cfg.append(str(self.cpsoil))# = _noneparse(cfg[48],float)
        cfg.append(str(self.soildepth))# = float(cfg[49])
        cfg.append(str(self.mldepth))# = float(cfg[50])
        cfg.append(str(self.writefrequency))# = _noneparse(cfg[51],int)
        cfg.append(str(self.modeltop))# = _noneparse(cfg[52],float)
        cfg.append(str(self.stratosphere*1))# = bool(int(cfg[53]))
        cfg.append(str(self.tropopause))# = _noneparse(cfg[54],float)
        cfg.append(str(self.timestep))# = float(cfg[55])
        cfg.append(str(self.runscript))# = _noneparse(cfg[56],str)
        cfg.append(str(self.columnmode))# = _noneparse(cfg[57],str)
        hcdict = []
        for hc in self.highcadence:
            hcdict.append(hc+"|"+str(self.highcadence[hc]))
        hcdict = "&".join(hcdict)
        cfg.append(hcdict)
        cfg.append(str(self.snapshots))# = _noneparse(cfg[59],int)
        cfg.append("&".join(self.resources))
        cfg.append(str(self.landmap))# = _noneparse(cfg[61],str)
        cfg.append(str(self.topomap))# = _noneparse(cfg[62],str)
        cfg.append(str(self.stormclim*1))# = bool(int(cfg[63]))
        cfg.append(str(self.nstorms))# = int(cfg[64])
        stormdict = []
        for arg in self.stormcapture:
            stormdict.append(arg+"|"+str(self.stormcapture[arg]))
        stormdict = "&".join(stormdict)
        cfg.append(stormdict)
        otherdict = []
        for arg in self.otherargs:
            item = arg+"|"+str(self.otherargs[arg])
            if type(self.otherargs[arg])==int:
                item+="~i"
            if type(self.otherargs[arg])==str:
                item+="~s"
            if type(self.otherargs[arg])==float:
                item+="~f"
            otherdict.append(item)
        cfg.append("&".join(otherdict))
        if self.sidyear:
            cfg.append(str(self.sidyear*86400.0))
        else:
            cfg.append(str(self.sidyear))
            
        cfg.append("&".join([str(self.glaciers["toggle"]*1),
                            str(self.glaciers["mindepth"]),
                            str(self.glaciers["initialh"])]))
        
        cfg.append(str(self.threshold))
        cfg.append(str(self.tlcontrast))
        cfg.append(str(self.top_restoretime))
        cfg.append(str(self.runsteps))
        cfg.append(str(self.desync))
        
        print("Writing configuration....\n"+"\n".join(cfg))
        print("Writing to %s...."%filename)
        with open(filename,"w") as cfgf:
            cfgf.write("\n".join(cfg))
        
    def _rm_namelist_param(self,namelist,arg,val):
        """Remove an argument from a namelist"""
        
        f=open(self.workdir+"/"+namelist,"r")
        fnl=f.read().split('\n')
        f.close()
        found=False
        fnl1=fnl[1].split(' ')
        if '=' in fnl1:
            mode='EQ'
        else:
            mode='CM'
        #print fnl1
        item = fnl1[-1]
        if item=='':
            item = fnl1[-2]
        if item.strip()[-1]!=",":
            mode='EQ'
        
        for l in range(1,len(fnl)-2):
            fnl[l]=fnl[l].split(' ')
            if arg in fnl[l]:
                found=True
            elif (arg+'=') in fnl[l]:
                found=True
            if found:
                fnl.pop(l)
                break
                
        f=open(self.workdir+"/"+namelist,"w")
        f.write('\n'.join(fnl))
        f.close()
            
    def _edit_namelist(self,namelist,arg,val):
        """Either edit or add argument/value pair to a namelist"""
        
        f=open(self.workdir+"/"+namelist,"r")
        fnl=f.read().split('\n')
        f.close()
        found=False
        fnl1=fnl[1].split(' ')
        if '=' in fnl1:
            mode='EQ'
        else:
            mode='CM'
        #print fnl1
        item = fnl1[-1]
        if item=='':
            item = fnl1[-2]
        if item.strip()[-1]!=",":
            mode='EQ'
        
        for l in range(1,len(fnl)-2):
            fnl[l]=fnl[l].split(' ')
            if arg in fnl[l]:
                fnl[l]=['',arg,'','=','',str(val),'']
                found=True
            elif (arg+'=') in fnl[l]:
                tag = ','
                item = fnl[l][-1]
                k=-1
                while item=='':
                    k-=1
                    item = fnl[l][k]
                if item.strip()[-1]!=',':
                    tag = ''
                fnl[l]=['',arg+'=','',str(val),'',tag]
                found=True
            fnl[l]=' '.join(fnl[l])
        if not found:
            if mode=='EQ':
                fnl.insert(-3,' '+arg+' = '+val+' ')
            else:
                fnl.insert(-3,' '+arg+'= '+val+' ,')
            
        f=open(self.workdir+"/"+namelist,"w")
        f.write('\n'.join(fnl))
        f.close()
        
    def _edit_postnamelist(self,namelist,arg,val):
        """Edit postprocessing namelist"""
        
        with open(self.workdir+"/"+namelist,"r") as f:
            pnl = f.read().split('\n')
            
        flag=False
        pnl = [y for y in pnl if y!='']
        for n in range(len(pnl)):
            if pnl[n].split('=')[0].strip()==arg:
                pnl[n]=arg+"="+val
                flag=True
                break
        if not flag:
            pnl.append(arg+'='+val)
        pnl.append('')
        
        with open(self.workdir+"/"+namelist,"w") as f:
            f.write('\n'.join(pnl))
            
    def _add_postcodes(self,namelist,newcodes):
        """Add postprocessor codes to postprocessor namelist"""
        
        with open(self.workdir+"/"+namelist,"r") as f:
            pnl = f.read().split('\n')
        pnl = [y for y in pnl if y!='']
        for n in range(len(pnl)):
            if pnl[n].split('=')[0].strip()=="code":
                codes = pnl[n].split('=')[1].strip().split(',')
                lineno=n
                break
        ncodes = [int(n) for n in codes]
        for n in newcodes:
            if n not in ncodes:
                ncodes.append(n)
        pnl[lineno]+=','+','.join([str(n) for n in ncodes])
        #print "Writing to %s/%s: \n"%(home,filename)+'\n'.join(pnl)+"\n"
        with open(self.workdir+"/"+namelist,"w") as f:
            f.write('\n'.join(pnl)+"\n")

    def _rm_postcodes(self,namelist,rmcodes):
        """Add postprocessor codes to postprocessor namelist"""
        
        with open(self.workdir+"/"+namelist,"r") as f:
            pnl = f.read().split('\n')
        pnl = [y for y in pnl if y!='']
        for n in range(len(pnl)):
            if pnl[n].split('=')[0].strip()=="code":
                codes = pnl[n].split('=')[1].strip().split(',')
                lineno=n
                break
        ncodes = [int(n) for n in codes]
        
        newcodes = []
        for n in ncodes:
            if n not in rmcodes:
                newcodes.append(n)
        pnl[lineno]+=','+','.join([str(n) for n in newcodes])
        #print "Writing to %s/%s: \n"%(home,filename)+'\n'.join(pnl)+"\n"
        with open(self.workdir+"/"+namelist,"w") as f:
            f.write('\n'.join(pnl)+"\n")


class TLaquaplanet(Model):
    """Create a tidally-locked planet with no land.

    Identical to :py:class:`Model <exoplasim.Model>`, except configuration options suitable for
    tidally-locked models are the default when configure() is called,
    and the surface is entirely ocean-covered. Specifically, a 30-minute
    timestep, snapshot outputs every 720 timesteps, eccentricity=0.0,
    0-degree obliquity, exponential physics filtering, fixed orbital
    parameters, and no ozone. All these defaults can be overridden.
"""
    def configure(self,timestep=30.0,snapshots=720,eccentricity=0.0,ozone=False,
                obliquity=0.0,physicsfilter="gp|exp|sp",tlcontrast=100.0,**kwargs):
        super(TLaquaplanet,self).configure(synchronous=True,fixedorbit=True,aquaplanet=True,
                        eccentricity=eccentricity,obliquity=obliquity,timestep=timestep,
                        snapshots=snapshots,physicsfilter=physicsfilter,ozone=ozone,
                        **kwargs)
        
class TLlandplanet(Model): #Default will be ZERO soil water; set soilsaturation if you want any
    """Create a tidally-locked model with no oceans.

    Identical to :py:class:`Model <exoplasim.Model>`, except configuration options suitable for
    tidally-locked models are the default when configure() is called,
    and the surface is entirely land-covered. Specifically, a 30-minute
    timestep, snapshot outputs every 720 timesteps, eccentricity=0.0,
    0-degree obliquity, exponential physics filtering, fixed orbital
    parameters, and no ozone. All these defaults can be overridden.

    Notes
    -----
    The default is to include zero soil water initially. This will result in a completely dry
    model. Set soilsaturation to something nonzero if you want groundwater.
"""
    def configure(self,timestep=30.0,snapshots=720,eccentricity=0.0,ozone=False,
                obliquity=0.0,physicsfilter="gp|exp|sp",tlcontrast=100.0,**kwargs):
        super(TLlandplanet,self).configure(synchronous=True,fixedorbit=True,desertplanet=True,
                        eccentricity=eccentricity,obliquity=obliquity,timestep=timestep,
                        snapshots=snapshots,physicsfilter=physicsfilter,ozone=ozone,
                        **kwargs)
        
class Earthlike(Model):
    """Create an Earth-like model, but more flexible.

    Identical to :py:class:`Model <exoplasim.Model>`, except configuration options common for
    Earth-like models requiring slightly more flexibility are 
    the default when configure is called--specifically, 45-minute 
    timestep, snapshot output reporting every 480 timesteps, and 
    a model top pinned to 50 mbar. All these defaults can be overridden.
"""
    def configure(self,timestep=45.0,snapshots=480,vtype=4,modeltop=50.0,**kwargs):
        super(Earthlike,self).configure(vtype=vtype,modeltop=modeltop,timestep=timestep,
                        snapshots=snapshots,**kwargs)

class TLmodel(Model):
    """Create a tidally-locked model.    

    Identical to :py:class:`Model <exoplasim.Model>`, except configuration options suitable for
    tidally-locked models are the default when configure() is called.
"""
    def configure(self,timestep=30.0,snapshots=720,eccentricity=0.0,ozone=False,
                obliquity=0.0,physicsfilter="gp|exp|sp",tlcontrast=100.0,**kwargs):
        super(TLmodel,self).configure(synchronous=True,fixedorbit=True,
                        eccentricity=eccentricity,obliquity=obliquity,timestep=timestep,
                        snapshots=snapshots,physicsfilter=physicsfilter,ozone=ozone,
                        **kwargs)
    