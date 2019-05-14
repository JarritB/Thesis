# -------------------------------------------
# MODULES
# -------------------------------------------
import sys
import time
import os
import numpy as np
import subprocess
import math
from mathutils import Vector
from CifFile import CifFile
try:
    import bpy
    Blender_env = True
except:
    print("Not in blender environment.")

# -------------------------------------------
# VARIABLES
# -------------------------------------------

# global variables
file_path       =   "Select a file" # path to CIF-file
draw_bonds      =   False           # draws bonds between atoms
draw_style      =   "SPACE FILLING" # sets draw style
draw_quality    =   "MED"           # sets key for qualitydic
draw_lattice    =   False           # draws unit cell outline
bond_distance   =   2               # set the max distance between bound atoms
lattice_size    =   0.03            # sets size of lattice borders
bond_radius     =   0.05            # radius of bond
render_image	=	True			# render final image


# dictionaries
# sets detail of spheres
styledic   =    {
                        "SPACE FILLING"     :   [1,0],
                        "BALL AND STICK"    :   [0.5,0],
                        "STICK"             :   [0,1]
                }

# sets detail of spheres
qualitydic   =  {
                        "MIN"   :   8,
                        "LOW"   :   16,
                        "MED"   :   32,
                        "HIGH"  :   64,
                        "MAX"   :   128
                }

'''
Uncomment this when no external dictionaries are found
# dictionary which couples atoms to a color
colordic        =   {
                        "O"     :   [1,0,0],
                        "Si"    :   [0.25,0.25,1],
                        "Fe"    :   [1,0.2,0.2],
                    }

# dictionary which couples atoms to a specific size
sizedic         =   {
                        "O"     :   0.3,
                        "Si"    :   0.6,
                        "Fe"    :   1.4,
                    }
'''
# Read in dictionaries from external files



path = os.path.dirname(os.path.realpath(__file__))

# dictionary which couples atoms to a color
# Color scheme following the CPK convention was extracted from https://en.wikipedia.org/wiki/CPK_coloring#Typical_assignments
# data can be changed by modifying the values in colordic.txt
with open(path+'\\colordic.txt','r') as inf:
    colordic = eval(inf.read())

# dictionary which couples atoms to a specific size
# Atom data, in Ångström, was extracted from https://en.wikipedia.org/wiki/Atomic_radii_of_the_elements_(data_page)
# data can be changed by modifying the values in sizedic.txt
with open(path+'\\sizedic.txt','r') as inf:
    sizedic = eval(inf.read())


# ----------------------------------------------
# BLENDER ADD-ON
# ----------------------------------------------

# add-on info
bl_info = {
    "name": "Crystallographic Drawing Tool for Blender",
    "description": "Add-on for drawing crystals from CIF-files.",
    "author": "Jarrit Boons",
    "blender": (2, 80,0),
    "location": "View3D",
    "category": "Crystallography in Blender"
}


# Operator to open the file browser and select a file
class ScanFileOperator(bpy.types.Operator):

    bl_idname = "error.scan_file"
    bl_label = "Scan file for return"
    filepath = bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):

        global file_path
        file_path = self.filepath
        return {'FINISHED'}


    def invoke(self, context, event):

        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


    def register():

        bpy.types.Scene.path_to_file = bpy.props.StringProperty(
        name="",
        description="Path to CIF file",
        default = "empty"
        )

