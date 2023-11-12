import bpy
import blf
import gpu
from gpu_extras.batch import batch_for_shader
import re


# based on https://github.com/JacquesLucke/AudioToMarkers


class Marking_of_Highlights(bpy.types.Operator):
    bl_idname = "qnal.marking_of_highlights"
    bl_label = "Insert Markers"
    bl_description = "hello kitty"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        aef = bpy.context.active_editable_fcurve is not None
        return aef

    def invoke(self, context, event):
        self.insertion_preview_data = None
        if context.area.type == "GRAPH_EDITOR":
            self._handle = bpy.types.SpaceGraphEditor.draw_handler_add(
                self.draw_callback_px, (context,), 'WINDOW', 'POST_PIXEL')
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report(
                {'WARNING'}, "GraphEditor not found, cannot run operator")
            return {'CANCELLED'}

    def modal(self, context, event):
        context.area.tag_redraw()

        if event.type == 'ESC':
            context.area.header_text_set(None)
            bpy.types.SpaceGraphEditor.draw_handler_remove(
                self._handle, 'WINDOW')
            return {'FINISHED'}
        context.area.header_text_set("Press ESC to finish")

        _fcurve = bpy.context.active_editable_fcurve
        if _fcurve is None:
            return {"RUNNING_MODAL"}

        if not self.is_mouse_inside(event, bpy.context.region):
            return {"PASS_THROUGH"}

        # ==== calculate highlight
        start_frame = round(
            bpy.context.region.view2d.region_to_view(event.mouse_region_x - 20, 0)[0])
        end_frame = round(
            bpy.context.region.view2d.region_to_view(event.mouse_region_x + 20, 0)[0])

        snap_frame = 0
        max_value = -float("inf")
        for frame in range(start_frame, end_frame):
            value = _fcurve.evaluate(frame)
            if value > max_value:
                snap_frame = frame
                max_value = value
        snap_location = bpy.context.region.view2d.view_to_region(
            snap_frame, max_value)
        # ====

        marked_frames = [
            marker.frame for marker in bpy.context.scene.timeline_markers]

        self.insertion_preview_data = {
            "loc": snap_location,
            "marked": snap_frame not in marked_frames
        }

        if event.type == "LEFTMOUSE":
            if snap_frame not in marked_frames:
                bpy.context.scene.timeline_markers.new(
                    name="#{}".format(snap_frame), frame=snap_frame)
                return {"RUNNING_MODAL"}

        if event.type == "RIGHTMOUSE":
            if snap_frame in marked_frames:
                for marker in bpy.context.scene.timeline_markers:
                    if marker.frame == snap_frame:
                        bpy.context.scene.timeline_markers.remove(marker)
                        return {"RUNNING_MODAL"}

        return {"PASS_THROUGH"}

    def is_mouse_inside(self, event, area):
        padding = 5
        return padding <= event.mouse_region_x < area.width-padding and padding < event.mouse_region_y < area.height-padding

    def draw_callback_px(self, context):
        if self.insertion_preview_data is None:
            return
        loc = self.insertion_preview_data["loc"]
        marked = self.insertion_preview_data["marked"]

        if marked:
            color = (0, 1, 0, 1)
            size = 8.0
        else:
            color = (1, 0, 0, 1)
            size = 8.0

        shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
        shader.uniform_float("color", color)
        gpu.state.point_size_set(size)
        batch = batch_for_shader(
            shader, 'POINTS', {"pos": [loc]})
        batch.draw(shader)


def menu_func(self, context):
    # self.layout.operator_context = 'INVOKE_DEFAULT'
    self.layout.operator(Marking_of_Highlights.bl_idname,
                         text="Marking of Highlights", icon='SNAP_INCREMENT')


classes = [Marking_of_Highlights]


def register():
    for c in classes:
        bpy.utils.register_class(c)

    bpy.types.GRAPH_HT_header.append(menu_func)


def unregister():
    for c in classes[::-1]:
        bpy.utils.unregister_class(c)

    bpy.types.GRAPH_HT_header.remove(menu_func)