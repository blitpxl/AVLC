from .event import AudioPlayerEvent
from .util import get_local_file
from random import randint

import threading
import warnings
import ctypes
import vlc


def set_lib(dll, plugin_path=None):
    vlc.dll = ctypes.CDLL(dll)
    vlc.plugin_path = plugin_path


class PlaybackMode(object):
    normal = 0
    repeatTrack = 1
    shuffle = 2
    repeatPlaylist = 3


class AvlcMedia(object):
    """
    **Spawn new media object from vlcInstance**
    """

    pafy_obj = None

    def __init__(self, location, mediaType, vlcInstance):
        if mediaType == "local":
            self.vlcMediaObject = vlcInstance.media_new(location)
        else:
            self._import_pafy()
            p = self._get_pafy().new(location)
            a = p.getbest()
            self.vlcMediaObject = vlcInstance.media_new(a.url)
        self.path = location
        self.mediaType = mediaType

    @classmethod
    def _get_pafy(cls):
        return cls.pafy_obj

    @classmethod
    def _import_pafy(cls):
        if cls.pafy_obj is None:
            from pafy import pafy
            cls.pafy_obj = pafy


class AudioPlayer(object):
    """
    **Main class for handling music playback.**

    During the instantiation of this class it will also instantiate a new ``vlcInstance``
    which you could pass a vlc argument to.
    """

    set_lib(get_local_file("dll/libvlc.dll"))

    def __init__(self, vlcArg="vlc"):
        super(AudioPlayer, self).__init__()
        self.vlcInstance = vlc.Instance(vlcArg)
        self.vlcPlayer = self.vlcInstance.media_player_new()
        self.vlcMediaList = []
        self.playerIndex = 0
        self.playbackMode = 0
        self.volumeLimit = 100
        self.connect_event(AudioPlayerEvent.InternalTrackEndReached, self._on_track_end_reached)

    def _on_track_end_reached(self):  # called everytime AudioPlayer finished playing a track
        if self.playbackMode == 0 or self.playbackMode == 3:
            self.next()
        elif self.playbackMode == 1:
            self.play(self.playerIndex)
        elif self.playbackMode == 2:
            self.play(randint(0, self.get_media_count() - 1))
        else:
            msg = f"Invalid playback mode, Defaulting to normal playback mode."
            warnings.warn(msg, RuntimeWarning)
            self.next()
        AudioPlayerEvent.TrackEndReached.call()

    def _on_playlist_end_reached(self):  # called everytime AudioPlayer finished playing a playlist
        if self.playbackMode == 3:
            self.play(0)
            AudioPlayerEvent.PlaylistEndRepeat.call()
        else:
            AudioPlayerEvent.PlaylistEndReached.call()

    def add_local_media(self, uri: str):
        """
        **Add a local media from disk to the playlist.**

        :param uri: path to the media or media uri
        """

        self.vlcMediaList.append(AvlcMedia(uri, "local", self.vlcInstance))
        AudioPlayerEvent.MediaAdded.call()

    def add_youtube_media(self, url: str):
        """
        **Add a youtube media to stream into the playlist.**

        *Remember that you cannot stream a live video.*

        :param url: url to a youtube video
        """

        self.vlcMediaList.append(AvlcMedia(url, "youtube", self.vlcInstance))
        AudioPlayerEvent.MediaAdded.call()

    def play(self, trackIndex: int = 0, position: int = 0):
        """
        **Play the media inside the playlist.**

        :param trackIndex: the starting index to play when you call the function
        :param position: the start position of a track when it got played
        """

        if not trackIndex >= self.get_media_count():
            self.playerIndex = trackIndex
        else:
            msg = f"Track Index out of range ({trackIndex}), Defaulting to 0"
            warnings.warn(msg, RuntimeWarning)
            self.playerIndex = 0
        self.vlcPlayer.set_media(self.vlcMediaList[self.playerIndex].vlcMediaObject)
        self.vlcPlayer.play()
        self.vlcPlayer.set_time(position)

    def pause(self):
        """
        **Pause the current playing track.**
        """

        self.vlcPlayer.pause()

    def stop(self):
        """
        **Stop playing the current track.**
        """

        self.vlcPlayer.stop()

    def next(self):
        """
        **Play the next track in the playlist.**
        """

        if not self.playerIndex + 1 >= self.get_media_count():
            self.playerIndex += 1
            self.play(self.playerIndex)
            AudioPlayerEvent.NextTrack.call()
        else:
            self._on_playlist_end_reached()

    def previous(self):
        """
        **Play the previous track in playlist.**
        """
        if not self.playerIndex - 1 < 0:
            self.playerIndex += 1
            self.play(self.playerIndex)
            AudioPlayerEvent.PrevTrack.call()
        else:
            pass

    def set_position(self, position: int):
        """
        **Set the position of the current playing track.**

        :param position: time position in ms
        """

        self.vlcPlayer.set_time(position)

    def set_volume(self, value: int):
        """
        **Set the loudness level of the audio output.**

        The volume can be set to max of 200% but the current limit is set to 100%.
        To change the volume limit, use ``set_volume_limit()`` method.

        :param value: volume (0 - 200)
        :return:
        """

        if not value > self.volumeLimit:
            self.vlcPlayer.audio_set_volume(value)
        else:
            AudioPlayerEvent.VolumeLimitReached.call()

    def set_volume_limit(self, value: int):
        """
        **Set the volume limit**

        :param value: volume limit
        """

        self.volumeLimit = value

    def set_playback_mode(self, playbackMode: PlaybackMode):
        """
        **Set the playback mode for the AudioPlayer**

        Use ``PlaybackMode`` enum to set the mode.

        example: ``PlaybackMode.repeatTrack``

        :param playbackMode: PlaybackMode enum
        """

        self.playbackMode = playbackMode
        AudioPlayerEvent.PlaybackModeChanged.call()

    def get_position(self):
        """
        **Get the current position of the playing track.**

        :return: track position in ms
        """

        return self.vlcPlayer.get_time()

    def get_volume(self):
        """
        **Get the current volume level.**

        :return: volume level
        """

        return self.vlcPlayer.audio_get_volume()

    def get_volume_limit(self):
        """
        **Get the volume limit value**

        :return: volume limit value
        """

        return self.volumeLimit

    def get_media_count(self):
        """
        **Get the count of media in the playlist.**

        :return: count of media in playlist
        """

        return len(self.vlcMediaList)

    def connect_event(self, eventType, function):
        """
        **Connect a function to call when an event occured**

        Event Types are defined in ``AudioPlayerEvent`` class.

        :param eventType: the event to be listened to
        :param function: function to call when the event occured
        """

        if hasattr(eventType, "callbacks"):
            eventType.set_callback(function)
        else:
            def callback_thread(_):
                threading.Thread(target=function).start()
            self.vlcPlayer.event_manager().event_attach(eventType, callback_thread)
