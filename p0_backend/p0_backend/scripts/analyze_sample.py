import math
import sys
from typing import List

import librosa
import numpy as np
from numpy import ndarray


def frequency_to_note(freq: float):
    notes = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]

    note_number = 12 * math.log2(freq / 440) + 49
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


def process_wav_file(file_path):
    # Load the audio file using librosa
    audio_data, sr = librosa.load(file_path, sr=None, mono=True)
    print(f"Sample rate : {sr} Hz")

    # Calculate the skip samples (10 milliseconds)
    skip_samples = int(sr * 0.01)

    # Skip the first 10 milliseconds
    audio_data = audio_data[skip_samples:]

    sample_counts = get_zero_crossing_sample_counts(audio_data)

    frequencies = get_sample_frequencies(sr, sample_counts)
    # print(f"Sample counts : {sample_counts}")
    print(f"Frequencies : {[round(f, 2) for f in frequencies]}")
    if len(frequencies) < 5:
        print("Not enough frequencies")
        return

    average_freq = sum(frequencies[-5:]) / 5
    closest_note, octave, cent = frequency_to_note(average_freq)
    print(
        f"Last 5 average: {average_freq:.2f} Hz, {closest_note}{octave}{'+' if cent >= 0 else ''}{cent}"
    )


def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <filename.wav>")
        sys.exit(1)

    file_path = sys.argv[1]
    process_wav_file(file_path)