# Operator to hold CDTB-data and program execution
class Operator(bpy.types.Operator):

    bl_idname = "object.cdtb_operator"
    bl_label = "CDTB_operator"
    bl_descriptor = "Operator for drawing crystal"

    # Runs the whole program
    def execute(self, context):

        if(file_path == "Select a file"):
            print("No file selected")
        else:
            global draw_bonds
            draw_bonds = context.scene.draw_bonds

            global bond_distance
            bond_distance = context.scene.bond_distance

            global draw_lattice
            draw_lattice = context.scene.draw_lattice

            global print_data
            print_data = context.scene.print_data

            global draw_style
            draw_style = context.scene.style_selection_mode
            if(draw_style=="SPACE FILLING"):
                draw_bonds = False
            if(draw_style=="STICK"):
                draw_bonds = True

            global draw_quality
            draw_quality = context.scene.quality_selection_mode

            drawCrystal(file_path)

        return {'FINISHED'}


    @classmethod
    def register(cls):

        print("Registered class: %s " % cls.bl_label)
        bpy.types.Scene.draw_bonds = bpy.props.BoolProperty(
            name="Draw bonds",
            description="Draw bonds between elements"
        )

        bpy.types.Scene.bond_distance = bpy.props.FloatProperty(
            name="Bond distance",
            description="Set max distance for bonds to occur",
            default=2,
            min=0.0,
            max=10.0,
            precision=2
        )

        bpy.types.Scene.print_data = bpy.props.BoolProperty(
            name="Print data",
            description="Print crystal data in terminal"
        )

        bpy.types.Scene.draw_lattice = bpy.props.BoolProperty(
            name="Draw lattice",
            description="Draw unit cell outline"
        )

        # Dropdown menu for drawing style
        selection_style = [
            ("SPACE FILLING",   "SPACE FILLING",    "",     1),
            ("BALL AND STICK",  "BALL AND STICK",   "",     2),
            ("STICK",           "STICK",            "",     3),
        ]

        bpy.types.Scene.style_selection_mode = bpy.props.EnumProperty(
                items=selection_style,
                name="Style"
            )

        # Dropdown menu for drawing quality
        selection_qual = [
            ("MIN",     "MIN",      "",     1),
            ("LOW",     "LOW",      "",     2),
            ("MED",     "MED",      "",     3),
            ("HIGH",    "HIGH",     "",     4),
            ("MAX",     "MAX",      "",     5)
        ]

        bpy.types.Scene.quality_selection_mode = bpy.props.EnumProperty(
                items=selection_qual,
                name="Quality",
                default="MED"
            )


    @classmethod
    def unregister(cls):

        print("Unregistered class: %s " % cls.bl_label)

# Panel to display add-on in Blender environment
class Panel(bpy.types.Panel):

    bl_idname = "CDTB_Panel"
    bl_label = "CDTB_Panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_category = "CDTB"
    bl_ui_units_x = 50

    def draw(self,context):

        scn = context.scene
        layout = self.layout
        layout.ui_units_x = 15
        layout.label(text = 'Input file',icon_value=112)

        '''
        for i in range(100):
            layout.label(text = str(i),icon_value =i)
        '''

        box = layout.box()
        row = box.row()
        splitrow = row.split(factor=0.075)
        left_col = splitrow.column()
        right_col = splitrow.column()
        left_col.operator('error.scan_file',icon_value=108,text="")
        right_col.label(text=file_path.rsplit('\\', 2)[-1])
        layout.label(text = 'Settings',icon_value =117)
        box = layout.box()
        box.prop(scn,'draw_bonds')
        box.prop(scn,'bond_distance')
        box.prop(scn,'draw_lattice')
        box.prop(scn,'print_data')
        box.prop(scn, 'style_selection_mode')
        box.prop(scn, 'quality_selection_mode')
        layout.separator()
        splitrow = layout.split(factor=0.3)
        col = splitrow.column()
        col.operator('object.cdtb_operator',text="Draw Crystal")
        col = splitrow.column()
        layout.separator()


    @classmethod
    def register(cls):

        print("Registered class: %s " % cls.bl_label)


    @classmethod
    def unregister(cls):

        print("Unregistered class: %s " % cls.bl_label)


def register():

    bpy.utils.register_class(Operator)
    bpy.utils.register_class(ScanFileOperator)
    bpy.utils.register_class(Panel)


def unregister():

    bpy.utils.unregister_class(Operator)
    bpy.utils.unregister_class(Panel)
    bpy.utils.unregister_class(ScanFileOperator)


#----------------------------------------------
# MAIN PROGRAM
#----------------------------------------------


