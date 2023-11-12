# from .pipeclient import PipeClient
from . import async_loop

import requests
import hashlib
import asyncio
import shutil
import time
import aud
import sys
import os
import bpy


docker_client = None
docker_container = None

pipe_client = None


def init_docker():
    global docker_client
    # logger.info("Init Docker")

    addon_prefs = bpy.context.preferences.addons[__package__].preferences
    try:
        if docker_client == None:
            import docker
            docker_client = docker.from_env()

        addon_prefs.docker_access = docker_client.ping()  # TODO
    except:
        addon_prefs.docker_access = False  # TODO


class Docker_Check(bpy.types.Operator):

    bl_label = "Check docker"
    bl_idname = "qnal.docker_check"
    bl_description = "Check your docker access"
    bl_options = {"REGISTER", "UNDO"}

    # client = freesound_api.FreesoundClient()

    def execute(self, context):
        init_docker()
        return {"FINISHED"}

    def register():
        init_docker()

class Docker_Launch(bpy.types.Operator, async_loop.AsyncModalOperatorMixin):

    bl_label = "Launch docker"
    bl_idname = "qnal.docker_launch"
    bl_description = "Launch docker tts server"
    bl_options = {"REGISTER", "UNDO"}

    # client = freesound_api.FreesoundClient()

    async def async_execute(self, context):
        global docker_client
        global docker_container
        addon_prefs = bpy.context.preferences.addons[__package__].preferences

        if docker_client == None:
            import docker

            docker_client = docker.from_env()

        docker_container = docker_client.containers.run(
            "ghcr.io/coqui-ai/tts-cpu:latest",
            "--model_name tts_models/en/vctk/vits",
            entrypoint="tts-server",
            detach=True,
            volumes={
                f"/home/{os.getlogin()}/.local/share/tts": {
                    "bind": "/root/.local/share/tts",
                    "mode": "rw",
                }
            },
            ports={"5002/tcp": ("127.0.0.1", 5002)},
        )

        # logger.info("before request")
        addon_prefs.docker_server_status = "loading ..."
        while True:
            await asyncio.sleep(1)
            try:
                response = requests.get("http://127.0.0.1:5002/")
                if response.status_code == 200:
                    break
            except:
                pass

        addon_prefs.docker_server_status = "on"

        self.quit()
        # return {'FINISHED'}


def docker_stop():
    global docker_client
    global docker_container
    addon_prefs = bpy.context.preferences.addons[__package__].preferences

    if docker_container == None:
        addon_prefs.docker_server_status = "off"
    else:
        docker_container.stop()
        docker_container = None
        addon_prefs.docker_server_status = "off"


class Docker_Stop(bpy.types.Operator):

    bl_label = "Stop docker"
    bl_idname = "qnal.docker_stop"
    bl_description = "Stop docker tts server"
    bl_options = {"REGISTER", "UNDO"}

    # client = freesound_api.FreesoundClient()

    def execute(self, context):
        docker_stop()
        return {"FINISHED"}

    def unregister():
        bpy.context.preferences.addons[
            __package__
        ].preferences.docker_server_status = "off" # TODO
        docker_stop()


def doCommand(cmd):
    global pipe_client
    reply = ""
    pipe_client.write(cmd)
    start_time = time.time()
    while reply == "":
        time.sleep(0.1)
        if time.time() - start_time > 1 and cmd != "De-Clicker":
            reply = "Timeout"
            print(reply)
            sys.exit()

        reply = pipe_client.read()

    print(reply)
    return reply


def init_audacity():
    global pipe_client
    # logger.info("Init Audacity")
    addon_prefs = bpy.context.preferences.addons[__package__].preferences

    try:
        if pipe_client == None:
            pipe_client = PipeClient()

        reply = doCommand("Help")

        addon_prefs.audacity_initialized = True
    except:
        addon_prefs.audacity_initialized = False

    # logger.info(f"--> audacity_initialized : {addon_prefs.audacity_initialized}")


class Audacity_Check(bpy.types.Operator):

    bl_label = "Check Audacity Python API"
    bl_idname = "qnal.audacity_check"
    bl_description = "Check your Audacity Python API"
    bl_options = {"REGISTER", "UNDO"}

    # client = freesound_api.FreesoundClient()

    def execute(self, context):
        init_audacity()
        return {"FINISHED"}

    def register():
        init_audacity()


