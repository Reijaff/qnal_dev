import time
import wave
import io
import numpy as np
from scipy.io.wavfile import write
from flask import Flask, render_template, render_template_string, request, send_file

app = Flask(__name__)

from huggingface_hub import hf_hub_download
# addon_path = hf_hub_download(repo_id="balacoon/tts", filename="en_us_hifi92_light_cpu.addon")
addon_path = hf_hub_download(repo_id="balacoon/tts", filename="en_us_hifi_jets_cpu.addon")


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

    print(f" > Model input: {text}")
    out = io.BytesIO()
    samples = tts.synthesize(text, speaker)

    with wave.open("/tmp/tmp.wav", "w") as fp:
        fp.setparams((1, 2, tts.get_sampling_rate(), len(samples), "NONE", "NONE"))
        fp.writeframes(samples)

    return send_file("/tmp/tmp.wav", mimetype="audio/wav")

app.run(port=5300)
