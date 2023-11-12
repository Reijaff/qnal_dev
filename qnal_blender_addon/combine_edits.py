import bpy
import re

def combine_edits_menu_draw(self, context):
    self.layout.operator(Qnal_Combine_Edits.bl_idname, icon="MOD_ARRAY")

class Qnal_Combine_Edits(bpy.types.Operator):

    bl_label = "Combine edits"
    bl_idname = "qnal.combine_edits"
    bl_description = "Combine scene edits (sequencer mode)"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        if not bpy.context.scene.sequence_editor:
            bpy.context.scene.sequence_editor_create()

        scene_names_sorted = []
        edit_scenes = {}
        for scene in bpy.data.scenes:
            if re.search("\.\d{3}\.edit$", scene.name):
                scene_names_sorted.append(scene.name)
                edit_scenes[scene.name] = {
                    "frame_start": scene.frame_start,
                    "frame_end": scene.frame_end,
                }

        scene_names_sorted.sort(key=lambda x: int(x.split(".")[-2]))

        cur = 1
        for scene_name in scene_names_sorted:
            beg = bpy.data.scenes[scene_name].frame_start
            end = bpy.data.scenes[scene_name].frame_end
            diff = end - beg + 1

            bpy.ops.sequencer.scene_strip_add(
                frame_start=cur, channel=2, scene=scene_name
            )
            bpy.context.active_sequence_strip.scene_input = "SEQUENCER"

            cur += diff

        print("frame end", cur)
        bpy.context.scene.frame_end = cur

        return {"FINISHED"}

def register():

    bpy.utils.register_class(Qnal_Combine_Edits)
    bpy.types.SEQUENCER_MT_add.append(combine_edits_menu_draw)

def unregister():
    bpy.utils.unregister_class(Qnal_Combine_Edits)
    bpy.types.SEQUENCER_MT_add.remove(combine_edits_menu_draw)