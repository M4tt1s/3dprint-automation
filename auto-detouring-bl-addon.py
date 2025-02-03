
bl_info = {
    "name": "Auto-detouring 3d printing tool",
    "description": "A 3d Printing Tool that create 2d planes from drawings",
    "author": "M4tt1s_",
    "version": (0, 1),
    "blender": (3, 0, 0),
    "location": "3D View > Tools",
    "warning": "", # used for warning icon and text in addons panel
    "doc_url": "",
    "tracker_url": "",
    "support": "COMMUNITY",
    "category": "Tools"
}

import bpy

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       )
from bpy.types import (Panel,
                       Menu,
                       Operator,
                       PropertyGroup,
                       )
from bpy_extras.io_utils import ImportHelper

import bmesh

import cv2 as cv
import numpy as np


# ------------------------------------------------------------------------
#    Scene Properties
# ------------------------------------------------------------------------

class AutoDetouringProps(PropertyGroup) :

    mfile: StringProperty(
        name = "Image File",
        description="Choose an image to process :",
        default="",
        maxlen=1024,
        subtype='DIR_PATH' # FILE_PATH
        )
    
    mthick: FloatProperty(
        name = "Thickness",
        description = "Plane thickness",
        default = 0.0005,
        min = 0.00001,
        max = 0.01
        )
    
    msize: IntProperty(
        name = "Size",
        description="Width of the genereated mesh",
        default = 1,
        min = 1,
        max = 100
        )
    
    mythresh1: IntProperty(
        name = "Threshold 1",
        description="Threshold 1 for edge detection",
        default = 450,
        min = 100,
        max = 1000
        )
    
    mythresh2: IntProperty(
        name = "Threshold 2",
        description="Threshold 2 for edge detection",
        default = 600,
        min = 100,
        max = 1000
        )

    mreturn: StringProperty(
        name="Process message",
        description="Return message from process",
        default="",
        maxlen=1024,
        )


# ------------------------------------------------------------------------
#    Operators
# ------------------------------------------------------------------------

class AutoDetouringChooseFile(Operator, ImportHelper) :

    bl_label = "Select image"
    bl_idname = "autodetour.choosefile"
    bl_options = {'PRESET', 'UNDO'}
    
    filter_glob: StringProperty(
        default='*.jpg;*.jpeg;*.png;*.tif;*.tiff;*.bmp',
        options={'HIDDEN'}
    )
    
    def execute(self, context):
        scene = context.scene
        mytool = scene.my_tool

        mytool.mfile = self.filepath

class AutoDetouringProcess(Operator) :

    bl_label = "Process"
    bl_idname = "autodetour.process" 
    
    def execute(self, context):
        scene = context.scene
        mytool = scene.my_tool

        if mytool.mfile == "" :
            return {'FINISHED'}

        img = cv.imread(mytool.mfile)
        if img is None or img.size == 0:
            mytool.mreturn = f"Unable to read image {mytool.mfile}."
            return {'FINISHED'}
        
        gray_img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        edge_img = cv.Canny(gray_img, threshold1=450, threshold2=600)

        ratio = mytool.msize / len(edge_img[0])

        path = []

        for i in range(len(edge_img)) :
            for j in range(len(edge_img[i])) :
                if edge_img[i][j] == 255 :
                    path.append([i * ratio, j * ratio])

        path = np.array(path)

        verts = []
        edges = []
        faces = []

        last_p = []
        for p in path :
            verts.append([p[0], p[1], 0])
            # if len(last_p) :
            #     edges.append([[last_p[0], last_p[1], 0], [p[0], p[1], 0]]) # add a new edge
            last_p = p

        mesh = bpy.data.meshes.new("PathMesh")  # add the new mesh
        obj = bpy.data.objects.new(mesh.name, mesh)
        col = bpy.data.collections["Collection"]
        col.objects.link(obj)
        bpy.context.view_layer.objects.active = obj

        mesh.from_pydata(verts, edges, faces)

        return {'FINISHED'}


# ------------------------------------------------------------------------
#    Panel in Object Mode
# ------------------------------------------------------------------------

class AutoDetouringMenu(bpy.types.Panel) :

    bl_idname = "Menu_AutoDetour"
    bl_label = "Auto-detouring"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Tool"
    bl_context = ""
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return (context.object is not None)

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="Auto-detouring 3d Printing Tool")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        scene = context.scene
        mytool = scene.my_tool

        layout.separator(factor=.5)

        layout.prop(mytool, "mthick")
        layout.prop(mytool, "msize")
        layout.prop(mytool, "mythresh1")
        layout.prop(mytool, "mythresh2")
        layout.separator(factor=.5)

        layout.separator(factor=.5)
        layout.menu(AutoDetouringMenu.bl_idname, text="Choose Image", icon="SCENE")
        layout.operator("autodetour.choosefile")
        layout.label(text=mytool.mfile)

        layout.separator(factor=.5)
        layout.menu(AutoDetouringMenu.bl_idname, text="Process", icon="SCENE")
        layout.operator("autodetour.process")
        layout.label(text=mytool.mreturn)
        layout.separator()
        

# class AutoDetouringPlugin(Operator, ImportHelper):
#     bl_idname = 'printingtools.autodetour'
#     bl_label = 'Import Path'
#     bl_options = {'PRESET', 'UNDO'}
 
#     filename_ext = '.npy'
    
#     filter_glob: StringProperty(
#         default='*.npy',
#         options={'HIDDEN'}
#     )
 
#     def execute(self, context):

#         verts = []
#         edges = []
#         faces = []

#         path = np.load(self.filepath)
#         last_p = []
#         for p in path :
#             verts.append([p[0], p[1], 0])
#             # if len(last_p) :
#             #     edges.append([[last_p[0], last_p[1], 0], [p[0], p[1], 0]]) # add a new edge
#             last_p = p

#         mesh = bpy.data.meshes.new("PathMesh")  # add the new mesh
#         obj = bpy.data.objects.new(mesh.name, mesh)
#         col = bpy.data.collections["Collection"]
#         col.objects.link(obj)
#         bpy.context.view_layer.objects.active = obj

#         mesh.from_pydata(verts, edges, faces)        

#         return {'FINISHED'}
 

# ------------------------------------------------------------------------
#    Registration
# ------------------------------------------------------------------------

classes = (
    AutoDetouringProps,
    AutoDetouringChooseFile,
    AutoDetouringProcess,
    AutoDetouringMenu
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    
    bpy.types.Scene.my_tool = PointerProperty(type=AutoDetouringProps)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

    del bpy.types.Scene.my_tool


if __name__ == "__main__":
    register()
