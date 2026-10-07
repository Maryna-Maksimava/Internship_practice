#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <espeak-ng/speak_lib.h>

/* Usage: test-espeak [voice] [rate wpm] [pitch 0-99]
   e.g.   test-espeak en-us+f3 150 60 */
int main(int argc, char* argv[]) {
  const char *voice = argc > 1 ? argv[1] : "en-us+f3";
  int rate  = argc > 2 ? atoi(argv[2]) : 150;
  int pitch = argc > 3 ? atoi(argv[3]) : 55;
  const char *text =
    "Good morning. Today we are testing speech synthesis with eSpeak NG. "
    "The quick brown fox jumps over the lazy dog, while the rain falls softly on the quiet town. "
    "Numbers such as 1984 and 3.14159 are read aloud, and questions are spoken with a rising tone. "
    "Can you tell whether this voice sounds natural? Thank you for listening.";

  espeak_Initialize(AUDIO_OUTPUT_SYNCH_PLAYBACK, 500, NULL, 0);
  if (espeak_SetVoiceByName(voice) != EE_OK) {
    fprintf(stderr, "Voice '%s' not found\n", voice);
    return 1;
  }
  espeak_SetParameter(espeakRATE, rate, 0);
  espeak_SetParameter(espeakPITCH, pitch, 0);

  printf("Voice %s, rate %d, pitch %d\nSaying: %s\n", voice, rate, pitch, text);
  espeak_Synth(text, strlen(text) + 1, 0, POS_CHARACTER, 0, espeakCHARS_AUTO, NULL, NULL);
  espeak_Synchronize();
  printf("Done\n");
  espeak_Terminate();
  return 0;
}
