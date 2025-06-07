import tkinter as tk
from tkinter import ttk, filedialog
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import spectrogram, get_window
from scipy.io import wavfile
import sounddevice as sd

from signals import *

class SpectrogramGui:
    def __init__(self, root):
        self.root = root
        self.root.title("Spectrogram Viewer")
        self.audio_data = None
        self.audio_fs = None

        self.create_widgets()

    def create_widgets(self):
        frame = tk.Frame(self.root)
        frame.pack(pady=10)

        # Select specific signal
        tk.Label(frame, text="Signal Type:").grid(row=0, column=0)
        self.signal_type = tk.StringVar(value="Linear Chirp")
        ttk.Combobox(frame, textvariable=self.signal_type, values=[
            "Linear Chirp", "Exponential Chirp", "Piecewise Sinusoid", "Piecewise Sum", "Audio File"
        ]).grid(row=0, column=1)

        # Window changer
        tk.Label(frame, text="Window Length:").grid(row=1, column=0)
        self.win_len = tk.IntVar(value=256)
        tk.Entry(frame, textvariable=self.win_len, width=10).grid(row=1, column=1)

        # Overlap changer
        tk.Label(frame, text="Overlap:").grid(row=2, column=0)
        self.overlap = tk.IntVar(value=128)
        tk.Entry(frame, textvariable=self.overlap, width=10).grid(row=2, column=1)

        tk.Label(frame, text="Window Type:").grid(row=3, column=0)
        self.window_type = tk.StringVar(value="hann")
        ttk.Combobox(frame, textvariable=self.window_type, values=["rectangular", "hann", "hamming"]).grid(row=3, column=1)

        # Buttons
        tk.Button(frame, text="Plot Spectrogram", command=self.plot_spectrogram).grid(row=4, column=0, columnspan=2, pady=5)
        tk.Button(frame, text="Load Audio File", command=self.load_audio).grid(row=5, column=0, columnspan=2, pady=5)
        tk.Button(frame, text="Plot Audio Waveform", command=self.plot_audio_waveform).grid(row=6, column=0, columnspan=2, pady=5)
        tk.Button(frame, text="Play Audio", command=self.play_audio).grid(row=7, column=0, columnspan=2, pady=5)
        tk.Button(frame, text="Detect High-Energy Region", command=self.detect_high_energy).grid(row=8, column=0, columnspan=2, pady=5)

    def load_audio(self):
        file_path = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
        if file_path:
            self.audio_fs, data = wavfile.read(file_path)
            self.audio_data = data.astype(np.float32)
            if self.audio_data.ndim > 1:
                # select first channel if stereo
                self.audio_data = self.audio_data[:, 0]

    def plot_audio_waveform(self):
        # if selected signal is not audio file or not any audio loaded then return
        if self.signal_type.get() != "Audio File" or self.audio_data is None:
            return
        t = np.arange(len(self.audio_data)) / self.audio_fs
        plt.figure(figsize=(8, 3))
        plt.plot(t, self.audio_data)
        plt.title("Audio Signal (Time Domain)")
        plt.xlabel("Time [s]")
        plt.ylabel("Amplitude")
        plt.tight_layout()
        plt.show()

    def play_audio(self):
        if self.signal_type.get() == "Audio File" and self.audio_data is not None:
            sd.play(self.audio_data, self.audio_fs)

    def detect_high_energy(self):
        if self.signal_type.get() != "Audio File" or self.audio_data is None:
            return
        frame_len = self.win_len.get()
        jumping_range = frame_len - self.overlap.get()

        # simple discrete energy formula for each window
        energy = [
            np.sum(self.audio_data[i:i+frame_len] ** 2)
            for i in range(0, len(self.audio_data) - frame_len, jumping_range)
        ]
        # convert to numpy array
        energy = np.array(energy)
        # defining a threshold for max energy
        threshold = 0.6 * np.max(energy)
        high_energy_indices = np.where(energy > threshold)[0]

        if len(high_energy_indices) == 0:
            print("No high energy regions")
            return

        start_time = high_energy_indices[0] * jumping_range / self.audio_fs
        end_time = high_energy_indices[-1] * jumping_range / self.audio_fs
        print(f"High energy region: {start_time} s to {end_time} s")

    def plot_spectrogram(self):
        signal_name = self.signal_type.get()

        if signal_name == "Audio File":
            if self.audio_data is None:
                print("No audio file loaded!!")
                return
            x = self.audio_data
            fs = self.audio_fs
        else:
            if signal_name == "Linear Chirp":
                signal = LinearChirp()
            elif signal_name == "Exponential Chirp":
                signal = ExponentialChirp()
            elif signal_name == "Piecewise Sinusoid":
                signal = PiecewiseSinusoid()
            elif signal_name == "Piecewise Sum":
                signal = PiecewiseSumOfSinusoids()
            else:
                return
            _, x, fs = signal.generate()

        nperseg = self.win_len.get()
        noverlap = self.overlap.get()
        win_type = self.window_type.get()

        if win_type == "rectangular":
            window = np.ones(nperseg)
        else:
            window = get_window(win_type, nperseg)

        f, t_spec, Sxx = spectrogram(x, fs=fs, window=window, nperseg=nperseg, noverlap=noverlap)

        plt.figure(figsize=(8, 4))
        # plotting spectrogram (energy unit is dB)
        plt.pcolormesh(t_spec, f, 10 * np.log10(Sxx + 1e-10), shading='gouraud')
        plt.title(f"Spectrogram: {signal_name}")
        plt.xlabel("Time [s]")
        plt.ylabel("Frequency [Hz]")
        plt.colorbar(label="Power/Frequency (dB/Hz)")
        plt.tight_layout()
        plt.show()