def tts_output(audio_filepath):
    print("hello from tts_output")
    global pipe_client
    addon_prefs = bpy.context.preferences.addons[__package__].preferences
    addon_data = bpy.context.scene.qnal_data

    addon_prefs.tts_server_status = "processing"
    payload = {
        "text": addon_data.input_text,
        # "speaker_id": addon_data.vctk_vits_speaker_idx,
    }
    ret = requests.get("http://127.0.0.1:5300/api/balacoon_tts", params=payload)
    addon_prefs.tts_server_status = "free"

    with open(audio_filepath, "wb") as f:
        f.write(ret.content)

    # if addon_data.audacity_declicker:
        # if pipe_client == None:
            # pipe_client = PipeClient()

        # # doCommand( 'SetProject: X=10 Y=10 Width=910 Height=800' )
        # doCommand("SelectAll")
        # doCommand("RemoveTracks")
        # doCommand(f"Import2: Filename={audio_filepath}")
        # doCommand("Select: Track=0")
        # doCommand("SelTrackStartToEnd")
        # doCommand("De-Clicker")
        # doCommand('TruncateSilence: Action="Compress Excess Silence" Compress=10')
        # doCommand("LoudnessNormalization")
        # doCommand("Select: Start=0 End=0.1")
        # doCommand("FadeIn")

        # # add filename + path
        # doCommand("SelTrackStartToEnd")
        # doCommand(f"Export2: Filename={audio_filepath}")

        # doCommand("SelectAll")
        # doCommand("RemoveTracks")


class TTS_Audio_Add(bpy.types.Operator):
    bl_label = "Add"
    bl_idname = "qnal.tts_audio_add"
    bl_description = "Add sound to the VSE at the current frame"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        addon_prefs = bpy.context.preferences.addons[__package__].preferences

        _input_text = bpy.context.scene.qnal_data.input_text
        _preview_folder = addon_prefs.tts_audio_preview_folder

        if _input_text == "":
            self.report({"ERROR"}, "Input text is empty")
            return {"FINISHED"}

        if not bpy.data.is_saved:
            self.report({"ERROR"}, "Project is not saved")
            return {"FINISHED"}

        # algorithm for audio name
        audio_name = hashlib.md5(
            _input_text.encode("utf-8")).hexdigest() + ".wav"

        # create directory for audio
        folderpath = os.path.join(
            os.path.dirname(
                bpy.data.filepath), addon_prefs.tts_audio_project_folder
        )
        if not os.path.isdir(folderpath):
            os.makedirs(folderpath, exist_ok=True)
        audio_filepath = os.path.join(folderpath, audio_name)

        preview_filepath = os.path.join(_preview_folder, audio_name)

        if os.path.isfile(preview_filepath):
            shutil.copy(preview_filepath, audio_filepath)

        if not os.path.isfile(audio_filepath):
            tts_output(audio_filepath)

        if not bpy.context.scene.sequence_editor:
            bpy.context.scene.sequence_editor_create()

        if not bpy.context.sequences:
            addSceneChannel = 1
        else:
            channels = [s.channel for s in bpy.context.sequences]
            channels = sorted(list(set(channels)))
            empty_channel = channels[-1] + 1
            addSceneChannel = empty_channel

        newStrip = bpy.context.scene.sequence_editor.sequences.new_sound(
            name=os.path.basename(audio_filepath),
            filepath=f"//{addon_prefs.tts_audio_project_folder}/{audio_name}",
            channel=addSceneChannel,
            frame_start=bpy.context.scene.frame_current,
        )
        newStrip.show_waveform = True
        newStrip.sound.use_mono = True
        # bpy.context.scene.sequence_editor.sequences_all[
        # newStrip.name
        # ].frame_start = bpy.context.scene.frame_current

        return {"FINISHED"}


class TTS_Audio_Play(bpy.types.Operator):
    bl_label = "Play"
    bl_idname = "qnal.tts_audio_play"
    bl_description = "Play audio preview"
    bl_options = {"REGISTER", "UNDO"}
    handle = 0

    def execute(self, context):
        addon_prefs = bpy.context.preferences.addons[__package__].preferences
        addon_data = bpy.context.scene.qnal_data
        _preview_folder = addon_prefs.tts_audio_preview_folder
        _input_text = bpy.context.scene.qnal_data.input_text

        if _input_text == "":
            self.report({"ERROR"}, "Input text is empty")
            return {"FINISHED"}

        if not bpy.data.is_saved:
            self.report({"ERROR"}, "Project is not saved")
            return {"FINISHED"}

        # algorithm for audio name
        audio_name = hashlib.md5(
            _input_text.encode("utf-8")).hexdigest() + ".wav"

        # create directory for audio

        if not os.path.isdir(_preview_folder):
            os.makedirs(_preview_folder, exist_ok=True)
        audio_filepath = os.path.join(_preview_folder, audio_name)

        if not os.path.isfile(audio_filepath):
            tts_output(audio_filepath)

        try:

            # Playing file audio_filepath
            addon_data.audio_is_playing = True
            device = aud.Device()
            audio = aud.Sound.file(audio_filepath)

            TTS_Audio_Play.handle = device.play(audio)
            TTS_Audio_Play.handle.loop_count = -1  # TODO

        except Exception as e:
            self.report({"WARNING"}, f"[Play] Error ... {e}")
            return {"CANCELLED"}

        return {"FINISHED"}


