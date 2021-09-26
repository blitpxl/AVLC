from vlc import EventType


class AvlcEventObject(object):
    def __init__(self, allowMultipleAssignment: bool = True):
        super(AvlcEventObject, self).__init__()
        self.multipleAssignment = allowMultipleAssignment

        self.callbacks = []
        self.callback = lambda x=None: None

    def __call__(self, arg=None):
        if self.multipleAssignment:
            if arg is None:
                for callback in self.callbacks:
                    callback()
            else:
                for callback in self.callbacks:
                    callback(arg)
        else:
            if arg is None:
                self.callback()
            else:
                self.callback(arg)

    def set_callback(self, callback_fn):
        if self.multipleAssignment:
            self.callbacks.append(callback_fn)
        else:
            self.callback = callback_fn


class AudioPlayerEvent(object):
    # internally used native vlc events is reserved but still can be utilized under other event name
    InternalTrackEndReached = EventType(265)

    # native vlc events
    Opening = EventType(258)
    Buffering = EventType(259)
    Playing = EventType(260)
    Paused = EventType(261)
    Stopped = EventType(262)
    Error = EventType(266)
    VolumeChanged = EventType(283)
    PositionChanged = EventType(267)

    # avlc custom events. can be called internally or externally
    TrackEndReached = AvlcEventObject()
    PlaylistEndRepeat = AvlcEventObject()
    PlaylistEndReached = AvlcEventObject()
    NextTrack = AvlcEventObject()
    PrevTrack = AvlcEventObject()
    MediaAdded = AvlcEventObject()
    PlaybackModeChanged = AvlcEventObject()
    VolumeLimitReached = AvlcEventObject()
    CleanupEvent = AvlcEventObject()
    ArgsChanged = AvlcEventObject()


class MediaEvent(object):
    InternalParsed = EventType(3)
    DurationChanged = EventType(2)

    Parsed = AvlcEventObject(allowMultipleAssignment=False)
