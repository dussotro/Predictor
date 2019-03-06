# -*- coding: utf-8 -*-
"""
Created on Tue Apr 17 19:13:33 2018
@author: alexandre
"""

from roblib import *
import time
import math
from PyUnityVibes.UnityFigure import UnityFigure

def kalman_predict(xup,Gup,u,Γα,A):
    Γ1 = A @ Gup @ A.T + Γα
    x1 = A @ xup + u 
    return(x1,Γ1)    

def kalman_correc(x0,Γ0,y,Γβ,C):
    S = C @ Γ0 @ C.T + Γβ 
    if det(S) != 0 :
        K = Γ0 @ C.T @ inv(S)
    else : 
        K = zeros((3,2))
    ytilde = y - C @ x0        
    Gup = (eye(len(x0))-K @ C) @ Γ0 
    xup = x0+ K@ytilde    
    return(xup,Gup) 
    
def kalman(x0,Γ0,u,y,Γα,Γβ,A,C):
    xup,Gup = kalman_correc(x0,Γ0,y,Γβ,C)
    x1,Γ1=kalman_predict(xup,Gup,u,Γα,A)
    return(x1,Γ1)

############################################
class Particule:
    """
    Particule class
    """
    def __init__(self,X,U,cov, figure, tf):
        """
        Constructor
        Parameters
        ----------
        X: state vector
            X[0]:x coordinate
            X[1]:y coordinate
            X[2]:v speed
        U: input vector
            U[0]:u speed input
            U[1]:theta heading input
        cov: matrix 3*3
            covariance matrix
        """

        self.Xchap = X
        self.X = X
        self.U = U
        self.cov = cov
        self.theta = 0
        self.omega_max = math.radians(10)
        self.tfinal = tf
        self.auv = figure.create(UnityFigure.OBJECT_3D_SUBMARINE, 0, 0, 0, dimX=5, dimY=5, dimZ=5, color=UnityFigure.COLOR_YELLOW)
        self.auv.updateRotation(0,math.degrees(self.U[1,0]),0)
        time.sleep(0.1)


    def __str__(self):
        """
        Allows to print the Particule object
        """
        X = self.X.flatten()
        U = self.U.flatten()
        return 'X: \n x coordinate > {}\n y coordinate > {}\n speed > {}\n\n U: \n speed input > {}\n theta heading input > {}\n\n cov:\n {}'.format(self.X[0], self.X[1], self.X[2], self.U[0], self.U[1], self.cov)

    def __repr__(self):
        X = self.X.flatten()
        U = self.U.flatten()
        return "Vecteur etat : [{},{},{}]".format(self.X[0],self.X[1],self.X[2]) + "\n Matrice de covariance : {}".format(self.cov) + "\n Vecteur d'entree : [{},{}]".format(self.U[0],self.U[1])  # {:.2f} notation pour n'afficher que deux chiffres après la virgule

    def noise(self, variance):
        return np.random.normal(0,variance**2)

    def sign(self, a):
        """
        Return the sign of a
        """
        if a > 0:
            return 1
        else:
            return -1

    def display(self,col):
        """
        Allows to display the Particule object through matplotlib
        """
        X = self.X.flatten()
        U = self.U.flatten()
        draw_arrow(X[0],X[1],U[1],0.1,col)

    def appendFrame(self,anim): #PyUnityVibes
        #print("U : ", math.degrees(self.U[1,0]), "th: ", math.degrees(self.theta))
        anim.appendFrame(self.auv, x=self.X[1,0], y=0.0, z=self.X[0,0], rx=0, ry=math.degrees(self.theta), rz=0)

    def controle(self,t,dt):
        """
        Control equation of the AUV
        """  
        if t>self.tfinal:
            self.U[1,0] = arctan2(self.Xchap[1,0], self.Xchap[0,0]) + np.pi
        self.theta += dt*self.sign(self.U[1,0] - self.theta)*min(self.omega_max, abs(self.U[1,0] - self.theta))


    def f(self):
        """
        State equation of the AUV
        alpha : bruit gaussien sur x,y et v
        """

        sigma_x, sigma_y,sigma_v = 0.1,0.1,0.15
        G_alpha = np.diag([sigma_x**2,sigma_y**2,sigma_v**2])

        alpha = np.zeros((3,1))
        alpha[0,0] = np.random.normal(0,sigma_x)
        alpha[1,0] = np.random.normal(0,sigma_y)
        alpha[2,0] = np.random.normal(0,sigma_v)

        A  = array([[0,0,cos(self.theta)],[0,0,sin(self.theta)],[0,0,-1]])
        return A.dot(self.X) + array([[0],[0],[self.U[0,0]]]) + alpha


    def step(self,t,dt):
        """
        Allows to apply the evolution model between t and t+dt
        """
        if (self.tfinal - 0.01 < t < self.tfinal + 0.01):
            C      = array([[1,0,0],[0,1,0]])
            G_beta = diag([[0.48**2],[0.48**2]])
        else :
            C      = zeros((2,3))
            G_beta = zeros((2,2))
        
        sigma_x, sigma_y,sigma_v = 0.1,0.1,0.15
        G_alpha = np.diag([sigma_x**2,sigma_y**2,sigma_v**2])

        self.X = self.X + dt*self.f()

        U = self.U.flatten()
        
        A  = array([[1,0,cos(self.theta)],
                    [0,1,sin(self.theta)],
                    [0,0,-1]])

        self.Xchap,self.cov = kalman(self.X,self.cov,array([[0],[0],[U[0]]]),G_beta ,G_alpha,G_beta,A,C)
        self.controle(t, dt)

    def afficher_ellipse(self,ax,col):
        #draw_ellipse(c,Γ,η,ax,col): # Gaussian confidence ellipse with artist
        #draw_ellipse(array([[1],[2]]),eye(2),0.9,ax,[1,0.8-0.3*i,0.8-0.3*i])
        draw_ellipse(self.Xchap[0:2,0],self.cov[0:2, 0:2],0.99,col)


def afficher_ellipse_all(tab_part,col):
    
    """
    tab_part: tableau contenant les toutes particules
    col : couleurs [R G B]
    """    
    all_Xchap = [p.Xchap[0,0] for p in tab_part]
    all_Ychap = [p.Xchap[1,0] for p in tab_part]    
    fig = plt.figure(0)
    ax = fig.add_subplot(111, aspect='equal')
    ax.set_xlim(min(all_Xchap)-30, max(all_Xchap)+30)
    ax.set_ylim(min(all_Ychap)-30, max(all_Ychap)+30)
    for p in tab_part:
        p.afficher_ellipse(ax,col)




if __name__ == "__main__":

    fig1 = figure()
    X = array([[1],[10],[2]])
    Xchap = X
    U = array([[3],[pi/4]])
    cov = eye(3)
    theta = 0
    part = Particule(X,U,cov,fig1)
    print(part)
    part2 = part
    part2.step(10,0.1)
    print(part2)
    part2.display("red")
    part2.step(12,0.1)
    part2.display("green")
    
    part3 = Particule(2*X,U,10*cov,fig1)    
    part4 = Particule(array([[-7],[12],[3]]),U,cov,fig1) 
    tab_part = [part,part2,part3,part4] 
    part2.step(12,0.1)
    afficher_ellipse_all(tab_part,[0.9,0,0])