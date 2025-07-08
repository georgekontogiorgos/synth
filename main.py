from function_generator import FunctionGenerator

from PyQt5 import uic, QtWidgets, QtCore

from PyQt5.QtWidgets import QMainWindow

import sys
from numpy import sin, pi
import sounddevice as sd
import threading
import numpy as np
import sounddevice as sd
import soundfile as sf
import time
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s][%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

class MainPanel(QMainWindow):
    def __init__(self):
        super().__init__()

        uic.loadUi("main.ui", self)

        self.func_gen_button.clicked.connect(self.on_click_func_gen)
        self.rec_button.clicked.connect(self.on_click_rec)

        self.samplerate = sd.query_devices(None, 'output')['default_samplerate']

        self.generators = []
        self.generator_id_counter = 0

        self.output_filename = "output.wav"

        self.file = sf.SoundFile(self.output_filename, mode='w', samplerate=int(self.samplerate),
                channels=1, subtype='PCM_16')

        self.recording = True

        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self.consumer)
        self.thread.start()

    def closeEvent(self, event):
        self.stop_event.set()
        self.thread.join()
        event.accept()

    def _mix_audio(self, frames):
        try:
            if not self.generators:
                return np.zeros((frames, 1), dtype=np.float32)

            chunks = [gen.get_data(frames) for gen in self.generators]
            
            if not all(chunk.shape == chunks[0].shape for chunk in chunks):
                raise ValueError("Inconsistent chunk shapes from generators.")
            
            return np.sum(chunks, axis=0)

        except Exception as e:
            logging.exception("Error while mixing audio")
            return np.zeros((frames, 1), dtype=np.float32)

    def _callback(self, outdata, frames, time, status):
        if status:
            logging.error(f"Stream status: {status}")
        mixed = self._mix_audio(frames)
        outdata[:] = mixed
        if self.recording:
            try:
                self.file.write(mixed.copy())
            except Exception as e:
                logging.warning(f"Skipping file write: {e}")

    def consumer(self):

        logging.info("Starting audio stream with %d generators", len(self.generators))

        try:
            with sd.OutputStream(device=None, channels=1,
                                callback=self._callback,
                                samplerate=self.samplerate):
                while not self.stop_event.is_set():
                    time.sleep(0.1)
        finally:
            self.recording = False
            self.file.close()
            logging.info(f"Recording saved to {self.output_filename}")

    def on_click_rec(self):
        self.recording = True if self.rec_button.isChecked() else False

    def on_click_func_gen(self):
        generator = FunctionGenerator(self)
        self.generators.append(generator)
        generator.show()

    def remove_generator(self, target):
        try:
            self.generators.remove(target)
        except ValueError:
            logging.error(f"'{target}' not found in the list.")

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainPanel()
    window.show()
    sys.exit(app.exec_())
