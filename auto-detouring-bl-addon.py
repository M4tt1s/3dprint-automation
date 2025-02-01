
bl_info = {
    "name": "Auto-detouring 3d printing tool",
    "blender": (2, 80, 0),
    "category": "Automation",
}

import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator
from bpy.props import StringProperty
from bpy.utils import register_class

import bmesh

import numpy as np
 
class TEST_OT_import_tst(Operator, ImportHelper):
    bl_idname = 'autodetour.import_npy'
    bl_label = 'Import Path'
    bl_options = {'PRESET', 'UNDO'}
 
    filename_ext = '.npy'
    
    filter_glob: StringProperty(
        default='*.npy',
        options={'HIDDEN'}
    )
 
    def execute(self, context):

        verts = []
        edges = []
        faces = []

        path = np.load(self.filepath)
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
 
 
register_class(TEST_OT_import_tst)
 
bpy.ops.autodetour.import_npy('INVOKE_DEFAULT')
