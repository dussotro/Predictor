from  particule import Particule
import roblib
import time
import numpy as np
import sys
import matplotlib.pyplot as plt
from PyUnityVibes.UnityFigure import UnityFigure


class mission:
	def __init__(self, num):
		self.figure = UnityFigure(UnityFigure.FIGURE_3D, UnityFigure.SCENE_EMPTY)
		time.sleep(1)
		self.tfinal = 60
		self.listParticules = [Particule(np.array([[0.0],[0.0],[0.0]]), np.array([[1.0],[0.0]]), np.diag((10**-9,10**-9,10**-9)), self.figure , self.tfinal) for i in range(num)]
		self.t = 0
		self.dt = 0.1
		
		self.num = num
		self.traj_part0 = []
		self.traj_part5 = []
		self.anim = self.figure.createAnimation(self.dt)
		time.sleep(1)
	
		print("Ajout des objets à l'animation")
		for part in self.listParticules:
			self.anim.addObject(part.auv)
			time.sleep(1)

	def __repr__(self):
		return "Programme de la mission: \n Aller en ligne droite, retour a 60s\n Nombre de particules {}".format(self.num)

	def display(self):
		print("Affichage de la mission sur PyUnityVibes")
		self.figure.animate(self.anim)

	def afficher_ellipse_all(self, ax, col=[0.9,0,0]):
     
		global max_x, max_y, min_y, min_x #pour regler la fenetre de l'affichage
		all_Xchap = [p.Xchap[0,0] for p in self.listParticules]
		all_Ychap = [p.Xchap[1,0] for p in self.listParticules] 
  
		if min(all_Xchap) < min_x or min_x == None:
			min_x = min(all_Xchap)    

		if min(all_Ychap) < min_y or min_y == None:
			min_y = min(all_Ychap)  

		if max(all_Xchap) > max_x or max_x == None:
			max_x = max(all_Xchap)  

		if max(all_Ychap) > max_y or max_y == None:
			max_y = max(all_Ychap)    

		
		ax.set_xlim(min_x-30, max_x+30)
		ax.set_ylim(min_y-30, max_y+30)
		for p in self.listParticules:
			p.afficher_ellipse(ax,col)

	def recalage(self):
		for part in self.listParticules:
			
			x_gps = part.X[0,0] + part.noise(0.48**2)
			y_gps = part.X[1,0] + part.noise(0.48**2)
			"""
			part.Xchap[0,0] = x_gps
			part.Xchap[1,0] = y_gps

			part.cov = np.diag([0.48**2, 0.48**2, part.cov[2,2]])
			"""
			L = x_gps
			h = y_gps
			
			desired_angle = -(np.arctan2(h,L) + np.pi)
			part.U[1,0] = desired_angle

	def aller_retour(self):

		global max_x, max_y, min_y, min_x   #pour regler la fenetre de l'affichage     
		max_x, max_y, min_y, min_x = self.listParticules[0].Xchap[0,0], self.listParticules[0].Xchap[1,0], self.listParticules[0].Xchap[1,0], self.listParticules[0].Xchap[0,0]        
        
		fig_ellipse = plt.figure() 
		ax = fig_ellipse.add_subplot(111, aspect='equal')

		for part in self.listParticules:
			part.theta = np.arctan2(0.0001, 50)

		while self.t < self.tfinal :
			#print("[{:.2f},{:.2f},{:.2f}]".format(self.listParticules[0].X[0,0], self.listParticules[0].X[1,0], self.listParticules[0].X[2,0]))
			sys.stdout.write("Aller  : t = %f \r" % self.t)
			for part in self.listParticules: 
				part.step(self.t, self.dt)
				part.appendFrame(self.anim)
			self.listParticules[0].afficher_ellipse(ax, "r")
			#self.traj_part0.append(self.listParticules[0].X[0:2])
			#self.traj_part5.append(self.listParticules[5].X[0:2])
			self.t  += self.dt

		""" Affichage """

		self.afficher_ellipse_all(ax, "red")

		self.recalage()

		fig_ellipse = plt.figure() 
		ax_ret = fig_ellipse.add_subplot(111, aspect='equal')

		while self.t < 2*self.tfinal+20:
			sys.stdout.write("Retour : t = %f \r" % self.t)
			for part in self.listParticules: 
				part.step(self.t, self.dt)
				part.appendFrame(self.anim)
			self.listParticules[0].afficher_ellipse(ax_ret, "r")
			#self.traj_part0.append(self.listParticules[0].X[0:2])
			#self.traj_part5.append(self.listParticules[5].X[0:2])
			self.t  += self.dt

		""" Affichage """
		self.afficher_ellipse_all(ax_ret, "green")
		
		
		#xplot_0 = [self.traj_part0[i][0] for i in range(len(self.traj_part0))]
		#yplot_0 = [self.traj_part0[i][1] for i in range(len(self.traj_part0))]
		#xplot_5 = [self.traj_part5[i][0] for i in range(len(self.traj_part5))]
		#yplot_5 = [self.traj_part5[i][1] for i in range(len(self.traj_part5))]
		
		part_pos_x = []
		part_pos_y = []
		for part in self.listParticules:
			part_pos_x.append(part.X[0,0])
			part_pos_y.append(part.X[1,0])

		#plt.plot(xplot_0, yplot_0, 'bo', markersize='0.5', )
		#plt.plot(xplot_5, yplot_5, 'bo', markersize='0.5')
		plt.plot(part_pos_x, part_pos_y, '+b')

		plt.xlabel("coordonnee x en metres")
		plt.ylabel("coordonnee y en metres")
		plt.title("Ellipses d'incertitude en position pour les differents\n auv apres trajet aller puis apres trajet retour")  
		plt.show()

		print("\n Done ! ")
		time.sleep(1)
		self.display()



	def run(self):
		while self.t < self.tfinal :	
			sys.stdout.write("t = %f \r" % self.t)
			for part in self.listParticules: 
				part.step(self.t, self.dt)
				part.appendFrame(self.anim)
			self.t  += self.dt

		print("\n Done ! ")
		time.sleep(1)
		self.display()

if __name__=='__main__':
	N = 2
	mission = mission(N)
	mission.aller_retour()