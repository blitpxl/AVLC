from .util import get_local_file, RandomMediaIndexGenerator
from .enums import PlaybackMode, SortMode, SortBy
from .event import AudioPlayerEvent
from operator import attrgetter
from natsort import os_sorted
from .media import AvlcMedia
from typing import Union

import threading
import warnings
import ctypes
import vlc


def set_lib(dll, plugin_path=None):
    vlc.dll = ctypes.CDLL(dll)
    vlc.plugin_path = plugin_path


class AudioPlayer(object):

    set_lib(get_local_file("dll/libvlc.dll"))

    def __init__(self, *vlcArgs):
        super(AudioPlayer, self).__init__()
        self.vlcInstanceArgs = [*vlcArgs]
        self.vlcInstance = vlc.Instance(self.vlcInstanceArgs)
        self.vlcPlayer = self.vlcInstance.media_player_new()

        self.mediaList = []
        self.sortMedia = False
        self.playerIndex = 0
        self.playbackMode = PlaybackMode.normal
        self.volumeLimit = 100
        self.mediaIndexGenerator = RandomMediaIndexGenerator()

        self.connect_internal_events()  # connect internal events

        # reconnect internal events if vlcInstance new args added/removed
        self.connect_event(AudioPlayerEvent.ArgsChanged, self.connect_internal_events)

    def connect_internal_events(self):
        self.connect_event(AudioPlayerEvent.InternalTrackEndReached, self._on_track_end_reached)

    def _on_track_end_reached(self):  # called everytime MediaListPlayer finished playing player track
        self.next()
        AudioPlayerEvent.TrackEndReached()

    def _on_playlist_end_reached(self):  # called everytime MediaListPlayer finished playing player playlist
        if self.playbackMode == 3:
            self.play(0)
            AudioPlayerEvent.PlaylistEndRepeat()
        else:
            AudioPlayerEvent.PlaylistEndReached()

    # NOTE: Reloading vlcInstance/vlcPlayer will require the user to reconnect the native events (not the avlc events)
    # because the native events were tied to the vlcPlayer. You can listen to AudioPlayerEvent.ArgsChanged to be
    # notified when the vlcInstance/vlcPlayer is reloaded

    def _reload_instance(self, new_args):               # ====== method to reload vlcInstance and vlcPlayer ======
        self.vlcPlayer.release()                        # delete the player object, which will also stop playback
        self.vlcInstance.release()                      # delete the old vlcInstance
        self.vlcInstance = vlc.Instance(new_args)       # create new vlcInstance with new args passed into it
        self.vlcPlayer = self.vlcInstance.media_player_new()  # create new player object from the new vlcInstance

    def add_args(self, *vlcArgs):                       # ====== add new args into vlcInstance at runtime ======
        position = self.get_position()                  # remember song position
        playback_rate = self.get_playback_rate()        # remember the playback rate/speed
        self.vlcInstanceArgs += list(vlcArgs)           # add new argument/s to the argument container
        self._reload_instance(self.vlcInstanceArgs)     # reload the vlcInstance and apply the args inside the container
        self.play(self.playerIndex, position)           # continue playing the song from the saved position
        self.set_playback_rate(playback_rate)           # reapply the playback rate to the new player
        AudioPlayerEvent.ArgsChanged()                  # emit signal that the instance finished reloading

    def remove_args(self, *vlcArgs):                    # does the same thing as above, but this time it's removing the
        position = self.get_position()                  # arguments instead of adding it into the vlcInstance
        playback_rate = self.get_playback_rate()
        for args in vlcArgs:
            self.vlcInstanceArgs.remove(args)
        self._reload_instance(self.vlcInstanceArgs)
        self.play(self.playerIndex, position)
        self.set_playback_rate(playback_rate)
        AudioPlayerEvent.ArgsChanged()

    def sort_media_list(self, sortBy=SortBy.filename, sortMode=SortMode.ascending):
        currentPlayingMedia = self.mediaList[self.playerIndex]
        self.mediaList = os_sorted(self.mediaList, key=attrgetter(sortBy), reverse=sortMode)
        self.playerIndex = self.mediaList.index(currentPlayingMedia)

    def add_avlc_media(self, avlcmedia):
        self.mediaList.append(avlcmedia)

    def add_local_media(self, uri: str):
        self.mediaList.append(AvlcMedia(uri, "local", self.vlcInstance))
        AudioPlayerEvent.MediaAdded()
        return self

    def add_youtube_media(self, url: str):
        self.mediaList.append(AvlcMedia(url, "youtube", self.vlcInstance))
        AudioPlayerEvent.MediaAdded()
        return self

    def play(self, trackIndex: int = 0, position: int = 0):
        if not trackIndex >= self.get_media_count():
            self.playerIndex = trackIndex
        else:
            msg = f"Track Index out of range ({trackIndex}), Defaulting to 0"
            warnings.warn(msg, RuntimeWarning)
            self.playerIndex = 0
        self.vlcPlayer.set_media(self.mediaList[self.playerIndex].vlcMediaObject)
        self.vlcPlayer.play()
        self.vlcPlayer.set_time(position)
        return self

    def pause(self):
        self.vlcPlayer.pause()
        return self

    def stop(self):
        self.vlcPlayer.stop()
        return self

    def next(self):
        if self.playbackMode == PlaybackMode.normal or self.playbackMode == PlaybackMode.repeatPlaylist:
            if not self.playerIndex + 1 >= self.get_media_count():
                self.playerIndex += 1
                self.play(self.playerIndex)
                AudioPlayerEvent.NextTrack()
            else:
                self._on_playlist_end_reached()
        elif self.playbackMode == PlaybackMode.repeatTrack:
            self.play(self.playerIndex)
            AudioPlayerEvent.NextTrack()
        elif self.playbackMode == PlaybackMode.shuffle:
            randomIndex = self.mediaIndexGenerator(self.get_media_count())
            if randomIndex is None:
                AudioPlayerEvent.PlaylistEndReached()
            else:
                self.play(randomIndex)
            AudioPlayerEvent.NextTrack()
        else:
            msg = f"Invalid playback mode, Resetting playlist position index"
            warnings.warn(msg, RuntimeWarning)
            self.play(0)
            AudioPlayerEvent.NextTrack()
        return self

    def previous(self):
        if not self.playerIndex - 1 < 0:
            self.playerIndex -= 1
            self.play(self.playerIndex)
            AudioPlayerEvent.PrevTrack()
        else:
            pass
        return self

    def set_playback_rate(self, playback_rate: float):
        self.vlcPlayer.set_rate(playback_rate)
        return self

    def set_position(self, position: int):
        self.vlcPlayer.set_time(position)
        return self

    def set_volume(self, value: int):
        if not value > self.volumeLimit:
            self.vlcPlayer.audio_set_volume(value)
        else:
            AudioPlayerEvent.VolumeLimitReached()
        return self

    def set_volume_limit(self, value: int):
        self.volumeLimit = value
        return self

    def set_playback_mode(self, playbackMode: Union[int, PlaybackMode]):
        self.playbackMode = playbackMode
        AudioPlayerEvent.PlaybackModeChanged()
        return self

    def get_playback_rate(self):
        return self.vlcPlayer.get_rate()

    def get_position(self):
        return self.vlcPlayer.get_time()

    def get_volume(self):
        return self.vlcPlayer.audio_get_volume()

    def get_volume_limit(self):
        return self.volumeLimit

    def get_media_count(self):
        return len(self.mediaList)

    def connect_event(self, eventType, function):
        if hasattr(eventType, "callbacks"):
            eventType.set_callback(function)
        else:
            def callback_thread(_):
                threading.Thread(target=function).start()
            self.vlcPlayer.event_manager().event_attach(eventType, callback_thread)
        return self

    def wait(self):
        input("AudioPlayer is running... Press enter to close.")
        self.cleanup()

    def cleanup(self):
        self.vlcPlayer.release()
        for media in self.mediaList:
            media.vlcMediaObject.release()
        self.vlcInstance.release()
        AudioPlayerEvent.CleanupEvent()
