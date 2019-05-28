#
# An example of how to output a subset of looped items.
#

import sys
from CifFile import CifFile
#import bpy
#import mathutils

class Crysdata():
    
    def __init__(self,F,cb):
        self.name   =   F
        self.cell   =   Cell(cb)
        self.atoms  =   readEl(cb) 
        self.pos    =   readPos(cb)  
    
    def printout(self):
        print(self.name)
        print()
        self.cell.printout()
        print()
        for element in self.pos:    
            element.printout()
        print()
        for element in self.atoms:
            element.printout()
    

class Cell():
    
    def __init__(self,cb):
        self.alen   =   float(cb["_cell_length_a"].strip("(0)"))
        self.blen   =   float(cb["_cell_length_b"].strip("(0)"))
        self.clen   =   float(cb["_cell_length_c"].strip("(0)"))
        self.alpha  =   float(cb["_cell_angle_alpha"].strip("(0)"))
        self.beta   =   float(cb["_cell_angle_beta"].strip("(0)"))
        self.gamma  =   float(cb["_cell_angle_gamma"].strip("(0)"))
        
        
    def printout(self):
        print("alen:{:8} \nblen:{:8} \nclen:{:8} \nalpha:{:8} \nbeta: {:8} \ngamma:{:8}".format(self.alen,self.blen,self.clen,self.alpha,self.beta,self.gamma))
    
    
class Atom():
    def __init__(self,elid,sym,xpos,ypos,zpos):
        self.elid   =   elid
        self.sym    =   sym
        self.xpos   =   float(xpos)
        self.ypos   =   float(ypos)
        self.zpos   =   float(zpos)
        
    def printout(self):
        print("id:{:3} symbol:{:2} x:{:.4f} y:{:.4f} z:{:.4f}".format(self.elid,self.sym,self.xpos,self.ypos,self.zpos))
    
class sympos():
    def __init__(self,string):
        self.xsym = (string[0].split(','))[0]
        self.ysym = (string[0].split(','))[1]
        self.zsym = (string[0].split(','))[2]
        
    def printout(self):
        print("x:{:8} y:{:8} z:{:8}".format(self.xsym,self.ysym,self.zsym))


def readEl(cb):    
    elements = [];
    lb = cb.GetLoop("_atom_site_label")
    for el in lb:
        elements.append(Atom(el[0],el[1],el[2],el[3],el[4]))
    return elements

def readPos(cb):    
    positions = [];
    lb = cb.GetLoop("_symmetry_equiv_pos_as_xyz")
    for el in lb:
        positions.append(sympos(el))
    return positions

    
def main():
    #read filename
    f = 'CHA.cif'#input("Filename: ")
    # open and parse our cif
    cf = CifFile(f)
    F = f[:3]
    cb = cf[F]
    Crystal = Crysdata(F,cb)
    Crystal.printout();
    
main()