import time
import json
import wave
import io
import base64
import pathlib
import tqdm
import subprocess
import numpy as np
from scipy.io.wavfile import write
from flask import Flask, render_template, render_template_string, request, send_file

import whisper_timestamped as whisper

import torch
import torchaudio

from resemble_enhance.enhancer.inference import denoise, enhance

if torch.cuda.is_available():
    device = "cuda"
else:
    device = "cpu"

print(device)

app = Flask(__name__)

from huggingface_hub import hf_hub_download

# addon_path = hf_hub_download(repo_id="balacoon/tts", filename="en_us_hifi92_light_cpu.addon")
addon_path = hf_hub_download(
    repo_id="balacoon/tts", filename="en_us_hifi_jets_cpu.addon"
)


# model_path = hf_hub_download(
    # repo_id="rhasspy/piper-voices",
    # filename="en/en_US/lessac/high/en_US-lessac-high.onnx",
# )
# config_path = hf_hub_download(
    # repo_id="rhasspy/piper-voices",
    # filename="en/en_US/lessac/high/en_US-lessac-high.onnx.json",
# )
enhance_path = hf_hub_download(
    repo_id="ResembleAI/resemble-enhance",
    filename="enhancer_stage2/ds/G/default/mp_rank_00_model_states.pt",
)

pp = pathlib.Path(enhance_path)
my_run_dir = pp.parent.parent.parent.parent
# print(pp.parents)
# print(pp.parts)
# print(pp.absolute())
# print(dir(pp))
# print(model_path)
# print(config_path)
# print(addon_path)
# print(enhance_path)

from balacoon_tts import TTS

# adjust the path to the addon based on the previous step
tts = TTS(addon_path)
# this will return a list of speakers that model supports.
supported_speakers = tts.get_speakers()
# speaker = supported_speakers[-1]
print(supported_speakers)
speaker = supported_speakers[-1]
# finally run synthesis
# samples = tts.synthesize("Being honest, I think the second problem I pointed out is not-fixable by design, since the rec specifier will replace the urls content with the variables, thus even if I possibly find a way to access super.src.url the replace would’ve happend in the super object, returing me a pre-formatted url (pointing to the old package). This whole log4j event gave me a mountain of memes, some material to tinker with and, more importatly, something some-what interesting to write about! I’m happy to be back and I hope I will find some more interesting stuff to write about in the future!", speaker)
sampling_rate = tts.get_sampling_rate()


@app.route("/api/balacoon_tts", methods=["GET", "POST"])
def balacoon_tts():
    # global speaker, tts

    text = request.headers.get("text") or request.values.get("text", "")
    isTranscription = (
        request.headers.get("transcription")
        or request.values.get("transcription", "")
        or False
    )
    isEnhance = False


    tmp_file_name = "/tmp/tmp.wav"

    print(f" > Model input: {text}")
    out = io.BytesIO()
    samples = tts.synthesize(text, speaker)

    with wave.open(tmp_file_name, "w") as fp:
        fp.setparams((1, 2, tts.get_sampling_rate(), len(samples), "NONE", "NONE"))
        fp.writeframes(samples)

    # p = subprocess.run(
        # [
            # "piper",
            # "-m",
            # f"{model_path}",
            # "-c",
            # f"{config_path}",
            # "-f",
            # tmp_file_name,
        # ],
        # input=text,
        # encoding="ascii",
    # )

    # pbar = tqdm(paths)

    # out_path = args.out_dir / path.relative_to(args.in_dir)

    # Cool emoji effect saying the job is done
    # elapsed_time = time.perf_counter() - start_time
    # print(f"🌟 Enhancement done! {len(paths)} files processed in {elapsed_time:.2f}s"

    transcription_data = None
    print(isTranscription)

    if isEnhance:
        # enhance
        dwav, sr = torchaudio.load(tmp_file_name)
        dwav = dwav.mean(0)
        hwav, sr = enhance(
            dwav=dwav,
            sr=sr,
            device=device,
            nfe=64,
            solver="midpoint",
            lambd=1,
            tau=0.5,
            run_dir=my_run_dir,
        )
        # out_path.parent.mkdir(parents=True, exist_ok=True)
        torchaudio.save(tmp_file_name, hwav[None], sr)
        # 

    
    if isTranscription == "True":
        audio = whisper.load_audio(tmp_file_name)
        model = whisper.load_model("tiny", device="cpu")
        transcription_data = whisper.transcribe(model, audio, language="en")

    encoded_string = None
    with open(tmp_file_name, "rb") as file:
        encoded_string = base64.b64encode(file.read()).decode("utf-8")

    ret_data = {
        "audio": encoded_string,
        "transcription": transcription_data,
    }
    return ret_data


app.run(port=5300)
