import sys
import mido
from collections import defaultdict

midi_note_to_ly = {
        0: 'c',
        1: 'cis',
        2: 'd',
        3: 'dis',
        4: 'e',
        5: 'f',
        6: 'fis',
        7: 'g',
        8: 'gis',
        9: 'a',
        10: 'ais',
        11: 'b',
}

class Movement:
    from_note = None
    to_note = None
    note_number = None

    def __init__(self, from_note, to_note, note_number=None):
        self.from_note = from_note
        self.to_note = to_note
        self.note_number = note_number

    def is_parallel_to_movement(self, other):
        bad_intervals = (
                0,  # Octave
                5,  # Forth
                7,  # Fifth
        )
        for bad_interval in bad_intervals:
            if self.from_note % 12 != (other.from_note + bad_interval) % 12:
                continue
            if self.to_note % 12 != (other.to_note + bad_interval) % 12:
                continue
            if self.from_note < self.to_note and other.from_note > other.to_note:
                # opposite direction in both movements
                continue
            return True
        return False


def main():
    m = mido.MidiFile(sys.argv[1])
    movements = defaultdict(dict)
    for track_idx, track in enumerate(m.tracks):
        time = 0
        note_number = 0
        prev_note = None
        for msg in track:
            if msg.type != 'note_on':
                continue
            time += msg.time
            if msg.velocity > 0:
                note_number += 1
            if prev_note is not None and msg.note != prev_note:
                movements[track_idx][time] = Movement(prev_note, msg.note, note_number=note_number)
            prev_note = msg.note
    for track_idx in movements:
        for other_track_idx in movements:
            if other_track_idx <= track_idx:
                continue
            for time, movement in movements[track_idx].items():
                if not time in movements[other_track_idx]:
                    continue
                other_movement = movements[other_track_idx][time]
                if movement.is_parallel_to_movement(other_movement):
                    print(f"{time} ticks: Track {track_idx}'s movement from {midi_note_to_ly[movement.from_note % 12]} to {midi_note_to_ly[movement.to_note % 12]} (note #{movement.note_number}) is parallel to Track {other_track_idx}'s movement from {midi_note_to_ly[other_movement.from_note % 12]} to {midi_note_to_ly[other_movement.to_note % 12]} (note #{other_movement.note_number})")


if __name__ == '__main__':
    main()


import unittest
class Test(unittest.TestCase):
    def test_parallel(self):
        m1 = Movement(69, 70)
        m2 = Movement(70, 71)
        self.assertEqual(m1.is_parallel_to_movement(m2), False)

    def test_parallel_same(self):
        m1 = Movement(69, 70)
        m2 = Movement(69, 70)
        self.assertEqual(m1.is_parallel_to_movement(m2), True)

    def test_parallel_same_other_direction(self):
        m1 = Movement(69, 74)
        m2 = Movement(69, 62)
        self.assertEqual(m1.is_parallel_to_movement(m2), False)

    def test_parallel_octave(self):
        m1 = Movement(69, 70)
        m2 = Movement(81, 82)
        self.assertEqual(m1.is_parallel_to_movement(m2), True)

    def test_parallel_ok(self):
        m1 = Movement(69, 70)
        m2 = Movement(81, 81)
        self.assertEqual(m1.is_parallel_to_movement(m2), False)

    def test_parallel_fifth(self):
        m1 = Movement(69, 70)
        m2 = Movement(76, 77)
        self.assertEqual(m1.is_parallel_to_movement(m2), True)

    def test_parallel_fifth_ok(self):
        m1 = Movement(69, 70)
        m2 = Movement(76, 76)
        self.assertEqual(m1.is_parallel_to_movement(m2), False)

    def test_parallel_forth(self):
        m1 = Movement(69, 70)
        m2 = Movement(74, 75)
        self.assertEqual(m1.is_parallel_to_movement(m2), True)

    def test_parallel_forth_ok(self):
        m1 = Movement(69, 70)
        m2 = Movement(74, 74)
        self.assertEqual(m1.is_parallel_to_movement(m2), False)
