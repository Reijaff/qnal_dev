import bpy
import os
import subprocess
import sys

from . import bake_audio_frequencies
from . import marking_of_highlights
from . import tts_coqui_docker 
from . import combine_edits
from . import add_scene_with_sound
from . import plane_quad_mask
from . import import_latex_as_curve 


bl_info = {
    "name": "qnal_blender_addon",
    "author": "reijaff",
    "description": "",
    "blender": (3, 4, 0),
    "version": (0, 5, 0),
    "location": "",
    "warning": "",
    "category": "Generic"
}

class QnalAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    tts_audio_project_folder: bpy.props.StringProperty(
        name="Folder name for TTS audio",
        description="Folder name for TTS audio in a specific folder alongside blend file",
        default="tts_audio",
    )

    tts_audio_preview_folder: bpy.props.StringProperty(
        name="Common folder path for TTS audio",
        description="Common folder path where TTS audio are stored",
        subtype="DIR_PATH",
        default=os.path.join(
            bpy.utils.user_resource("DATAFILES"), "tts_audio"),
    )

    #docker_access: bpy.props.BoolProperty()
    #audacity_initialized: bpy.props.BoolProperty()
    #deps_installed: bpy.props.BoolProperty()

    # docker_server_status: bpy.props.StringProperty(
        # name="docker server status", description="docker server status", default="off"
    # )

    tts_server_status: bpy.props.StringProperty(
        name="tts server status", description="tts server status", default="free"
    )

    def draw(self, context):
        # logger.info(f"Draw addon preferences {self.docker_access}")
        box = self.layout.box()

        row = box.row(align=True)
        row.operator("qnal.deps_check",
                     text="Check dependencies", icon="QUESTION")
        if self.deps_installed:
            row.label(text="Dependencies are installed", icon="CHECKBOX_HLT")
        else:
            row.label(text="Dependencies are not installed")#, icon="CHECKBOX_HLT")
            # row.operator(
                # "qnal.deps_install", text="Install dependencies", icon="CHECKBOX_DEHLT"
            # )

        if self.docker_access:
            box.operator(
                "qnal.docker_check", text="Docker access ensured", icon="CHECKBOX_HLT"
            )
        else:
            box.operator(
                "qnal.docker_check",
                text="Ensure your docker access",
                icon="CHECKBOX_DEHLT",
            )



def init_deps_check():
    addon_prefs = bpy.context.preferences.addons[__package__].preferences
    # logger.info("Checking dependencies")

    try:
        import pip
        import docker

        # logger.info(f"pip filepath : {pip.__file__}")

        addon_prefs.deps_installed = True
    except:
        addon_prefs.deps_installed = False


class Deps_Check(bpy.types.Operator):

    bl_label = "Check dependencies"
    bl_idname = "qnal.deps_check"

    bl_description = "Check dependencies"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        init_deps_check()
        return {"FINISHED"}

    def register():
        init_deps_check()


class Deps_Install(bpy.types.Operator):

    bl_label = "Install Dependencies"
    bl_idname = "qnal.deps_install"
    bl_description = "Install dependencies"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        # logger.info("Installing dependencies")
        # logger.info(f"python path : {sys.executable}")

        binary_path = bpy.app.binary_path
        blender_dir_path = os.path.dirname(binary_path)
        version_dir = ".".join(map(str, bpy.app.version[0:2]))
        target = os.path.join(
            blender_dir_path,
            version_dir,
            os.path.relpath("python/lib"),
            os.path.basename(sys.executable),
            os.path.relpath("site-packages"),
        )

        packages = ["docker"]

        _ret = subprocess.check_call([sys.executable, "-m", "ensurepip"])
        # logger.info(f"--> ensurepip : {_ret}")

        subprocess.check_call(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                f"--target={target}",
                "--upgrade",
                "pip",
            ]
        )

        for package in packages:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install",
                    f"--target={target}", package]
            )

        init_deps_check()

        return {"FINISHED"}


class QnalData(bpy.types.PropertyGroup):
    """Setting per Scene"""


    audio_is_playing: bpy.props.BoolProperty(description="Audio is playing")

    # audacity_declicker: bpy.props.BoolProperty(
        # description="Apply Audacity De-Clicker on audio", default=False
    # )

    input_text: bpy.props.StringProperty(
        description="Text to synthesize", default="Everything is a test!"
    )


classes = [
    QnalAddonPreferences,
    QnalData,
    Deps_Check,
    # Deps_Install,
]


def register():
    for c in classes:
        bpy.utils.register_class(c)

    bpy.types.Scene.qnal_data = bpy.props.PointerProperty(
        type=QnalData)

    tts_coqui_docker.register()
    import_latex_as_curve.register()
    combine_edits.register()
    add_scene_with_sound.register()
    plane_quad_mask.register()
    marking_of_highlights.register()
    bake_audio_frequencies.register()

def unregister():
    tts_coqui_docker.unregister()
    import_latex_as_curve.unregister()
    combine_edits.unregister()
    add_scene_with_sound.unregister()
    plane_quad_mask.unregister()
    marking_of_highlights.unregister()
    bake_audio_frequencies.unregister()

    for c in classes[::-1]:
        bpy.utils.unregister_class(c)