class Crysdata():

    def __init__(self,F,cb):

        self.start  =   time.time()
        self.name   =   F
        self.cell   =   Cell(cb)
        self.atoms  =   readEl(cb)
        self.pos    =   readPos(cb)
        c           =   self.cell
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


    def drawCrystal(self):

        if draw_lattice:
            self.drawCell()
            print("Lattice drawn after {:.3f} seconds".format((time.time()-self.start)))
        self.drawAtoms()
        print("Atoms drawn after {:.3f} seconds".format((time.time()-self.start)))
        if(draw_bonds):
            self.drawBonds()
            print("Bonds drawn after {:.3f} seconds".format((time.time()-self.start)))


    def drawAtoms(self):

        for a in self.atoms:
            a.drawObj(self.ftoc)
        print("Atoms drawn:",len(self.atoms))


    def drawCell(self):

        cell_corners=[]
        cell_edges=[]
        # calculate and draw corners
        for i in range(2):
            for j in range(2):
                for k in range(2):
                    bpy.ops.mesh.primitive_uv_sphere_add(size=lattice_size,location=toCarth(self.ftoc,[i,j,k]))
                    activeObject = bpy.context.active_object # Set active object to variable
                    cell_corners.append(activeObject)
                    mat = bpy.data.materials.new(name="MaterialName") # set new material to variable
                    activeObject.data.materials.append(mat) # add the material to the object
                    bpy.context.object.active_material.diffuse_color = [0,0,0] # change color
        # draw lines
        for i,j in zip([0,0,0,1,1,2,2,3,4,4,5,6],[1,2,4,3,5,3,6,7,5,6,7,7]):
            cell_edges.append(self.drawLine(cell_corners[i].location,cell_corners[j].location))
        # select all line and corners
        for i in cell_corners:
            i.select_set(action="SELECT")
        for i in cell_edges:
            i.select_set(action="SELECT")
        # set corner in origin as active and join meshes as one object
        bpy.context.view_layer.objects.active = cell_corners[0]
        bpy.ops.object.join()

        print("Cell box drawn")


    def drawLine(self,ac,tc):

        dx = tc[0] - ac[0]
        dy = tc[1] - ac[1]
        dz = tc[2] - ac[2]
        dist = np.sqrt(dx**2 + dy**2 + dz**2)
        bpy.ops.mesh.primitive_cylinder_add(vertices=qualitydic[draw_quality],radius=lattice_size,depth = dist,location = (dx/2 + ac[0], dy/2 + ac[1], dz/2 + ac[2]))
        activeObject = bpy.context.active_object
        mat = bpy.data.materials.new(name="MaterialName") # set new material to variable
        activeObject.data.materials.append(mat) # add the material to the object
        bpy.context.object.active_material.diffuse_color = [0,0,0] # change color

        phi = math.atan2(dy, dx)
        theta = math.acos(dz/dist)

        bpy.context.object.rotation_euler[1] = theta
        bpy.context.object.rotation_euler[2] = phi
        return activeObject


    def drawBonds(self):

        cnt = 0
        bpy.ops.curve.primitive_bezier_circle_add(location=(0,0,0),radius = bond_radius)
        bpy.context.object.name = 'bez'
        for atom in self.atoms:
            for target in self.atoms:
                if atom != target:
                    if("bond{}-{}".format(target.elid,atom.elid)in bpy.data.objects):
                        continue
                    if calcDistance(self.ftoc,atom,target) <= bond_distance:
                        self.makeBond(atom,target)
                        cnt += 1
        print("Atom bonds drawn:",cnt)


    # This function hooks the bond to the atoms
    def makeBond(self,atom,target):

        if 'OBJECT'!=bpy.context.mode:
            bpy.ops.object.mode_set(mode='OBJECT')
        o1 = bpy.data.objects[atom.elid]
        o2 = bpy.data.objects[target.elid]
        bond = self.hookCurve(o1,o2, bpy.context.scene)
        bpy.context.object.data.bevel_object = bpy.data.objects["bez"]
        bpy.context.object.name = "bond{}-{}".format(atom.elid,target.elid)
        activeObject = bpy.context.active_object # Set active object to variable
        mat = bpy.data.materials.new(name="MaterialName") # set new material to variable
        activeObject.data.materials.append(mat) # add the material to the object
        bpy.context.object.active_material.diffuse_color = [255,255,255] # change color
        if 'OBJECT'!=bpy.context.mode:
            bpy.ops.object.mode_set(mode='OBJECT')


    def hookCurve(self,o1, o2, scn):

        curve = bpy.data.curves.new("link", 'CURVE')
        curve.dimensions = '3D'
        spline = curve.splines.new('BEZIER')

        spline.bezier_points.add(1)
        p0 = spline.bezier_points[0]
        p1 = spline.bezier_points[1]
        # p0.co = o1.location
        p0.handle_right_type = 'VECTOR'
        # p1.co = o2.location
        p1.handle_left_type = 'VECTOR'


        obj = bpy.data.objects.new("link", curve)
        m0 = obj.modifiers.new("alpha", 'HOOK')
        m0.object = o1
        m1 = obj.modifiers.new("beta", 'HOOK')
        m1.object = o2

        bpy.context.collection.objects.link(obj)
        bpy.context.view_layer.objects.active = obj

        bpy.ops.object.mode_set(mode='EDIT')

        # Reassign the points
        p0 = curve.splines[0].bezier_points[0]
        p1 = curve.splines[0].bezier_points[1]

        # Hook first control point to first atom
        p0.select_control_point = True
        p1.select_control_point = False
        bpy.ops.object.hook_assign(modifier="alpha")

        # Hook second control point to first atom
        p0 = curve.splines[0].bezier_points[0]
        p1 = curve.splines[0].bezier_points[1]
        p1.select_control_point = True
        p0.select_control_point = False
        bpy.ops.object.hook_assign(modifier="beta")

        return obj


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
        size = sizedic[self.sym]*styledic[draw_style][0]+bond_radius*styledic[draw_style][1]
        bpy.ops.mesh.primitive_uv_sphere_add(segments=qualitydic[draw_quality],ring_count=qualitydic[draw_quality]/2,size=size,location=toCarth(ftoc,[self.xpos,self.ypos,self.zpos]))
        bpy.context.object.name = self.elid
        activeObject = bpy.context.active_object # Set active object to variable
        mat = bpy.data.materials.new(name="MaterialName") # set new material to variable
        activeObject.data.materials.append(mat) # add the material to the object
        bpy.context.object.active_material.diffuse_color = colordic[self.sym] # change color


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

    # Convert symmetry to P1 using openbabel as subprocess
    # Notation: obabel [-i<input-type>] <infilename> [-o<output-type>] -O<outfilename> [Options]
    subprocess.run(['obabel', '-icif', cif_file, '-ocif', '-O', p1_file, '--fillUC', 'strict'])


