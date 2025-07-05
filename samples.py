import numpy as np


def clap(duration, samplerate, attack_time):

    # Sampling parameters
    samples = int(duration * samplerate)

    # Generate white noise
    noise = np.random.randn(samples)

    # Envelope to shape the noise (quick attack, exponential decay)
    envelope = np.zeros(samples)
    attack_samples = int(attack_time * samplerate)
    decay_samples = samples - attack_samples
    envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
    envelope[attack_samples:] = np.exp(-np.linspace(0, 5, decay_samples))

    # Shape the noise to make a clap
    clap = noise * envelope

    # Normalize
    clap /= np.max(np.abs(clap))

    return clap

def bass(duration, samplerate, freq=60, decay=50.0):
    """
    Generate a simple bass tone using a sine wave with exponential decay.

    Parameters:
    - duration (float): Length of sound in seconds.
    - samplerate (int): Samples per second.
    - freq (float): Frequency of the bass tone in Hz.
    - decay (float): How quickly the sound fades out.
    """
    t = np.linspace(0, duration, int(duration * samplerate), False)
    envelope = np.exp(-decay * t)
    wave = np.sin(2 * np.pi * freq * t) * envelope
    wave /= np.max(np.abs(wave))
    return wave

def pause(duration, samplerate):
    return np.zeros(int(duration * samplerate))
