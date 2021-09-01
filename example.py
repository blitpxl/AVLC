from avlc import AudioPlayer, AudioPlayerEvent

a = AudioPlayer()
a.connect_event(AudioPlayerEvent.Playing, lambda: print("Playing"))
a.add_media("AudioExample/Eliminate - This Song Is Copyright Free.mp3")
a.add_media("AudioExample/TheFatRat & Slaydit - Solitude.mp3")
a.play()

input()
