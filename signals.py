import numpy as np

class LinearChirp:
    def __init__(self, f0=100, f1=1000, T=5, fs=8000):
        self.f0 = f0
        self.f1 = f1
        self.T = T
        self.fs = fs
        self.k = (f1 - f0) / T

    def generate(self):
        t = np.linspace(0, self.T, int(self.T * self.fs), endpoint=False)
        x = np.sin(2 * np.pi * (self.f0 * t + (self.k / 2) * t**2))
        return t, x, self.fs

class ExponentialChirp:
    def __init__(self, f0=200, f1=2000, T=4, fs=8000):
        self.f0 = f0
        self.f1 = f1
        self.T = T
        self.fs = fs
        self.r = (f1 / f0) ** (1 / T)

    def generate(self):
        t = np.linspace(0, self.T, int(self.T * self.fs), endpoint=False)
        x = np.sin(2 * np.pi * self.f0 * ((self.r ** t - 1) / np.log(self.r)))
        return t, x, self.fs

class PiecewiseSinusoid:
    def __init__(self, fs=8000):
        self.fs = fs
        self.T = 6

    def generate(self):
        t = np.linspace(0, self.T, int(self.T * self.fs), endpoint=False)
        x = np.zeros_like(t)
        x[(0 <= t) & (t < 2)] = np.sin(2 * np.pi * 300 * t[(0 <= t) & (t < 2)])
        x[(2 <= t) & (t < 4)] = np.sin(2 * np.pi * 500 * t[(2 <= t) & (t < 4)])
        x[(4 <= t) & (t < 6)] = np.sin(2 * np.pi * 400 * t[(4 <= t) & (t < 6)])
        return t, x, self.fs

class PiecewiseSumOfSinusoids:
    def __init__(self, fs=8000):
        self.fs = fs
        self.T = 6

    def generate(self):
        t = np.linspace(0, self.T, int(self.T * self.fs), endpoint=False)
        x = np.zeros_like(t)
        x[(0 <= t) & (t < 2)] = (
            np.sin(2 * np.pi * 300 * t[(0 <= t) & (t < 2)]) +
            np.sin(2 * np.pi * 700 * t[(0 <= t) & (t < 2)])
        )
        x[(2 <= t) & (t < 4)] = (
            np.sin(2 * np.pi * 500 * t[(2 <= t) & (t < 4)]) +
            np.sin(2 * np.pi * 900 * t[(2 <= t) & (t < 4)])
        )
        x[(4 <= t) & (t < 6)] = (
            np.sin(2 * np.pi * 400 * t[(4 <= t) & (t < 6)]) +
            np.sin(2 * np.pi * 1200 * t[(4 <= t) & (t < 6)])
        )
        return t, x, self.fs