from Live._meta import LomObject


class Song(LomObject):
    class View(LomObject):
        pass


class BeatTime(LomObject):
    pass


class Quantization:
    q_no_q = 0
    q_8_bars = 1
    q_4_bars = 2
    q_2_bars = 3
    q_bar = 4
    q_half = 5
    q_half_triplet = 6
    q_quarter = 7
    q_quarter_triplet = 8
    q_eight = 9
    q_eight_triplet = 10
    q_sixtenth = 11
    q_sixtenth_triplet = 12
    q_thirtysecond = 13


class RecordingQuantization:
    rec_q_no_q = 0
    rec_q_quarter = 1
    rec_q_eight = 2
    rec_q_eight_triplet = 3
    rec_q_eight_eight_triplet = 4
    rec_q_sixtenth = 5
    rec_q_sixtenth_triplet = 6
    rec_q_sixtenth_sixtenth_triplet = 7
    rec_q_thirtysecond = 8
