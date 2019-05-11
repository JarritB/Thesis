bl_info = {
    "name": "Crystallographic Drawing Tool for Blender",
    "description": "Add-on for drawing crystals from CIF-files.",
    "author": "Jarrit Boons",
    "blender": (2, 80,0),
    "location": "View3D",
    "category": "Crystallography in Blender"
}

import bpy

File_Path = "..."
#
#   Opens a file select dialog and starts scanning the selected file.
#
class ScanFileOperator(bpy.types.Operator):
    bl_idname = "error.scan_file"
    bl_label = "Scan file for return"
    filepath = bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        File_Path = self.filepath
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

class Operator(bpy.types.Operator):
    bl_idname = "object.cdtb_operator"
    bl_label = "CDTB_operator"
    bl_descriptor = "Operator for drawing crystal"

    def execute(self, context):
        return {'FINISHED'}

    @classmethod
    def register(cls):
        print("Registered class: %s " % cls.bl_label)
        bpy.types.Scene.draw_bonds = bpy.props.BoolProperty(
        name="Draw bonds",
        description="Draw bonds between elements",
        )

    @classmethod
    def unregister(cls):
        print("Unregistered class: %s " % cls.bl_label)

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
        box = layout.box()
        row = box.row()
        row.label(text = 'Settings',icon ='PREFERENCES')
        box = layout.box()
        # Create a split row within it
        row = box.row()
        splitrow = row.split(factor=0.075)
        # Store references to each column of the split row
        left_col = splitrow.column()
        right_col = splitrow.column()
        left_col.operator('error.scan_file',icon='FILE',text="")
        right_col.label(text=File_Path)
        box.prop(scn,'draw_bonds')
        layout.separator()
        layout.operator('object.cdtb_operator',text="Draw Crystal")

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
