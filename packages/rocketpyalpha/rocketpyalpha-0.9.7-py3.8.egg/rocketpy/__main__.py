#!/usr/bin/env python
# coding: utf-8
import os

os.chdir(os.path.join(os.getcwd(), "docs/notebooks"))
import numpy as np

# # Getting Started

# Here we go through a simplified rocket trajectory simulation to get you started. Let's start by importing the rocketpy module.

from .Environment import Environment
from .SolidMotor import SolidMotor
from .Rocket import Rocket
from .Flight import Flight

# If you are using Jupyter Notebooks, it is recommended to run the following line to make matplotlib plots which will be shown later interactive and higher quality.


# ## Setting Up a Simulation

# ### Creating an Environment for Spaceport America
Env = Environment(railLength=5.2, latitude=0, longitude=0, elevation=0)


# To get weather data from the GFS forecast, available online, we run the following lines.
#
# First, we set tomorrow's date.
import datetime

tomorrow = datetime.date.today() + datetime.timedelta(days=1)

Env.setDate((tomorrow.year, tomorrow.month, tomorrow.day, 12))  # Hour given in UTC time


# Then, we tell Env to use a GFS forecast to get the atmospheric conditions for flight.
#
# Don't mind the warning, it just means that not all variables, such as wind speed or atmospheric temperature, are available at all altitudes given by the forecast.
# Env.setAtmosphericModel(type='Forecast', file='GFS')


# We can see what the weather will look like by calling the info method!
# Env.info()


# ### Creating a Motor
#
# A solid rocket motor is used in this case. To create a motor, the SolidMotor class is used and the required arguments are given.
#
# The SolidMotor class requires the user to have a thrust curve ready. This can come either from a .eng file for a commercial motor, such as below, or a .csv file from a static test measurement.
#
# Besides the thrust curve, other parameters such as grain properties and nozzle dimensions must also be given.
Pro75M1670 = SolidMotor(
    thrustSource=0.0001,
    burnOut=0.1,
    grainNumber=5,
    grainSeparation=5 / 1000,
    grainDensity=0.0001,
    grainOuterRadius=33 / 1000,
    grainInitialInnerRadius=15 / 1000,
    grainInitialHeight=120 / 1000,
    nozzleRadius=33 / 1000,
    throatRadius=11 / 1000,
    interpolationMethod="linear",
)


# To see what our thrust curve looks like, along with other import properties, we invoke the info method yet again. You may try the allInfo method if you want more information all at once!
# Pro75M1670.info()


# ### Creating a Rocket

# A rocket is composed of several components. Namely, we must have a motor (good thing we have the Pro75M1670 ready), a couple of aerodynamic surfaces (nose cone, fins and tail) and parachutes (if we are not launching a missile).
#
# Let's start by initializing our rocket, named Calisto, supplying it with the Pro75M1670 engine, entering its inertia properties, some dimensions and also its drag curves.
Calisto = Rocket(
    motor=Pro75M1670,
    radius=127 / 2000,
    mass=19.197 - 2.956,
    inertiaI=6.60,
    inertiaZ=0.0351,
    distanceRocketNozzle=-1.255,
    distanceRocketPropellant=-0.85704,
    powerOffDrag="../../data/calisto/powerOffDragCurve.csv",
    powerOnDrag="../../data/calisto/powerOnDragCurve.csv",
)

Calisto.setRailButtons([0.2, -0.5])


def mainTrigger(p, u):
    return True if u[5] < 0 else False


Calisto.addParachute(name="Main", CdS=1, trigger=mainTrigger, samplingRate=100, lag=1.5)

# ## Simulating a Flight
#
# Simulating a flight trajectory is as simples as initializing a Flight class object givin the rocket and environement set up above as inputs. The launch rail inclination and heading are also given here.
TestFlight = Flight(
    rocket=Calisto,
    environment=Env,
    inclination=85,
    heading=0,
    maxTime=300 * 60,
    # minTimeStep=0.1,
    # maxTimeStep=10,
    rtol=1e-8,
    atol=1e-6,
    verbose=True,
    initialSolution=[
        0.0,
        0.0,
        0.0,
        1.5e3,
        10,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
    ],
)

TestFlight.info()
TestFlight.postProcess()
TestFlight.allInfo()

print("Done")
# ## Analysing the Results
#
# RocketPy gives you many plots, thats for sure! They are divided into sections to keep them organized. Alternatively, see the Flight class documentation to see how to get plots for specific variables only, instead of all of them at once.
# TestFlight.allInfo()
