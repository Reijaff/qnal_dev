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

# while True:
    # mytext = input("My text: ")
    # start_time = time.time()
    # samples = tts.synthesize(
        # mytext
    # # '''
    # # As to be expected, the delivery from upstream developer patches to downstream linux distributions packages, can and will be delayed in cases like this one. This problem is not specific to any linux distribution in particular and can be very daunting to backport much needed hotfix to your otherwise stable system.
    # # ''' 
        # , speaker)
    # #"up to you what to do with the synthesized samples, in this example we will save them to a file.", speaker)
    # # up to you what to do with the synthesized samples (np.int16 array)
    # # in this example we will save them to a file

    # myout = io.BytesIO()
    # # myout.setparams((1, 2, tts.get_sampling_rate(), len(samples), "NONE", "NONE"))
    # # myout.writeframes(samples)
    # print(dir(samples))
    # # breakpoint()

    # scaled = np.int16(samples / np.max(np.abs(samples)) * 32767)
    # write(myout, sampling_rate, scaled)



    # with wave.open("/tmp/tmp.wav", "w") as fp:
        # fp.setparams((1, 2, tts.get_sampling_rate(), len(samples), "NONE", "NONE"))
        # fp.writeframes(samples)
    # print("time: ", time.time() - start_time)





@app.route("/api/balacoon_tts", methods=["GET", "POST"])
def balacoon_tts():
    # global speaker, tts
    text = request.headers.get("text") or request.values.get("text", "")
    # speaker_idx = request.headers.get("speaker-id") or request.values.get("speaker_id", "")
    # language_idx = request.headers.get("language-id") or request.values.get("language_id", "")
    # style_wav = request.headers.get("style-wav") or request.values.get("style_wav", "")
    # style_wav = style_wav_uri_to_dict(style_wav)

    print(f" > Model input: {text}")
    # print(f" > Speaker Idx: {speaker_idx}")
    # print(f" > Language Idx: {language_idx}")

    # wavs = synthesizer.tts(text, speaker_name=speaker_idx, language_name=language_idx, style_wav=style_wav)
    # out = io.BytesIO()
    # synthesizer.save_wav(wavs, out)

    # text = "Since 1980, 63 grizzlies have been hit by trains and killed along a section of railroad near Glacier National Park. Many died because they got drunk on fermented grain spilled from railcars and couldn’t move fast enough to outrun the trains."

    # myout.setparams((1, 2, tts.get_sampling_rate(), len(samples), "NONE", "NONE"))
    # myout.writeframes(samples)
    out = io.BytesIO()
    samples = tts.synthesize(text, speaker)

    with wave.open("/tmp/tmp.wav", "w") as fp:
        fp.setparams((1, 2, tts.get_sampling_rate(), len(samples), "NONE", "NONE"))
        fp.writeframes(samples)

    return send_file("/tmp/tmp.wav", mimetype="audio/wav")


    # scaled = np.int16(samples / np.max(np.abs(samples)) * 32767)
    # write(out, sampling_rate, scaled)


    # return send_file(out, mimetype="audio/wav")

app.run(port=5300)
