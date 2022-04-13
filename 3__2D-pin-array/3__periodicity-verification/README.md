# How to set up a periodic verification

## 1. fluid-only

Compare the results for a periodic simulation with those of a nonperiodic, but downstream repeated case.
After a certain amounf of copies, the simulation results should be the same.
The specific amount of copies necessary depends on the configuration (mesh, BC, material, etc.).

### Pressure, Velocity

In order to compare the results, it is easiest, to have an identical massflow in both simulations.
Two methods for the `VELOCITY_INLET` can be used (the outlet will always be `PRESSURE_OUTLET= 0.0`):
1. Use a block profile and choose the VelMag to fit the massflow requirement: i.e. v_mag[m/s] = m_dot[kg/s] / ( inlet_area[m^2] * density[kg/m^3] )
   MUSCL_FLOW= YES With the current values it is v_mag = 0.85 / ( 0.00122 * 1045 ) = 0.66671896
   MUSCL_FLOW= NO  With the current values it is v_mag = 0.773057117251 / ( 0.00122 * 1045 ) = 0.60636686583
   NOTE: All simulations here are performed without MUSCL reconstruction!
2. Extract and impose the profile from the periodic simulation. Like so, there should be no change over a periodic downstream length whatsoever.

How to visualize?
Take the Velocity profile starting from the top of the middle pin. 
This might avoid any weird effects from the outlet/inlet boundary in case that would be taken.

### Temperature

For true periodicity only constant Heatflux markers can be taken.

The temperature offset per domain is deltaT = Q[W] / (m_dot[kg/s]*c_p[J/(kg*K)])
With cp=3540 and m_dot as a simulation results 0.773057. Q can be determined from the constant HF boundary: The combined boundaries form a full circle so Q = q * 2*radius*pi
The Radius is 0.00322 (total-height) - 0.00122 (inlet-height) = 0.002 (pin-radius)
Such that deltaT= 5e5*0.002*2*pi / (0.773057*3540) = 2.295964[K] ~2.23[K]
I.e. The estimation of the periodic profile has to added with deltaT*ith-copy at each point in order to receive the Temperature estimate at that downstream length.

The very same concept applies to the pressure profile but much more straight forward as the pressure drop is prescribed with 208.023676[Pa]

Additionally an absolute threshold needs to be added/substracted to get on the same value-level.
The profile-by-profile is just one aspect but there needs to be an anchor for comparison, e.g. T on one of the borders (preferably symmetry) or the minimim is the same.

How to visualize?
Take the temperature profile from the top of the middle pin.

## 2. solid-only

Here one periodic simulation is enough as a full non-periodic half pin is already present in the domain.
It is necessary though to have a non-uniform boundary condition as otherwise the result will be symmetric which is not ideal to proove the validity of the implemntation

## 3. CHT

Here the Temperature should be taken from the middle pin. And the Pins should be connected periodically. Nothing changes for the downstream connedted simulation.

