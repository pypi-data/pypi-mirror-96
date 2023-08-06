"""
record.py

Stream the default input device and save to wav file.
Supports specifying backend, device, sample rate, block size.

Requires soundfile
    pip3 install soundfile

http://pysoundfile.readthedocs.io/
"""
import argparse
import time

import soundfile as sf
from pysoundio import (
    PySoundIo,
    SoundIoFormatFloat32LE,
)


class Record:

    def __init__(self, outfile, backend=None, input_device=None,
                 sample_rate=None, block_size=None, channels=None):
        self.wav_file = sf.SoundFile(
            outfile, mode='w', channels=channels,
            samplerate=sample_rate
        )
        self.pysoundio = PySoundIo(backend=backend)
        self.pysoundio.start_input_stream(
            device_id=input_device,
            channels=channels,
            sample_rate=sample_rate,
            block_size=block_size,
            dtype=SoundIoFormatFloat32LE,
            read_callback=self.callback
        )

    def close(self):
        self.pysoundio.close()
        self.wav_file.close()

    def callback(self, data, length):
        self.wav_file.buffer_write(data, dtype='float32')


def get_args():
    parser = argparse.ArgumentParser(
        description='PySoundIo audio record example',
        epilog='Stream the input device and save to wav file'
    )
    parser.add_argument('outfile', help='WAV output file name')
    parser.add_argument('--backend', type=int, help='Backend to use (optional)')
    parser.add_argument('--blocksize', type=int, default=4096, help='Block size (optional)')
    parser.add_argument('--rate', type=int, default=44100, help='Sample rate (optional)')
    parser.add_argument('--channels', type=int, default=1, help='Mono or stereo (optional)')
    parser.add_argument('--device', type=int, help='Input device id (optional)')
    args = parser.parse_args()
    return args


def main():
    args = get_args()
    record = Record(args.outfile, args.backend, args.device, args.rate, args.blocksize, args.channels)
    print('Recording...')
    print('CTRL-C to exit')

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('Exiting...')

    record.close()


if __name__ == '__main__':
    main()
