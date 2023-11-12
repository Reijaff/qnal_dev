import bpy


class Qnal_Add_Scene_With_Sound(bpy.types.Operator):

    bl_label = "Scene with sound strips"
    bl_idname = "qnal.scene_strip_with_sound_add"
    bl_description = "Add scene with sound strips (sequencer mode)"
    bl_options = {"REGISTER", "UNDO"}

    scene: bpy.props.StringProperty(name="String Value")

    def execute(self, context):
        max_channel = 1

        frame_current = bpy.context.scene.frame_current
        in_scene = bpy.data.scenes[str(self.scene)]

        if not bpy.context.scene.sequence_editor:
            bpy.context.scene.sequence_editor_create()

        if not in_scene.sequence_editor:
            in_scene.sequence_editor_create()

        strips = in_scene.sequence_editor.sequences_all
        for strip in strips:
            if type(strip) == bpy.types.SoundSequence:
                new_strip = bpy.context.scene.sequence_editor.sequences.new_sound(
                    strip.name,
                    strip.sound.filepath,
                    strip.channel,
                    int(strip.frame_start) + frame_current,
                )
                bpy.data.sounds.remove(new_strip.sound)
                new_strip.sound = strip.sound

                new_strip.animation_offset_end = strip.animation_offset_end
                new_strip.animation_offset_start = strip.animation_offset_start
                new_strip.frame_offset_end = strip.frame_offset_end
                new_strip.frame_offset_start = strip.frame_offset_start
                new_strip.channel = strip.channel
                new_strip.speed_factor = strip.speed_factor
                new_strip.show_waveform = True

                max_channel = max(max_channel, strip.channel)

                # # animate # TODO copy f-curves
                # new_strip.pan = strip.pan
                # new_strip.volume = strip.volume

        bpy.ops.sequencer.scene_strip_add(
            scene=self.scene, channel=max_channel + 1, frame_start=frame_current
        )

        return {"FINISHED"}


class SEQUENCER_MT_add_scene_and_sound(bpy.types.Menu):
    bl_label = "Scene with sound"

    def draw(self, context):

        layout = self.layout
        layout.separator()
        for sc_item in bpy.data.scenes:
            if sc_item == context.scene:
                continue

            layout.operator(
                "qnal.scene_strip_with_sound_add",
                text=sc_item.name,
            ).scene = sc_item.name


def add_scene_and_sound_menu_draw(self, context):
    self.layout.menu(
        "SEQUENCER_MT_add_scene_and_sound",
        text="Scene with sound",
        icon="SEQ_SEQUENCER",
    )


classes = [Qnal_Add_Scene_With_Sound, SEQUENCER_MT_add_scene_and_sound]


def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.SEQUENCER_MT_add.append(add_scene_and_sound_menu_draw)


def unregister():
    for c in classes[::-1]:
        bpy.utils.unregister_class(c)
    bpy.types.SEQUENCER_MT_add.remove(add_scene_and_sound_menu_draw)
