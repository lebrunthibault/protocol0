import math
import os
import sys
from dataclasses import dataclass
from typing import List

import librosa
import numpy as np
from numpy import ndarray


def frequency_to_note(freq: float):
    notes = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]

    try:
        note_number = 12 * math.log2(freq / 440) + 49
    except ValueError:
        return "C", "-2", 0

    cent = round((note_number - round(note_number)) * 100)
    note_number = round(note_number)

    note = notes[(note_number - 1) % len(notes)]

    octave = (note_number + 8) // len(notes)

    return note, octave, cent


def get_zero_crossing_sample_counts(audio_data: ndarray) -> List[float]:
    # Compute zero crossings using librosa
    zero_crossings = librosa.zero_crossings(audio_data, pad=False)

    # Find zero crossing indices
    zero_crossings_indices = np.where(zero_crossings)[0]
    sample_counts = []

    # Print the number of samples, RMS, and frequency between each zero crossing
    for i in range(1, len(zero_crossings_indices)):
        start_index = zero_crossings_indices[i - 1]
        end_index = zero_crossings_indices[i]

        # Extract the audio segment between two zero crossings
        audio_segment = audio_data[start_index:end_index]

        # Check if RMS level is below -30 dB
        rms_level = np.sqrt(np.mean(audio_segment**2))
        if librosa.amplitude_to_db(np.array([rms_level])) < -30:
            break

        sample_counts.append(end_index - start_index)

    return sample_counts


def get_sample_frequencies(sr: float, sample_counts: List[float]) -> List[float]:
    # Check if the input list has at least two elements
    if len(sample_counts) < 2:
        print("Input list should have at least two elements.")
        return []

    # Use list comprehension to calculate the sum of adjacent elements
    result_list = [
        sr / (sample_counts[i] + sample_counts[i + 1]) for i in range(len(sample_counts) - 1)
    ]

    return result_list


@dataclass
class Frequency:
    frequency: float
    closest_note: str
    octave: str
    cent: int

    def __init__(self, frequency: float):
        self.frequency = frequency
        self.closest_note, self.octave, self.cent = frequency_to_note(frequency)

    def __repr__(self) -> str:
        return f"{self.frequency:.2f} Hz, {self.closest_note}{self.octave}{'+' if self.cent >= 0 else ''}{self.cent}"


@dataclass
class Frequencies:
    frequencies: List[float]
    average_freq: Frequency

    def __init__(self, frequencies: List[float]):
        self.frequencies = frequencies
        self.average_freq = Frequency(sum(frequencies[-5:]) / 5)

    def __repr__(self) -> str:
        if len(self.frequencies) < 5:
            return "Not enough frequencies"

        return f"Frequencies : {[round(f, 2) for f in self.frequencies]}"


def get_wav_file_frequency(file_path: str) -> Frequencies:
    # Load the audio file using librosa
    audio_data, sr = librosa.load(file_path, sr=None, mono=True)

    # skip attack (10 milliseconds)
    audio_data = audio_data[int(sr * 0.01) :]

    sample_counts = get_zero_crossing_sample_counts(audio_data)

    frequencies = get_sample_frequencies(sr, sample_counts)
    return Frequencies(frequencies)


def process_kick_directory(directory_path: str):
    for root, _, files in os.walk(directory_path):
        for file_name in files:
            if file_name.lower().endswith(".wav"):
                file_path = os.path.join(root, file_name)
                frequencies = get_wav_file_frequency(file_path)

                # Write frequencies to a text file with the same name as the WAV file
                output_file_path = os.path.splitext(file_path)[0] + ".txt"
                with open(output_file_path, "w") as output_file:
                    output_file.write(f"{frequencies}\n{frequencies.average_freq}")


def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <filename.wav>")
        sys.exit(1)

    process_kick_directory(sys.argv[1])
