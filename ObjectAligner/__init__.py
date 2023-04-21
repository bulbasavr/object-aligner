bl_info = {
    "name": "Object Aligner",
    "author": "Stas Zvyagintsev",
    "version": (1, 0),
    "blender": (3, 4, 1),
    "location": "N-Panel > Object Aligner",
    "description": "Align the model",
    "warning": "",
    "doc_url": "",
    "category": "Object",
}

import bpy

from bpy.types import Operator, Panel
from bpy.utils import register_class, unregister_class


class OA_OT_object_aligner(Operator):
    bl_idname = "object.simple_operator"
    bl_label = "Align Object"

    def execute(self, context):
        self.align_object(context)
        return {'FINISHED'}

    def align_object(self, context) -> None:
        self.select_alignment_plane(context)
        active_obj = bpy.context.active_object.name
        aligner = self.add_aligner(context)
        self.set_parent(context, active_obj)

        self.set_active_object(context, aligner)
        self.clear_and_apply_transform(context)

        self.active_object_transform_apply(context, active_obj)

        self.change_selected_object(context, aligner)
        bpy.ops.object.delete(use_global=False)
        self.set_active_object(context, active_obj)

        self.align_view(context)

    def active_object_transform_apply(self, context, name: str) -> None:
        self.set_active_object(context, name)
        try:
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        except:
            pass

    def select_alignment_plane(self, context) -> None:
        bpy.ops.view3d.view_axis(type='BOTTOM')
        bpy.ops.view3d.view_axis(type='BOTTOM', align_active=True)
        bpy.ops.view3d.snap_cursor_to_selected()
        bpy.ops.object.editmode_toggle()

    def set_parent(self, context, child_element_name: str) -> None:
        bpy.data.objects[child_element_name].select_set(True)
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
        bpy.ops.object.select_all(action='TOGGLE')

    def set_active_object(self, context, name: str) -> None:
        bpy.data.objects[name].select_set(True)
        bpy.context.view_layer.objects.active = bpy.data.objects[name]

    def clear_and_apply_transform(self, context) -> None:
        bpy.ops.object.location_clear(clear_delta=False)
        bpy.ops.object.rotation_clear(clear_delta=False)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    def add_aligner(self, context) -> str:
        bpy.ops.object.empty_add(type='ARROWS', align='VIEW', scale=(1, 1, 1))
        return bpy.context.active_object.name

    def change_selected_object(self, context, name: str) -> None:
        bpy.ops.object.select_all(action='TOGGLE')
        self.set_active_object(context, name)

    def align_view(self, context) -> None:
        bpy.ops.view3d.view_selected()
        bpy.ops.view3d.view_axis(type='FRONT')


class OA_OT_object_aligner_without_origin(OA_OT_object_aligner):
    bl_idname = "object.object_aligner_dynamic_without_origin"
    bl_label = "Align the model"

    def execute(self, context):
        self.align_object(context)
        return {'FINISHED'}

    def align_object(self, context) -> None:
        self.select_alignment_plane(context)
        active_obj = bpy.context.active_object.name
        aligner = self.add_aligner(context)

        self.change_selected_object(context, active_obj)
        bpy.ops.view3d.snap_cursor_to_selected()

        self.change_selected_object(context, aligner)
        bpy.ops.view3d.snap_selected_to_cursor(use_offset=True)

        self.set_parent(context, active_obj)
        self.set_active_object(context, aligner)
        bpy.ops.object.rotation_clear(clear_delta=False)

        self.clear_and_apply_transform(context)
        self.active_object_transform_apply(context, active_obj)

        self.change_selected_object(context, aligner)
        bpy.ops.object.delete(use_global=False)
        self.set_active_object(context, active_obj)
        self.align_view(context)


class OA_OT_object_aligner_with_origin(OA_OT_object_aligner):
    bl_idname = "object.object_aligner_with_origin"
    bl_label = "Align and change origin"


class OA_PT_object_aligner(Panel):
    bl_label = "Object align"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Object Aligner"

    def draw(self, context):
        layout = self.layout
        row = layout.row()

        if bpy.context.mode == 'EDIT_MESH':
            row.operator('object.object_aligner_dynamic_without_origin', icon='ORIENTATION_CURSOR')
            row = layout.row()
            row.operator('object.object_aligner_with_origin', icon='OBJECT_ORIGIN')

        else:
            row.label(text=f'need to go into edit mode', icon='EDITMODE_HLT')


classes = (
    OA_OT_object_aligner_without_origin,
    OA_OT_object_aligner_with_origin,
    OA_PT_object_aligner
)


def register():
    for cl in classes:
        register_class(cl)


def unregister():
    for cl in reversed(classes):
        unregister_class(cl)


if __name__ == "__main__":
    register()
