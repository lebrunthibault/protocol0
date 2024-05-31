from enum import Enum


class InputRoutingChannelEnum(Enum):
    # AUDIO
    PRE_FX = "Pre FX"
    POST_FX = "Post FX"
    POST_MIXER = "Post Mixer"

    # MIDI
    CHANNEL_1 = "Ch. 1"
    CTHULHU = "Cthulhu_x64"
