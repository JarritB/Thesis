import bpy
import math
import bmesh
import mathutils
from mathutils import Vector

atomlist=[] 
au=[]
curat=[]
bondlist=[]
curbnd=['at1','at2']
maxdis=3.8
au0=[["org",0,(0,0,0)],
["T1",14,(3.1052,0.6475,-2.4592)],
["T2",14,(-1.6316,0.6332,-2.1574)],
["T3",14,(2.3505,-2.0685,-1.8182)],
["T4",14,(-0.6988,-2.1524,-1.4776)],
["T5",14,(0.881,2.4346,-1.5586)],
["T6",14,(-3.4453,2.8029,-0.7418)],
["T7",14,(1.5878,0.6104,-5.2199)],
["T8",14,(-1.6003,0.577,-5.1752)],
["T9",14,(3.6818,-3.9323,-3.8616)],
["T10",14,(2.778,-1.2019,-7.5579)],
["T11",14,(1.1222,-5.0586,-5.3427)],
["T12",14,(0.4834,-3.2378,-7.8759)],
["T13",14,(2.4173,3.6086,-5.9341)],
["T14",14,(0.5333,4.6458,-3.7731)],
["T15",14,(5.0685,-2.0892,-5.8037)],
["T16",14,(5.59,0.5213,-4.1212)],
["T17",14,(5.2984,2.7097,-6.3662)]]

def distance(vec1,vec2):
	delta=Vector(vec1)-Vector(vec2)
	i=0
	d=0
	while i < 3:
	   d=d+(delta[i]*delta[i])
	   i=i+1
	d=math.sqrt(d)
	return d
	
def createatom(atom):
	bpy.ops.mesh.primitive_ico_sphere_add(view_align=False, enter_editmode=False, location=(atom[2]), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
	ob = bpy.context.object
	ob.name = atom[0]
	ob.show_name = False
	me = ob.data
	me.name = atom[0]
	atom[0]=str(ob.name)
	return atom

def makebond(a1, center, scn):
	#cursor=bpy.context.scene.cursor_location
	#cursor=center.location
	bondthickness=bpy.data.objects["bondthick"]
	curve = bpy.data.curves.new("lnk2", 'CURVE')
	spline = curve.splines.new('BEZIER')
	curve.dimensions="3D"
	curve.use_stretch = True
	curve.use_deform_bounds = True
	curve.use_radius = True

	spline.bezier_points.add(1)
	cen = spline.bezier_points[0]
	p1 = spline.bezier_points[1]
	cen.co = center.location-center.location
	cen.handle_left_type = 'VECTOR'    
	cen.handle_right_type = 'VECTOR'
	p1.co = a1.location-center.location
	p1.handle_right_type = 'VECTOR'
	p1.handle_left_type = 'VECTOR'
	

	obj = bpy.data.objects.new("lnk2", curve)
	
	obj.data.bevel_object=bondthickness
	m0 = obj.modifiers.new("alpha", 'HOOK')
	m0.object = center
	m1 = obj.modifiers.new("beta", 'HOOK')
	m1.object = a1
	
	scn.objects.link(obj)
	scn.objects.active = obj
	bpy.context.scene.cursor_location=center.location
	#bpy.ops.object.origin_set(type='ORIGIN_CURSOR') 
	obj.location=bpy.context.scene.cursor_location
	# using anything in bpy.ops is a giant pain in the butt
	bpy.ops.object.mode_set(mode='EDIT')

	# the mode_set() invalidated the pointers, so get fresh ones
	cen = curve.splines[0].bezier_points[0]
	
	p1 = curve.splines[0].bezier_points[1]

	cen.select_control_point=True
	bpy.ops.object.hook_assign(modifier="alpha")
	bpy.ops.object.hook_reset(modifier="alpha")

	cen.select_control_point = False
	p1.select_control_point = True
	bpy.ops.object.hook_assign(modifier="beta")
	bpy.ops.object.hook_reset(modifier="beta")    
	
	
	bpy.ops.object.mode_set(mode='OBJECT')
	#obj.location=center
	return obj

def symop(unit,op):
	if op==0: 
#   	print('zeroloop', op)
		for ct in range(1, len(unit)):
#   		print('vorsymop',unit[ct][2])
			unit[ct][2]= Vector(unit[ct][2])

	elif op==1: 
#   	print(op,'vorher')
		for ct in range(1, len(unit)):
#   		print('vorsymop',unit[ct][2])
			unit[ct][2]= -1*Vector(unit[ct][2])
#   print(op,'nachher')

# a[:] = [(x, y/7) for x, y in a]
#   		for cx in range (0,2): print(unit[ct][2],unit[ct][2][cx])
#    unit[ct][2][cx]=-unit[ct][2][cx]
	return unit    

print('newrun')
au=au0
for i in range (1,len(au0)):
	au[i].append(0)
	au[i].append((0,0,0))
for sym in range (2):
#  au[:]=[]
#  au=au0
#  print(sym,'au0',au0)
  au=symop(au,sym)   
#  print('main',sym)
#  print(sym,"au", au) 
#  curat[:]=[]
  for i in range (1,len(au)):
	  curat=au[i]
#symop
	  curat[3]=sym
#uc
	  curat[4]=((0,0,0))
	  ball = bpy.data.objects[createatom(curat)[0]]
#blendob
	  print('len',len(atomlist),curat) 
	  if i!=1:print('vor',atomlist[0][0]) 
	  atomlist.append(curat)
	  if i==1:print('nach',atomlist[0][0]) 

	  for j in range(0,len(atomlist)):
		  targetname=str(atomlist[j][0])
		  target=bpy.data.objects[targetname]
#   	   targetlocation=bpy.data.objects[targetname].location
		  dis=distance(target.location,ball.location)
#   	  print(target.name,ball.name,dis)
#   	   print(ball)
		  if dis<maxdis:
#   		  print(dis, atomlist[j][5],curat,ball)
			  makebond(target,ball,bpy.context.scene)
#   		  print(atomlist[j][5],ball)
			  curbnd[0]=target.name
			  curbnd[1]=ball.name
			  bondlist.append(curbnd)
#   		  curbnd[:]=[]
#makebond(bpy.data.objects['T3'],bpy.data.objects['T4'],bpy.context.scene)

#print(atomlist)
