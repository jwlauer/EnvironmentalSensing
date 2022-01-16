# Import Numpy Library
import numpy as np


# Set parameters
dx = 0.05    #length of spatial step
L = 1        #length of bar in meters
dt = 10       #seconds
tmax = 4000   #seconds
k = 100 #205       #J/s/m/K
c = 900      #J/kg/K
rho = 2700   #density, kg/m3
kappa = k/(c*rho) #diffusion coef


# Specify initial and boundary conditions
T0 = 20      #initial condition, degrees C
Tleft = 100    #left boundary, degrees C
Tright = 0 #right boundary, degrees C

# Define and initialize grid
x = np.arange(0,L+dx,dx)
t = np.arange(0,tmax+dt,dt)

rowmax = int(tmax/dt)
columnmax = int(L/dx)


# Create an array of empty temperatures
T=np.ones((rowmax+1,columnmax+1))


# Set initial conditions
T[0,...]=T0


# Set boundary conditions
T[...,0] = Tleft
T[...,columnmax] = Tright


# Perform computations  
# start at row 0 and go to the last row
for i in range(0,rowmax):   
    #start at column 1 and go to the last column
    for m in range(1,columnmax):  
        T[i+1,m]=T[i,m]+ kappa * dt/dx**2*(T[i,m+1]-2*T[i,m]+T[i,m-1])


# Import graphing libraries
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

# Create plot of T vs t at x = 95, 50, and 5 cm
fig1 = plt.figure()
subfig = fig1.add_subplot(1, 1, 1)
line, = subfig.plot(t,T[:,19],label='95 cm')
line2, = subfig.plot(t,T[:,10],label='50 cm')
line3, = subfig.plot(t,T[:,1],label='5 cm')
subfig.legend()
plt.ylabel('Temperature (°C)')
plt.xlabel('Time (s)')

# Create plot of T vs x at t = 5, 10, 30, and 60 minutes
fig2 = plt.figure()
subfig = fig2.add_subplot(1, 1, 1)
line, = subfig.plot(x,T[int(5*60/dt),:],label='5 min')
line2, = subfig.plot(x,T[int(10*60/dt),:],label='10 min')
line3, = subfig.plot(x,T[int(30*60/dt),:],label='30 min')
line4, = subfig.plot(x,T[int(60*60/dt),:],label='60 min')
subfig.legend()
plt.ylabel('Temperature (°C)')
plt.xlabel('x (m)')

# Compare with observed data
#import data 
ObservedT = np.genfromtxt('instructor.txt', delimiter=',', skip_header=1)
#define x values
x_instructor = np.array([0.05, 0.2,0.4, 0.6, 0.8, 0.95])
line5, = subfig.plot(x_instructor, ObservedT[62,1:7],'o', label = 'observed @ 10 min')
subfig.legend()
fig2

# Create an animation
#get_ipython().run_line_magic('matplotlib', 'notebook')
#%matplotlib auto
#%matplotlib nbagg
fig3 = plt.figure()
subfig = fig3.add_subplot(1, 1, 1)
line, = subfig.plot(x,T[0,:])
subfig.set_ylabel('Temperature (°C)')
subfig.set_xlabel('distance (m)')

# Pad output array
T = np.pad(T,((50,50),(0,0)),'edge')
t = np.pad(t,50,'edge')

# Set up animation
# This function is called periodically from FuncAnimation
def animate(i, x, T, t):
    #line.set_xdata(x) #not needed here, but included to make function easier to modify
    line.set_ydata(T[i,:]) #update data in plot using index i
    plt.title(f'Time = {t[i]:.2f} seconds') # Format Title  with time in it
    return line, #it is necessary to return this

# Set up plot to call animate() function periodically
ani = FuncAnimation(fig3, animate, fargs=(x, T, t), 
                    interval=20, 
                    repeat=True, 
                    save_count=len(t)-1, 
                    #repeat_delay=2000, #does not work with PillowWriter
                    blit=True 
                    )
plt.show()

# Save the file
ani.save('animation.gif', writer=PillowWriter(fps=24))

# Add controllable animation to notebook
plt.rcParams['animation.html'] = 'jshtml'
ani

