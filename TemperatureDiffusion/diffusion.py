#import libraries
import numpy as np


#Setup parameters
dx = 0.05    #length of spatial step
L = 1        #length of bar in meters
dt = 2       #seconds
tmax = 3600   #seconds
k = 205       #J/s/m/K
c = 900      #J/kg/K
rho = 2700   #density, kg/m3
kappa = k/(c*rho) #diffusion coef

#specific initial and boundary conditions
T0 = 50      #initial condition, degrees C
Tleft = 100    #left boundary, degrees C
Tright = 0 #right boundary, degrees C

#create x every dx values and t every dt values (for graphing)
x = np.arange(0,L+dx,dx)
t = np.arange(0,tmax+dt,dt)

#find index of maximum row and column numbers
rowmax = int(tmax/dt)
columnmax = int(L/dx)

#create an array of empty Temperature values (actually an array of 1s)
T=np.ones((rowmax+1,columnmax+1))

#set initial conditions
T[0,...]=T0

#set boundary conditions
T[...,0] = Tleft
T[...,columnmax] = Tright

#recursively compute value of T for all other cells
#start at row 0 and go to the next to last row
for i in range(0,rowmax):   
    #start at column 1 and go to the next to last column
    for m in range(1,columnmax):  
        T[i+1,m]=T[i,m]+ kappa * dt/dx**2*(T[i,m+1]-2*T[i,m]+T[i,m-1])

import matplotlib.pyplot as plt
import matplotlib.animation as animation

#Create plot of T vs t at x = 95, 50, and 5 cm
fig1 = plt.figure()
subfig = fig1.add_subplot(1, 1, 1)
line, = subfig.plot(t,T[:,19],label='95 cm')
line2, = subfig.plot(t,T[:,10],label='50 cm')
line3, = subfig.plot(t,T[:,1],label='5 cm')
subfig.legend()
plt.ylabel('Temperature (°C)')
plt.xlabel('Time (s)')

#Create plot of T vs x at t = 5, 10, 30, and 60 minutes
fig2 = plt.figure()
subfig = fig2.add_subplot(1, 1, 1)
line, = subfig.plot(x,T[150,:],label='5 min')
line2, = subfig.plot(x,T[300,:],label='10 min')
line3, = subfig.plot(x,T[900,:],label='30 min')
line4, = subfig.plot(x,T[1800,:],label='60 min')
subfig.legend()
plt.ylabel('Temperature (°C)')
plt.xlabel('x (m)')

#import data from instructor file and plot on figure 1 at 10 minutes
ObservedT = np.genfromtxt('instructor.txt', delimiter=',', skip_header=1)
#define x values
x_instructor = np.array([0.05, 0.2,0.4, 0.6, 0.8, 0.95])
line5, = subfig.plot(x_instructor, ObservedT[62,1:7],'o', label = 'observed @ 10 min')
subfig.legend()
plt.plot

# Create figure for animation
fig3 = plt.figure()
subfig = fig3.add_subplot(1, 1, 1)
line, = subfig.plot(x,T[0,:])
plt.ylabel('Temperature (°C)')
plt.xlabel('distance (m)')

# This function is called periodically from FuncAnimation
def animate(i, x, T, t):
    #updata data in plot using index i
    line.set_ydata(T[i,:])
    # Format Title  with time in it
    plt.title('Time = %.2f seconds' %(t[i]))
    return line, #it is necessary to return this
# Set up plot to call animate() function periodically
ani = animation.FuncAnimation(fig3, animate, fargs=(x, T, t), interval=20, repeat=True, save_count=10)
plt.show()

plt.rcParams['animation.convert_path'] = 'C:\Program Files\ImageMagick-7.0.8-Q16\convert.exe' 
#plt.rcParams['animation.convert_path'] = 'C:\Program Files\ImageMagick-7.0.8-Q16\magick.exe'
ani.save('animation.gif', writer='imagemagick', fps=60)