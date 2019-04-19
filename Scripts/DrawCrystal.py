
# MODULES
# -------------------------------------------
import sys
import numpy as np
import subprocess
from CifFile import CifFile
#import bpy,bgl
import math
# -------------------------------------------

# VARIABLES
# -------------------------------------------

#global variables
drawbonds = True        #draws bonds between atoms
atom_counter = 0        #counts the number of atoms drawn
bond_distance = 0.161       #set the max distance between bound atoms
bond_radius = 0.1       #radius of bond
#dictionary which couples atoms to a color
colordic =  {
                "O" : [1,0,0] ,
                "Si" : [0.25,0.25,1]
            }
#dictionary which couples atoms to a specific size
sizedic =   {
                "O" : 0.3 ,
                "Si" : 0.6
            }

# -------------------------------------------



class Crysdata():

    def __init__(self,F,cb):
        self.name   =   F
        self.cell   =   Cell(cb)
        self.atoms  =   readEl(cb)
        #self.pos    =   readPos(cb)
        c = self.cell
        self.ftoc   =   self.get_fractional_to_cartesian_matrix(c.alen,c.blen,c.clen,c.alpha,c.beta,c.gamma)

    def printout(self):
        print(self.name)
        print()
        self.cell.printout()
        print()
        #for element in self.pos:
            #element.printout()
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

    def drawCrystal(self):
        self.drawCell()
        self.drawAtoms()
        if(drawbonds):
            self.drawBonds()

    def drawAtoms(self):
        for a in self.atoms:
            a.drawObj(self.ftoc)
        print("Atoms drawn:",len(self.atoms))

    def drawCell(self):
        for i in range(2):
            for j in range(2):
                for k in range(2):
                    bpy.ops.mesh.primitive_cube_add(radius=.3,location=toCarth(self.ftoc,[i,j,k]))
                    activeObject = bpy.context.active_object #Set active object to variable
                    mat = bpy.data.materials.new(name="MaterialName") #set new material to variable
                    activeObject.data.materials.append(mat) #add the material to the object
                    bpy.context.object.active_material.diffuse_color = [0,0,0] #change color
        print("Cell corners drawn")

    def drawBonds(self):
        cnt = 0
        for atom in self.atoms:
            for target in self.atoms:
                if atom != target:
                    if calcDistance(atom,target) <= bond_distance:
                        self.makeBond(atom,target)
                        cnt += 1
        print("Atom bonds drawn:",cnt)

    #This function creates a bond between the positions of the atoms, however the objects will not be attached to the bond
    
    def makeBond(self,atom,target):
        ac = toCarth(self.ftoc,[atom.xpos,atom.ypos,atom.zpos])
        tc = toCarth(self.ftoc,[target.xpos,target.ypos,target.zpos])
        dx = tc[0] - ac[0]
        dy = tc[1] - ac[1]
        dz = tc[2] - ac[2]
        dist = np.sqrt(dx**2 + dy**2 + dz**2)
        bpy.ops.mesh.primitive_cylinder_add(radius=bond_radius,depth = dist,location = (dx/2 + ac[0], dy/2 + ac[1], dz/2 + ac[2]))

        phi = math.atan2(dy, dx)
        theta = math.acos(dz/dist)

        bpy.context.object.rotation_euler[1] = theta
        bpy.context.object.rotation_euler[2] = phi

    """
    #function in which the bond is attached to atom
    def makeBond(self,atom,target):
        
        bpy.ops.curve.primitive_bezier_circle_add(location=(0,0,0))
        bpy.ops.transform.resize(value=(0.25, 0.25, 0.25))
        bpy.context.object.name = "BevelCircle"
        
        curve = bpy.data.curves.new("lnk2", 'CURVE')
        spline = curve.splines.new('BEZIER')
        curve.dimensions="3D"
        curve.use_stretch = True
        curve.use_deform_bounds = True
        curve.use_radius = True

    	spline.bezier_points.add(1)
        cen = spline.bezier_points[0]
        p1 = spline.bezier_points[1]
        cen.co = [atom.xpos,atom.ypos,atom.zpos]
        cen.handle_left_type = 'VECTOR'    
        cen.handle_right_type = 'VECTOR'
        p1.co = [target.xpos,target.ypos,target.zpos]
        p1.handle_right_type = 'VECTOR'
        p1.handle_left_type = 'VECTOR'
        
        obj = bpy.data.objects.new("lnk2", curve)
        
        #select objects and active        
        bpy.ops.object.select_all(action='DESELECT')
        py.data.objects[atom.elid].select_set('SELECT')
        py.data.objects[target.elid].select_set('SELECT')
        bpy.context.view_layer.objects.active = bpy.data.objects["1"]
        
        bpy.ops.object.hook_add_selob(use_bone=False)
        bpy.context.object.data.bevel_object = bpy.data.objects["BezierCircle"]
        

    """



class Cell():

    def __init__(self,cb):
        self.alen   =   float(cb["_cell_length_a"])
        self.blen   =   float(cb["_cell_length_b"])
        self.clen   =   float(cb["_cell_length_c"])
        self.alpha  =   float(cb["_cell_angle_alpha"])
        self.beta   =   float(cb["_cell_angle_beta"])
        self.gamma  =   float(cb["_cell_angle_gamma"])


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
    elements = []
    previd = []
    idcnt = []
    lb = cb.GetLoop("_atom_site_label")
    for el in lb:
        flag = False
        for i in range(len(previd)):
            if(el[0] == previd[i]):
                flag = True
                break
        if(flag):         
            idcnt[i] += 1                
        else:
            previd.append(el[0])
            idcnt.append(0)
            i = len(idcnt)-1
        id_t = "{}.{}".format(el[0],idcnt[i])
        elements.append(Atom(id_t,el[1],el[2],el[3],el[4]))
            
    return elements

def readPos(cb):
    positions = [];
    lb = cb.GetLoop("_symmetry_equiv_pos_as_xyz")
    for el in lb:
        positions.append(sympos(el))
    return positions


def obabel_fill_unit_cell(cif_file, p1_file):

    #Convert symmetry to P1 using openbabel as subprocess
    #Notation: obabel [-i<input-type>] <infilename> [-o<output-type>] -O<outfilename> [Options]

    subprocess.run(['obabel', '-icif', cif_file, '-ocif', '-O', p1_file, '--fillUC', 'strict'])

def calcDistance(atom1,atom2):
    return np.sqrt((atom1.xpos-atom2.xpos)**2 + (atom1.ypos-atom2.ypos)**2 + (atom1.zpos-atom2.zpos)**2)



def toCarth(ftoc,V_frac):
    return np.dot(ftoc, V_frac)



def clearWS():
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    print("Workspace cleared.")
    return



def main():
    #read filename
    f = "..\\Scripts\\CHA.cif" #input("Filename: ")
    #convert the cif file to its P1 symmetry notation as a temporary cif file
    print('Converting %s to P1' %f)
    obabel_fill_unit_cell(f, "temp.CIF")
    # open and parse our cif
    cf = CifFile("temp.CIF")
    f = f.rsplit('\\', 1)[-1]
    F = f[:3]
    print(f)
    cb = cf["I"]#cf[F]
    Crystal = Crysdata(F,cb)
    Crystal.printout();
    #print(Crystal.ftoc)
    #print(V_cart)

    """
    Comment this part out when running outside of the Blender environment
    --->
    ""
    clearWS()
    Crystal.drawCrystal()
    bpy.ops.object.select_all(action='DESELECT')

    ""
    <----
    """

main()
