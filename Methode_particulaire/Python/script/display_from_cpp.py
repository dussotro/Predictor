import time
import sys

import numpy as np

from PyUnityVibes.UnityFigure import UnityFigure

### Constante ###
N  = 30
dt = 0.1

if len(sys.argv) < 2:
	print("Merci de rentrer le chemin d'accès au fichier à traiter")
	sys.exit(1)
else:
	filename = sys.argv[1]

file = open(filename, "r")
heading = file.readline()
data = file.readlines()


N, T, dt = heading.split(";")
N = int(N[2:])    # on lit "N=100"
T = int(T[2:])    # ------ "T=1200"
dt= float(dt[3:]) # ------ "dt=0.1"

parts = np.zeros((N, int(T/dt), 6))

for line in data:
	data_line = line.split(";")
	ID, t, x, y, z, rx, ry, rz = [float(el) for el in data_line]
	#print(ID, t, x, y, z)
	ID = int(ID)
	#print(int(t/dt)-1)
	parts[ID, int(t/dt)-1] = x, y, z, rx, ry , rz

#print(parts[0])

### Initialisation de Unity ###
figure = UnityFigure(UnityFigure.FIGURE_3D, UnityFigure.SCENE_EMPTY)
time.sleep(1)
anim = figure.createAnimation(dt)
time.sleep(1)


### Creation des AUVs ###
AUVs = []
for ind_auv in range(N):
	AUVs.append(figure.create(UnityFigure.OBJECT_3D_SUBMARINE, 0, -0.4, 0, dimX=1, dimY=1, dimZ=5, color=UnityFigure.COLOR_YELLOW))
	anim.addObject(AUVs[ind_auv])
	time.sleep(0.1)

for coord in [[0,0],[50,0],[25,25]]:
			boue = figure.create(UnityFigure.OBJECT_3D_CUBE, -coord[1], -2, coord[0], dimX=0.2, dimY=5, dimZ=0.2, color=UnityFigure.COLOR_RED)
			anim.addObject(boue)
			time.sleep(0.5)

time.sleep(1)

### Calcul des frames successives ###
for k in range(int(T/dt)):
	sys.stdout.write("t = {} s \r".format(t))
	for ind_auv, auv in enumerate(AUVs):
		x_p, y_p, z_p, rx_p, ry_p, rz_p = parts[ind_auv, k]
		#print(x_p, y_p, z_p, rx_p, ry_p, rz_p)
		anim.appendFrame(auv, x=-y_p, y=-z_p, z=x_p, rx=rx_p, ry=-rz_p, rz=ry_p)
print("")
time.sleep(1)


### Display ###
figure.animate(anim)

sys.exit(0)
