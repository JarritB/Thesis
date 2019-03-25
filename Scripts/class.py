# -*- coding: utf-8 -*-
"""
Created on Tue Nov 13 12:23:05 2018

@author: Jarrit
"""

class Atom():
    def __init__(self,sym,xpos,ypos,zpos):
        self.sym = sym
        self.xpos = xpos
        self.ypos = ypos
        self.zpos = zpos
        
    def printout(self):
        print("symbol:{} x:{:6} y:{:6} z:{:6}".format(self.sym,self.xpos,self.ypos,self.zpos))
        
O1 = Atom('O',"0.123","0.123","0.123")
O1.printout()