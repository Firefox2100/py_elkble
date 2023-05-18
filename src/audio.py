import asyncio
import pyaudio
import numpy as np
import colorsys

CHUNK_SIZE = 1024  # number of data points to read at a time
SR = 44100  # time resolution of the recording device (Hz)

# frequency bands in Hz
BASS_MAX = 300
VOCAL_MAX = 2000
INSTRUMENT_MAX = 20000


class Audio:
    stream = None

    def get_audio(self):
        return np.frombuffer(self.stream.read(CHUNK_SIZE), dtype=np.int16)

    def open(self):
        p = pyaudio.PyAudio()
        self.stream = p.open(format=pyaudio.paInt16, channels=1, rate=SR, input=True, frames_per_buffer=CHUNK_SIZE)

    def close(self):
        self.stream.close()

    @staticmethod
    def audio_to_rgb(audio_data):
        fourier = np.abs(np.fft.fft(audio_data)[:CHUNK_SIZE // 2])  # Use only first half of the fft output
        frequencies = np.fft.fftfreq(len(audio_data), 1.0 / SR)[:CHUNK_SIZE // 2]

        fourier_sum = fourier.sum()
        if fourier_sum == 0 or np.isnan(fourier_sum):
            return 0, 0, 0  # or handle this case however you want

        # find the indices of the frequencies in the right bands
        idx_bass = np.where(frequencies < BASS_MAX)[0]
        idx_vocals = np.where((frequencies >= BASS_MAX) & (frequencies < VOCAL_MAX))[0]
        idx_instruments = np.where((frequencies >= VOCAL_MAX) & (frequencies < INSTRUMENT_MAX))[0]

        # sum the intensities in each band and normalize
        red = int(fourier[idx_bass].sum() / fourier.sum() * 255)
        green = int(fourier[idx_vocals].sum() / fourier.sum() * 255)
        blue = int(fourier[idx_instruments].sum() / fourier.sum() * 255)

        return red, green, blue


async def test_audio():
    loop = asyncio.get_event_loop()
    audio = Audio()
    audio.open()

    while True:
        audio_data = await loop.run_in_executor(None, audio.get_audio)
        print(Audio.audio_to_rgb(audio_data))
        await asyncio.sleep(0.1)


if __name__ == '__main__':
    asyncio.run(test_audio())