class TTS_Audio_Pause(bpy.types.Operator):
    bl_label = "Pause"
    bl_idname = "qnal.tts_audio_pause"
    bl_description = "Pause audio preview"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        addon_data = context.scene.qnal_data
        # if (addon_data.audio_loaded):
        addon_data.audio_is_playing = False
        TTS_Audio_Play.handle.stop()
        return {"FINISHED"}


class TTS_PT_Panel(bpy.types.Panel):
    bl_label = "Text To Speach"
    bl_space_type = "SEQUENCE_EDITOR"
    bl_region_type = "UI"
    bl_category = "TTS"

    @classmethod
    def poll(self, context):
        return context.space_data.view_type in {"SEQUENCER", "SEQUENCER_PREVIEW"}

    def draw(self, context):
        addon_prefs = bpy.context.preferences.addons[__package__].preferences

        # self.logger.info(f"docker access:{addon_prefs.docker_access}")
        # if not addon_prefs.docker_access:
            # col = self.layout.column(align=True)
            # col.label(text="Error accessing docker", icon="ERROR")
            # col.label(text="Check Addon Preferences")


class TTS_PT_subpanel_synthesize(bpy.types.Panel):
    bl_parent_id = "TTS_PT_Panel"
    bl_label = "Synthesize"

    bl_space_type = "SEQUENCE_EDITOR"
    bl_region_type = "UI"
    bl_category = "TTS"

    @classmethod
    def poll(cls, context):
        return True#bpy.context.preferences.addons[__package__].preferences.docker_access

    def draw(self, context):
        addon_prefs = bpy.context.preferences.addons[__package__].preferences
        addon_data = context.scene.qnal_data
        # if addon_prefs.docker_server_status != "on":
            # col = self.layout.column(align=True)
            # col.label(text="Error accessing docker server", icon="ERROR")
            # col.label(text="Launch docker server first")
        # else:

        col = self.layout.column(align=True)
        # col.scale_y = 2
        col.prop(addon_data, "input_text", text="", icon="RIGHTARROW")

        row = self.layout.row(align=True)
        if addon_data.audio_is_playing:
            row.operator("qnal.tts_audio_pause",
                            text="Pause", icon="PAUSE")
        else:
            row.operator("qnal.tts_audio_play",
                            text="Play", icon="PLAY_SOUND")

        # row.separator()
        row.operator("qnal.tts_audio_add",
                        text="Add", icon="NLA_PUSHDOWN")


class TTS_PT_subpanel_settings(bpy.types.Panel):
    bl_parent_id = "TTS_PT_Panel"
    bl_label = "Scene Settings"

    bl_space_type = "SEQUENCE_EDITOR"
    bl_region_type = "UI"
    bl_category = "TTS"

    def draw(self, context):
        addon_data = context.scene.qnal_data
        addon_prefs = bpy.context.preferences.addons[__package__].preferences

        col = self.layout.column(align=True)
        # col.operator("qnal.test_operator", text="test operator")
        # if addon_prefs.audacity_initialized:
            # col.prop(
                # addon_data,
                # "audacity_declicker",
                # text="Audacity De-Clicker",
                # toggle=True,
            # )
        # else:
            # col.label(text="Error accessing Audacity", icon="ERROR")
            # col.label(text="Setup Audacity Python API")

        box = self.layout.box()
        col = box.column()  # align=True)
        col.label(text="TTS server settings")

        row = col.row(align=True)
        row.label(text="Docker server status:")
        row.label(text=addon_prefs.docker_server_status)

        col.prop(addon_data, "model_name", text="Model")
        col.prop(addon_data, "vctk_vits_speaker_idx", text="Speaker id")

        # if addon_prefs.docker_server_status == "on":
            # col.operator("qnal.docker_stop",
                         # text="Stop docker server", icon="PAUSE")
        # elif addon_prefs.docker_server_status == "loading ...":
            # col.label(text=addon_prefs.docker_server_status)
        # elif addon_prefs.docker_server_status == "off":
            # col.operator("qnal.docker_launch",
                         # text="Launch docker server", icon="PLAY")


# order matters
classes = (
    async_loop.AsyncLoopModalOperator,
    # Audacity_Check,
    Docker_Check,
    Docker_Launch,
    Docker_Stop,
    TTS_Audio_Play,
    TTS_Audio_Add,
    TTS_Audio_Pause,
    TTS_PT_Panel,
    TTS_PT_subpanel_synthesize,
    TTS_PT_subpanel_settings,

)


def register():
    async_loop.setup_asyncio_executor()

    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    # global pipe_client
    # if pipe_client is not None and pipe_client._write_pipe is not None:
        # pipe_client.close()

    for c in classes[::-1]:
        bpy.utils.unregister_class(c)
