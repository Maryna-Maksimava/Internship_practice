import ctypes, os

# Same calls as test-espeak.c, made against the installed DLL (no C compiler needed).
d = r"C:\Program Files\eSpeak NG"
os.add_dll_directory(d)
lib = ctypes.CDLL(os.path.join(d, "libespeak-ng.dll"))

AUDIO_OUTPUT_SYNCH_PLAYBACK = 2
espeakCHARS_AUTO = 0

lib.espeak_Initialize.restype = ctypes.c_int
sr = lib.espeak_Initialize(AUDIO_OUTPUT_SYNCH_PLAYBACK, 500, None, 0)
print("sample rate:", sr)
print("SetVoiceByName:", lib.espeak_SetVoiceByName(b"English"))
text = b"Hello world!"
print("Saying '%s'..." % text.decode())
lib.espeak_Synth(text, 500, 0, 0, 0, espeakCHARS_AUTO, None, None)
lib.espeak_Synchronize()
print("Done")
