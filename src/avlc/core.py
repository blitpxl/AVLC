from .event import AudioPlayerEvent
from random import randint

import threading
import warnings
import vlc


class PlaybackMode(object):
    normal = 0
    repeatTrack = 1
    shuffle = 2
    repeatPlaylist = 3


class AudioPlayer(object):
    def __init__(self):
        super(AudioPlayer, self).__init__()
        self.vlcInstance = vlc.Instance()
        self.vlcPlayer = self.vlcInstance.media_player_new()
        self.vlcMediaList = []
        self.playerIndex = 0
        self.playbackMode = 0
        self.connect_event(AudioPlayerEvent.InternalTrackEndReached, self._on_track_end_reached)

    def _on_track_end_reached(self):
        if self.playbackMode == 0 or self.playbackMode == 3:
            self.next()
        elif self.playbackMode == 1:
            self.play(self.playerIndex)
        elif self.playbackMode == 2:
            self.play(randint(0, self.get_media_count() - 1))
        else:
            warnings.warn("Invalid playback mode, Defaulting to normal playback mode.", RuntimeWarning)
            self.next()
        AudioPlayerEvent.TrackEndReached.call()

    def _on_playlist_end_reached(self):
        if self.playbackMode == 3:
            self.play(0)
        else:
            AudioPlayerEvent.PlaylistEndReached.call()

    def add_media(self, uri):
        self.vlcMediaList.append(self.vlcInstance.media_new(uri))
        AudioPlayerEvent.MediaAdded.call()

    def play(self, trackIndex: int = 0, position: int = 0):
        if not trackIndex >= self.get_media_count():
            self.playerIndex = trackIndex
        else:
            warnings.warn("Track Index out of range, Defaulting to 0", RuntimeWarning)
            self.playerIndex = 0
        self.vlcPlayer.set_media(self.vlcMediaList[self.playerIndex])
        self.vlcPlayer.play()
        self.vlcPlayer.set_time(position)

    def pause(self):
        self.vlcPlayer.pause()

    def stop(self):
        self.vlcPlayer.stop()

    def next(self):
        if not self.playerIndex + 1 >= self.get_media_count():
            self.playerIndex += 1
            self.play(self.playerIndex)
            AudioPlayerEvent.NextTrack.call()
        else:
            self._on_playlist_end_reached()

    def previous(self):
        if not self.playerIndex - 1 < 0:
            self.playerIndex += 1
            self.play(self.playerIndex)
            AudioPlayerEvent.PrevTrack.call()
        else:
            pass

    def set_volume(self, value: int):
        self.vlcPlayer.audio_set_volume(value)

    def set_playback_mode(self, playbackMode: PlaybackMode):
        self.playbackMode = playbackMode

    def get_volume(self):
        return self.vlcPlayer.audio_get_volume()

    def get_media_count(self):
        return len(self.vlcMediaList)

    def connect_event(self, eventType, function):
        if hasattr(eventType, "callback_fn"):
            eventType.set_callback(function)
        else:
            def callback_thread(_):
                threading.Thread(target=function).start()
            self.vlcPlayer.event_manager().event_attach(eventType, callback_thread)