def calcDistance(ftoc,atom1,atom2):

    ac = toCarth(ftoc,[atom1.xpos,atom1.ypos,atom1.zpos])
    tc = toCarth(ftoc,[atom2.xpos,atom2.ypos,atom2.zpos])
    dx = tc[0] - ac[0]
    dy = tc[1] - ac[1]
    dz = tc[2] - ac[2]
    dist = np.sqrt(dx**2 + dy**2 + dz**2)
    return dist


def toCarth(ftoc,V_frac):

    return np.dot(ftoc, V_frac)

def look_at(obj_camera, point):
    loc_camera = obj_camera.matrix_world.to_translation()
    direction = point - loc_camera
    # point the cameras '-Z' and use its 'Y' as up
    rot_quat = direction.to_track_quat('-Z', 'Y')
    # assume we're using euler rotation
    obj_camera.rotation_euler = rot_quat.to_euler()

def renderImage(x,y,z):

    bpy.ops.object.camera_add(view_align=True, enter_editmode=False, location=(5*x,5*y,5*z))
    print("camera added")
    bpy.ops.object.light_add(type='SUN', view_align=False, location=(0, 0, 0))
    obj_camera = bpy.data.objects["Camera"]
    look_at(obj_camera, Vector([0,0,z/4]))
    obj_camera.data.type = 'ORTHO'
    obj_camera.data.ortho_scale = ((x+y+z))





def clearWS():

    if 'OBJECT'!=bpy.context.mode:
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    # remove all previouscurves
    for i in bpy.data.curves:
        bpy.data.curves.remove(i)
    print("Workspace cleared.")
    return

def drawCrystal(file):
    # Check OpenBabel installation
    try:
        # Convert the cif file to its P1 symmetry notation as a temporary cif file
        print('Converting %s to P1' %file)
        obabel_fill_unit_cell(file, "temp.CIF")
    except:
        print("No OpenBabel installation found, install it from http://openbabel.org/wiki/Category:Installation")
    # Open and parse our cif
    cf = CifFile("temp.CIF")
    f = file.rsplit('\\', 1)[-1]
    F = f[:3]
    print(f)
    cb = cf["I"]
    Crystal = Crysdata(F,cb)

    # Print crystal data in terminal if checked
    if(print_data):
        Crystal.printout()

    # Draw crystal if in Blender environment
    if(Blender_env):
        clearWS()
        Crystal.drawCrystal()
        bpy.ops.object.select_all(action='DESELECT')
        if(render_image):
            renderImage(Crystal.cell.alen,Crystal.cell.blen,Crystal.cell.clen)
