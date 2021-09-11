from avlc import AudioPlayer, AudioPlayerEvent
from avlc.tcm import ms2min

a = AudioPlayer()
a.set_volume(75)
a.add_local_media("AudioExample/Eliminate - This Song Is Copyright Free.mp3")
a.add_local_media("AudioExample/TheFatRat & Slaydit - Solitude.mp3")
a.play()

a.connect_event(AudioPlayerEvent.PositionChanged, lambda: print(ms2min(a.get_position())))
# everytime the track position changes, print the current position in the console

input()
