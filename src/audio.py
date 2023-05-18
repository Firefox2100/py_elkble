import pyaudio
import numpy as np
import colorsys


class Audio:
    def __init__(self):
        # Set up audio stream
        p = pyaudio.PyAudio()
        self.stream = p.open(format=pyaudio.paFloat32, channels=1, rate=44100, input=True)

    def get_audio(self):
        return np.frombuffer(self.stream.read(1024), dtype=np.float32)

    def close(self):
        self.stream.close()

    @staticmethod
    def frequency_separation(audio_data):
        # Perform FFT
        fft_result = np.abs(np.fft.rfft(audio_data))

        # Map frequencies to RGB
        fft_len = len(fft_result)
        low_freq = np.average(fft_result[:fft_len // 3])
        mid_freq = np.average(fft_result[fft_len // 3: 2 * fft_len // 3])
        high_freq = np.average(fft_result[2 * fft_len // 3:])

        # Scale to [0, 1]
        total = low_freq + mid_freq + high_freq

        return low_freq, mid_freq, high_freq, total, fft_result

    @staticmethod
    def audio_to_rgb(audio_data):
        low_freq, mid_freq, high_freq, total, _ = Audio.frequency_separation(audio_data)

        if total > 0:
            low_freq /= total
            mid_freq /= total
            high_freq /= total

        return low_freq, mid_freq, high_freq

    @staticmethod
    def audio_to_rgb_from_hls(audio_data):
        smooth_hue = 0
        smooth_lightness = 0
        smooth_factor = 0.1

        low_freq, mid_freq, high_freq, total, fft_result = Audio.frequency_separation(audio_data)

        if total > 0:
            hue = (low_freq / total * 0.33) + (mid_freq / total * 0.67) + (high_freq / total * 1.0)
            lightness = total / len(fft_result)
            smooth_hue = smooth_factor * hue + (1 - smooth_factor) * smooth_hue
            smooth_lightness = smooth_factor * lightness + (1 - smooth_factor) * smooth_lightness

        # Convert to RGB
        r, g, b = colorsys.hls_to_rgb(smooth_hue, smooth_lightness, 1.0)

        return r, g, b


if __name__ == '__main__':
    audio = Audio()
    while True:
        print(audio.audio_to_rgb(audio.get_audio()))
        # print(audio.audio_to_rgb_from_hls(audio.get_audio()))
