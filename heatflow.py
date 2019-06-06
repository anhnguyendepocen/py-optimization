import numpy as np
from numba import jit, jitclass, int64, float64

spec = [('w', int64),
        ('h', int64),
        ('D', int64)]

@jitclass(spec)
class hotplate:
    def __init__(self, w=10, h=20, D=4):
        self.w = w
        self.h = h
        self.D = D

spec = [('boundary_conditions', float64[:]),
        ('relaxation_guess',float64),
        ('ds',float64),
        ('maxiter',int64),
        ('dx', float64),
        ('dy', float64),
        ('dx2', float64),
        ('dy2', float64),
        ('nx', int64),
        ('ny', int64),
        ('dt', float64),
        ('u0', float64[:,:]),
        ('u', float64[:,:]),
        ('D', float64)]
@jitclass(spec)
class steadystate:
    def __init__(self,
                 hotplate,
                 boundary_conditions=[100.,0.,0.,.0],
                 relaxation_guess=30.,
                 ds = 0.1,
                 maxiter=500):
        self.boundary_conditions = boundary_conditions
        self.relaxation_guess = relaxation_guess
        self.ds = 0.1
        self.maxiter = maxiter
        self.D = hotplate.D # not perfect, but okay


        # SEE: second derivatives of spatially-dependent terms
        self.dx, self.dy = ds, ds
        self.dx2, self.dy2 = (self.dx*self.dx), (self.dy*self.dy)
        self.dt = self.dx2*self.dy2 / (2 * hotplate.D * (self.dx2 + self.dy2))

        # number of discrete points in each cardinal direction
        self.nx, self.ny = int(hotplate.w/self.dx), int(hotplate.h/self.dy)

        # Initialize the array we'll do calculations on
        # and set the interior value to Tguess
        self.u0 = np.empty((self.nx, self.ny), dtype=np.float64)

        for i in range(self.nx):
            for j in range(self.ny):
                self.u0[i, j] = relaxation_guess

        # Set boundary conditions for the steady state before t=0
        self.u0[:, (self.ny-1):] = boundary_conditions[0]
        self.u0[:, :1] = boundary_conditions[1]
        self.u0[:1, :] = boundary_conditions[-2]
        self.u0[(self.nx-1):, :] = boundary_conditions[-1]
        
    def calculate(self):
        # Compute the steady state distribution, where u0 = Steady-State Temperature Matrix
        for iteration in range(0, self.maxiter):
            for i in range(1, self.nx-1):
                for j in range(1, self.ny-1):
                    self.u0[i, j] = (0.25) * (self.u0[i+1][j] + self.u0[i-1][j] +
                                        self.u0[i][j+1] + self.u0[i][j-1])

spec = []
@jitclass(spec)
class hotboundaries:
    def __init__(self,
                 steadyplate, # pass in a hotplate with an initialized and/or state
                 boundary_conds=[0.0,0.0,0.0,0.0]):
        
        # New initial conditions
        Ttop_new = boundary_conds[0]
        Tbottom_new = boundary_conds[1]
        Tleft_new = boundary_conds[-2]
        Tright_new = boundary_conds[-1]

        # Set new boundary conditions in the steady-state matrix
        steadyplate.u0[:, :5] = Tbottom_new
        steadyplate.u0[(steadyplate.nx-5):, :] = Tright_new
        steadyplate.u0[:5, :] = Tleft_new
        steadyplate.u0[:, (steadyplate.ny-5):] = Ttop_new

    
# produce a hot spot on the plate and observe thermal diffusion
# circle of radius r, centred at c=(cx,cy)
spec = []
@jitclass(spec)
class hotspot:
    def __init__(self,
                 steadyplate, # pass in a hotplate with an initialized and/or steady state
                 temperature = 200, # temperature of spot
                 r = 1, # radius of circle
                 c = (0, 0) # position of center of circle on plate
                 ): 
        r2 = r*r # radius-squared
        for i in range(steadyplate.nx):
            for j in range(steadyplate.ny):
                p2 = (i * steadyplate.dx - c[0])**2 + (j * steadyplate.dy - c[1])**2
                if p2 < r2:
                    steadyplate.u0[i, j] = temperature
                    
spec = [('tsteps', int64),
        ('D', float64),
        ('dx2', float64),
        ('dy2', float64),
        ('nx', float64),
        ('ny', float64),
        ('dt', float64),
        ('u0', float64[:,:]),
        ('u', float64[:,:]),
        ('frames', float64[:,:,:])]
@jitclass(spec)
class heatflow:    
    def do_timestep(self):
        # Propagate with forward-difference in time, central-difference in space
        self.u[1:-1, 1:-1] = self.u0[1:-1, 1:-1] + self.D * self.dt * (
            (self.u0[2:, 1:-1] - 2*self.u0[1:-1, 1:-1] + self.u0[:-2, 1:-1])/self.dx2
            + (self.u0[1:-1, 2:] - 2*self.u0[1:-1, 1:-1] + self.u0[1:-1, :-2])/self.dy2)

        self.u0 = self.u
        
    def __init__(self,
                 steadyplate # pass in a hotplate entity with an initialized and/or steady state
                ):
        self.u = steadyplate.u0.copy()
        self.u0 = steadyplate.u0
        self.dt = steadyplate.dt
        self.dx2 = steadyplate.dx2
        self.dy2 = steadyplate.dy2
        self.nx = steadyplate.nx
        self.ny = steadyplate.ny
        self.D = steadyplate.D
    
    def calculate(self,
                  tsteps, # number of time steps
                  snapshots # on which timesteps should snapshots (frames) be save for visualizing?
                  ):
        # create an array of frames for visualizing the heatflow
        self.frames = np.empty((int(self.nx), int(self.ny), len(snapshots)), dtype=np.float64)
        
        # index for saving frames on the z-axis if the self.frames
        i = 0
        
        # perform timestep calculations and save the frames
        for n in range(tsteps): 
            self.do_timestep()
            
            # save the specified frames
            if n in snapshots:
                self.frames[:,:,i] = self.u0.copy()
                i+=1