from typing import List

import numpy as np
from loguru import logger

from pydantic import BaseModel

from p0_backend.api.client.p0_script_api_client import p0_script_client
from protocol0.application.command.KeyDetectedCommand import KeyDetectedCommand


class NoteModel(BaseModel):
    pitch: int
    start: float
    end: float


def analyze_key(notes_data: List[NoteModel]) -> None:
    logger.info(notes_data)
    """
    Analyze the musical key from MIDI note data.

    Args:
        notes_data: list of dicts with keys 'pitch', 'start', 'end'
                   e.g., [{'pitch': 60, 'start': 0.0, 'end': 1.0}, ...]

    Returns:
        str: The most likely key (e.g., "Cmaj", "Amin")
    """
    # ---- 1. Calculate duration from note data ----
    if not notes_data:
        raise ValueError("notes_data cannot be empty")

    duration = max(note.end for note in notes_data)

    # ---- 2. Extract pitch-class activity over time ----
    # Divide into small time windows (e.g., 0.5s)
    fs = 2.0  # frames per second
    n_frames = int(duration * fs)
    n_pitches = 12

    X = np.zeros((n_frames, n_pitches))

    for note in notes_data:
        start = int(note.start * fs)
        end = int(note.end * fs)
        pitch_class = note.pitch % 12
        X[start:end, pitch_class] += 1

    # Normalize to binary (active notes)
    X = (X > 0).astype(int)

    # ---- 3. Define possible hidden states (keys) ----
    notes = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]
    keys = [f"{n}maj" for n in notes] + [f"{n}min" for n in notes]
    n_states = len(keys)

    # ---- 4. Build transition matrix (uniform) ----
    A = np.ones((n_states, n_states)) / n_states

    # ---- 5. Define emission templates (Krumhansl key profiles) ----
    major_template = np.array(
        [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
    )
    minor_template = np.array(
        [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]
    )

    templates = []
    for i in range(12):
        templates.append(np.roll(major_template, i))
    for i in range(12):
        templates.append(np.roll(minor_template, i))
    templates = np.array([t / t.sum() for t in templates])

    # ---- 6. Compute observation likelihoods ----
    likelihoods = np.dot(X, templates.T)  # type: ignore[attr-defined]
    likelihoods_sum = likelihoods.sum(axis=1, keepdims=True)
    likelihoods_sum[likelihoods_sum == 0] = 1e-8
    likelihoods = likelihoods / likelihoods_sum

    # ---- 7. Manual Viterbi decoding ----
    n_frames = likelihoods.shape[0]
    log_A = np.log(A)
    log_likelihoods = np.log(likelihoods + 1e-12)

    viterbi = np.zeros((n_frames, n_states))
    backpointer = np.zeros((n_frames, n_states), dtype=int)

    # Initial probabilities = uniform
    viterbi[0] = np.log(1.0 / n_states) + log_likelihoods[0]

    for t in range(1, n_frames):
        for j in range(n_states):
            prob = viterbi[t - 1] + log_A[:, j] + log_likelihoods[t, j]
            backpointer[t, j] = np.argmax(prob)
            viterbi[t, j] = np.max(prob)

    # Backtrack to recover best state sequence
    state_seq = np.zeros(n_frames, dtype=int)
    state_seq[-1] = np.argmax(viterbi[-1])
    for t in range(n_frames - 2, -1, -1):
        state_seq[t] = backpointer[t + 1, state_seq[t + 1]]

    # ---- 8. Report most likely global key ----
    (unique, counts) = np.unique(state_seq, return_counts=True)
    dominant_state = unique[np.argmax(counts)]
    detected_key = keys[dominant_state]
    print("🎵 Most likely key:", detected_key)

    key = detected_key[:1]
    major_key = key
    if detected_key.endswith("min"):
        major_key = notes[notes.index(key) + 3 % 12]

    print("🎵 Major key:", major_key)
    p0_script_client().dispatch(KeyDetectedCommand(pitch=notes.index(key)))
