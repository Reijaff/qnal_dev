import bpy
import bpy_extras

# based on https://github.com/JacquesLucke/AudioToMarkers

frequency_ranges = (
    ("0 - 20 Hz", (0, 20)),
    ("20 - 40 Hz", (20, 40)),
    ("40 - 80 Hz", (40, 80)),
    ("80 - 250 Hz", (80, 250)),
    ("250 - 600 Hz", (250, 600)),
    ("600 - 4000 Hz", (600, 4000)),
    ("4 - 6 kHz", (4000, 6000)),
    ("6 - 8 kHz", (6000, 8000)),
    ("8 - 20 kHz", (8000, 20000)))

frequency_range_dict = {
    frequency_range[0]: frequency_range[1] for frequency_range in frequency_ranges}
frequency_range_items = [(frequency_range[0], frequency_range[0], "")
                         for frequency_range in frequency_ranges]


class SoundGraphs(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(default="unknown")
    g: bpy.props.FloatProperty(default=0.0)


class BakeAudioSettings(bpy.types.PropertyGroup):

    def callback(self, context):
        audio_strips = []
        for seq in context.scene.sequence_editor.sequences_all:
            if type(seq) == bpy.types.SoundSequence:
                audio_strips.append(seq)

        if audio_strips == []:
            return [("empty", "empty", "empty")]

        audio_strips_info = []
        for strip in audio_strips:
            audio_strips_info.append(
                (strip.name, strip.name, bpy.path.abspath(strip.sound.filepath)))
        return audio_strips_info

    audio_strip: bpy.props.EnumProperty(
        items=callback,
        name="Audio Strips",
        description="Which audio strips to bake",
    )

    def apply_frequency_range(self, context):
        self.low_frequency, self.high_frequency = frequency_range_dict[
            self.frequency_range]

    frequency_range: bpy.props.EnumProperty(
        name="frequency Range", items=frequency_range_items, default="80 - 250 Hz", update=apply_frequency_range)
    low_frequency: bpy.props.FloatProperty(name="Low frequency", default=80)
    high_frequency: bpy.props.FloatProperty(name="High frequency", default=250)


def only_select_fcurve(fcurve):
    deselect_all_fcurves()
    fcurve.select = True


def deselect_all_fcurves():
    for fcurve in iter_all_fcurves():
        fcurve.select = False


def iter_all_fcurves():
    for action in bpy.data.actions:
        for fcurve in action.fcurves:
            yield fcurve


class Bake_Audio_Frequencies(bpy.types.Operator):
    bl_idname = "qnal.bake_audio_frequency"
    bl_label = "bake chosen frequency"
    bl_description = "hello kitty"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        settings = bpy.context.scene.bake_audio_data

        audio_strip_name = bpy.context.scene.bake_audio_data.audio_strip
        for seq in context.scene.sequence_editor.sequences_all:
            if seq.name == audio_strip_name:
                _property_name = f"freq.{round(settings.low_frequency)}-{round(settings.high_frequency)}.{seq.sound.name}"
                _graph = None
                _fcurve = None

                for graph in bpy.context.scene.sound_graphs:
                    if graph.name == _property_name:
                        _graph = graph

                if _graph == None:
                    _graph = bpy.context.scene.sound_graphs.add()
                    _graph.name = _property_name
                    _graph.keyframe_insert("g")

                for fcurve in bpy.context.scene.animation_data.action.fcurves:
                    if _graph == eval("bpy.context.scene." + fcurve.data_path.split('.')[0]):
                        _fcurve = fcurve
                only_select_fcurve(_fcurve)

                bpy.context.scene.frame_current = seq.frame_final_start

                bpy.ops.graph.sound_bake(
                    filepath=seq.sound.filepath,
                    low=settings.low_frequency,
                    high=settings.high_frequency,)
        return {"FINISHED"}


class Bake_All_Audio_Frequencies(bpy.types.Operator):
    bl_idname = "qnal.bake_all_audio_frequencies"
    bl_label = "bake chosen frequency"
    bl_description = "hello kitty"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        settings = bpy.context.scene.bake_audio_data

        audio_strip_name = bpy.context.scene.bake_audio_data.audio_strip
        for seq in context.scene.sequence_editor.sequences_all:
            if seq.name == audio_strip_name:
                for r in frequency_range_dict.values():
                    print(r)  # TODO: make progress bar
                    _property_name = f"freq.{r[0]}-{r[1]}.{seq.sound.name}"
                    _graph = None
                    _fcurve = None

                    for graph in bpy.context.scene.sound_graphs:
                        if graph.name == _property_name:
                            _graph = graph

                    if _graph == None:
                        _graph = bpy.context.scene.sound_graphs.add()
                        _graph.name = _property_name
                        _graph.keyframe_insert("g")

                    for fcurve in bpy.context.scene.animation_data.action.fcurves:
                        if _graph == eval("bpy.context.scene." + fcurve.data_path.split('.')[0]):
                            _fcurve = fcurve
                    only_select_fcurve(_fcurve)

                    bpy.context.scene.frame_current = seq.frame_final_start

                    bpy.ops.graph.sound_bake(
                        filepath=seq.sound.filepath,
                        low=r[0],
                        high=r[1])
        return {"FINISHED"}


def menu_func(self, context):
    # self.layout.operator_context = 'INVOKE_DEFAULT'
    self.layout.operator(Bake_Audio_Frequencies.bl_idname,
                         text="Marking of Highlights", icon='SNAP_INCREMENT')


class GRAPH_EDITOR_PT_Bake_Audio(bpy.types.Panel):
    bl_space_type = 'GRAPH_EDITOR'
    bl_region_type = 'UI'
    bl_label = "Bake Audio"
    bl_category = 'Bake'
    # bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        settings = bpy.context.scene.bake_audio_data
        layout = self.layout

        strip = bpy.context.scene.sequence_editor.active_strip
        # bpy.ops.graph.sound_bake()
        layout.prop(settings, "audio_strip")

        col = layout.column(align=False)
        col.enabled = settings.audio_strip != "empty"

        subcol = col.column(align=True)
        subcol.prop(settings, "frequency_range", text="")
        subcol.prop(settings, "low_frequency", text="Low")
        subcol.prop(settings, "high_frequency", text="High")

        col.operator(Bake_Audio_Frequencies.bl_idname,
                     text="bake chosen frequency")
        col.operator(Bake_All_Audio_Frequencies.bl_idname,
                     text="bake all frequencies")


classes = [BakeAudioSettings, SoundGraphs, Bake_Audio_Frequencies, Bake_All_Audio_Frequencies,
           GRAPH_EDITOR_PT_Bake_Audio]


def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.Scene.bake_audio_data = bpy.props.PointerProperty(
        type=BakeAudioSettings)

    bpy.types.Scene.sound_graphs = bpy.props.CollectionProperty(
        type=SoundGraphs)


def unregister():
    for c in classes[::-1]:
        bpy.utils.unregister_class(c)