
# RKF
Implementation of Runge-Kutta Fehlberg method to numerically solve system of ODEs.

*Developed by [Amirhossein Rezaei](https://www.researchgate.net/profile/Amirhossein-Rezaei-2?ev=hdr_xprf)*.

## The Lorenz system
The **Lorenz system** is a system of [ordinary differential equations](https://en.wikipedia.org/wiki/Ordinary_differential_equation "Ordinary differential equation") first studied by [Edward Lorenz](https://en.wikipedia.org/wiki/Edward_Norton_Lorenz "Edward Norton Lorenz"). It is notable for having [chaotic](https://en.wikipedia.org/wiki/Chaos_theory "Chaos theory") solutions for certain parameter values and initial conditions. In particular, the **Lorenz attractor** is a set of chaotic solutions of the Lorenz system. In popular media the '[butterfly effect](https://en.wikipedia.org/wiki/Butterfly_effect "Butterfly effect")' stems from the real-world implications of the Lorenz attractor, i.e. that in any physical system, in the absence of perfect knowledge of the initial conditions (even the minuscule disturbance of the air due to a butterfly flapping its wings), our ability to predict its future course will always fail. This underscores that physical systems can be completely deterministic and yet still be inherently unpredictable even in the absence of quantum effects. The shape of the Lorenz attractor itself, when plotted graphically, may also be seen to resemble a butterfly.

### Overview
In 1963, Edward Lorenz, with the help of Ellen Fetter, developed a simplified mathematical model for atmospheric convection. The model is a system of three ordinary differential equations now known as the Lorenz equations:

<p align="center">
  <img src="https://wikimedia.org/api/rest_v1/media/math/render/svg/7928004d58943529a7be774575a62ca436a82a7f" />
</p>

The equations relate the properties of a two-dimensional fluid layer uniformly warmed from below and cooled from above. In particular, the equations describe the rate of change of three quantities with respect to time: 
<a href="https://www.codecogs.com/eqnedit.php?latex=\large&space;x" target="_blank"><img src="https://latex.codecogs.com/svg.latex?\large&space;x" title="\large x" /></a> is proportional to the rate of convection, <a href="https://www.codecogs.com/eqnedit.php?latex=\large&space;y" target="_blank"><img src="https://latex.codecogs.com/svg.latex?\large&space;y" title="\large y" /></a>  to the horizontal temperature variation, and <a href="https://www.codecogs.com/eqnedit.php?latex=\large&space;z" target="_blank"><img src="https://latex.codecogs.com/svg.latex?\large&space;z" title="\large z" /></a>  to the vertical temperature variation. The constants <a href="https://www.codecogs.com/eqnedit.php?latex=\large&space;\sigma" target="_blank"><img src="https://latex.codecogs.com/svg.latex?\large&space;\sigma" title="\large \sigma" /></a> , <a href="https://www.codecogs.com/eqnedit.php?latex=\large&space;\rho" target="_blank"><img src="https://latex.codecogs.com/svg.latex?\large&space;\rho" title="\large \rho" /></a> , and <a href="https://www.codecogs.com/eqnedit.php?latex=\large&space;\beta" target="_blank"><img src="https://latex.codecogs.com/svg.latex?\large&space;\beta" title="\large \beta" /></a>  are system parameters proportional to the Prandtl number, Rayleigh number, and certain physical dimensions of the layer itself.

The Lorenz equations also arise in simplified models for lasers, dynamos, thermosyphons, brushless DC motors, electric circuits, chemical reactions and forward osmosis. The Lorenz equations are also the governing equations in Fourier space for the Malkus waterwheel. The Malkus waterwheel exhibits chaotic motion where instead of spinning in one direction at a constant speed, its rotation will speed up, slow down, stop, change directions, and oscillate back and forth between combinations of such behaviors in an unpredictable manner.

From a technical standpoint, the Lorenz system is nonlinear, non-periodic, three-dimensional and deterministic. The Lorenz equations have been the subject of hundreds of research articles, and at least one book-length study.
#### Analysis and code
One normally assumes that the parameters <a href="https://www.codecogs.com/eqnedit.php?latex=\large&space;\sigma" target="_blank"><img src="https://latex.codecogs.com/svg.latex?\large&space;\sigma" title="\large \sigma" /></a>, <a href="https://www.codecogs.com/eqnedit.php?latex=\large&space;\rho" target="_blank"><img src="https://latex.codecogs.com/svg.latex?\large&space;\rho" title="\large \rho" /></a> , and <a href="https://www.codecogs.com/eqnedit.php?latex=\large&space;\beta" target="_blank"><img src="https://latex.codecogs.com/svg.latex?\large&space;\beta" title="\large \beta" /></a>   are positive. Lorenz used the values <a href="https://www.codecogs.com/eqnedit.php?latex=\large&space;\sigma&space;=&space;10" target="_blank"><img src="https://latex.codecogs.com/svg.latex?\large&space;\sigma&space;=&space;10" title="\large \sigma = 10" /></a>, <a href="https://www.codecogs.com/eqnedit.php?latex=\large&space;\beta&space;=8/3" target="_blank"><img src="https://latex.codecogs.com/svg.latex?\large&space;\beta&space;=8/3" title="\large \beta =8/3" /></a>  and <a href="https://www.codecogs.com/eqnedit.php?latex=\large&space;\rho&space;=&space;28" target="_blank"><img src="https://latex.codecogs.com/svg.latex?\large&space;\rho&space;=&space;28" title="\large \rho = 28" /></a> . The system exhibits chaotic behavior for these (and nearby) values. Further explanation on [wiki](https://en.wikipedia.org/wiki/Lorenz_system#Analysis).  

```
import numpy as np
import matplotlib.pyplot as plt 
import time
from RKF import rkf
import matplotlib.animation as animation

def lorenz(t,u):
    s=10
    r=24
    b=8/3
    x,y,z=u
    vx=s*y-s*x
    vy=r*x-x*z-y
    vz=x*y-b*z
    return np.array([vx,vy,vz])

x0=[2,2,2]

t,u  = rkf( f=lorenz, a=0, b=1e+1, x0=x0, atol=1e-8, rtol=1e-6 , hmax=1e-1, hmin=1e-40,plot_stepsize=True).solve()

x,y,z= u.T

plt.style.use('dark_background')
fig = plt.figure()
ax = fig.gca(projection='3d')
ax.set_axis_off()
ax.plot(x,y,z,lw=0.5,c='whitesmoke')
# plt.show()

def rotate(angle):
    ax.view_init(elev=7.,azim=angle)

print("Making animation")
rot_animation = animation.FuncAnimation(fig, rotate, frames=np.arange(0, 600, 2), interval=36)
rot_animation.save('lorenz.gif', dpi=400, writer='imagemagick')

```
[![lorenz.gif](https://i.postimg.cc/C1QtR7xv/lorenz.gif)](https://postimg.cc/Fd0Gqjcc)
