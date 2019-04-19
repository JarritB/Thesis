
# MODULES
# -------------------------------------------
import sys
import numpy as np
from CifFile import CifFile
import bpy,bgl
# -------------------------------------------

# VARIABLES
# -------------------------------------------

#global variables

#dictionary which couples atoms to a color
colordic =  {
                "O" : [1,0,0] , 
                "Si" : [0.25,0.25,1]
            }
#dictionary which couples atoms to a specific size
sizedic =   {
                "O" : 0.5 ,    
                "Si" : 1
            }
            
# -------------------------------------------

class Crysdata():
    
    def __init__(self,F,cb):
        self.name   =   F
        self.cell   =   Cell(cb)
        self.atoms  =   readEl(cb) 
        self.pos    =   readPos(cb)  
        c = self.cell               
        self.ftoc   =   self.get_fractional_to_cartesian_matrix(c.alen,c.blen,c.clen,c.alpha,c.beta,c.gamma)
    
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
        print()
        print("Fractional to cartesian matrix:")
        print(self.ftoc)
            
    def get_fractional_to_cartesian_matrix(self,a, b, c, alpha, beta, gamma):
        
        """
        Original code found at: https://gist.github.com/Bismarrck/a68da01f19b39320f78a
        
        !changed formula to resemble one found on: https://en.wikipedia.org/wiki/Fractional_coordinates
        
        Return the transformation matrix that converts fractional coordinates to
        cartesian coordinates.
        Parameters
        ----------
        a, b, c : float
        The lengths of the edges.
        alpha, gamma, beta : float
        The angles between the sides.
        angle_in_degrees : bool
        True if alpha, beta and gamma are expressed in degrees.
        Returns
        -------
        r : array_like
        The 3x3 rotation matrix. ``V_cart = np.dot(r, V_frac)``.
        """
    
        alpha = np.deg2rad(alpha)
        beta = np.deg2rad(beta)
        gamma = np.deg2rad(gamma)
        cosa = np.cos(alpha)
        sina = np.sin(alpha)
        cosb = np.cos(beta)
        sinb = np.sin(beta)
        cosg = np.cos(gamma)
        sing = np.sin(gamma)
        volume = 1.0 - cosa**2.0 - cosb**2.0 - cosg**2.0 + 2.0 * cosa * cosb * cosg
        volume = a*b*c*np.sqrt(volume)
        r = np.zeros((3, 3))
        r[0, 0] = float(a)
        r[0, 1] = float(b * cosg)
        r[0, 2] = float(c * cosb)
        r[1, 0] = float(0)
        r[1, 1] = float(b * sing)
        r[1, 2] = float(c * (cosa - cosb * cosg) / sing)
        r[2, 0] = float(0)
        r[2, 1] = float(0)
        r[2, 2] = float(volume / (a*b*sing))
        return r
    
    def drawAtoms(self):
        for a in self.atoms:
            a.drawObj(self.ftoc)
            
    def drawCell(self):
        for i in range(2):
            for j in range(2):
                for k in range(2):                
                    bpy.ops.mesh.primitive_cube_add(radius=.3,location=toCarth(self.ftoc,[i,j,k])) 
                    activeObject = bpy.context.active_object #Set active object to variable
                    mat = bpy.data.materials.new(name="MaterialName") #set new material to variable
                    activeObject.data.materials.append(mat) #add the material to the object
                    bpy.context.object.active_material.diffuse_color = [0,0,0] #change color
    

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
    
    def drawObj(self,ftoc):
        bpy.ops.mesh.primitive_ico_sphere_add(size=sizedic[self.sym],location=toCarth(ftoc,[self.xpos,self.ypos,self.zpos]))
        bpy.context.object.name = self.elid
        activeObject = bpy.context.active_object #Set active object to variable
        mat = bpy.data.materials.new(name="MaterialName") #set new material to variable
        activeObject.data.materials.append(mat) #add the material to the object
        bpy.context.object.active_material.diffuse_color = colordic[self.sym] #change color
        
    
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

def toCarth(ftoc,V_frac):
    return np.dot(ftoc, V_frac)
    
      
    
def clearWS():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    print("Workspace cleared.")
    return    


    
def main():
    #read filename
    f = "..\\Scripts\\CHA.cif" #input("Filename: ")
    # open and parse our cif
    cf = CifFile(f)
    f = f.rsplit('\\', 1)[-1]
    F = f[:3]
    print(f)
    cb = cf[F]
    Crystal = Crysdata(F,cb)
    #Crystal.printout();
    #print(Crystal.ftoc)
    #print(V_cart)    
    clearWS()
    Crystal.drawCell()
    Crystal.drawAtoms()
    bpy.ops.object.select_all(action='DESELECT')
    
        
    
main()