"""
Linear audio volume fader.
"""

from typing import Union
import threading
import time


def _fadeInFunc(start_volume, target_volume, delay, set_volume_function, fade_finished_callback):
    if start_volume < target_volume:
        start_volume = target_volume - 10
    for volume_level in range(target_volume + 1 - start_volume):
        set_volume_function(volume_level + start_volume)
        time.sleep(delay)
    if fade_finished_callback is not None:
        fade_finished_callback()


def _fadeOutFunc(current_volume, delay, set_volume_function, fade_finished_callback):
    for volume_level in range(current_volume):
        set_volume_function(current_volume - volume_level)
        time.sleep(delay)
    if fade_finished_callback is not None:
        fade_finished_callback()


def volFadeIn(
    start_volume: int,
    target_volume: int,
    delay_s: Union[int, float],
    set_volume_function,
    fade_finished_callback=None,
):
    t = threading.Thread(
        target=_fadeInFunc,
        args=(start_volume, target_volume, delay_s, set_volume_function, fade_finished_callback),
    )
    t.start()


def volFadeOut(
    current_volume: int,
    delay_s: Union[int, float],
    set_volume_function,
    fade_finished_callback=None,
):
    t = threading.Thread(
        target=_fadeOutFunc,
        args=(current_volume, delay_s, set_volume_function, fade_finished_callback),
    )
    t.start()
