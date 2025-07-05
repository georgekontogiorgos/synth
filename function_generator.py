from PyQt5 import uic, QtWidgets, QtCore
import sys
import time
from numpy import sin, pi
import sounddevice as sd


class GeneratorThread(QtCore.QThread):
    new_output = QtCore.pyqtSignal(float)

    def __init__(self, get_frequency, get_gain):
        super().__init__()
        self.get_frequency = get_frequency
        self.get_gain = get_gain
        self._running = True

    def run(self):
        t = 0
        dt = 1e-6
        while self._running:
            freq = self.get_frequency()
            gain = self.get_gain()
            output = gain * sin(2 * pi * freq * t)
            self.new_output.emit(output)
            t += dt
            time.sleep(dt)

    def stop(self):
        self._running = False
        self.wait()


class FunctionGenerator(QtWidgets.QMainWindow):  # Changed to QMainWindow
    def __init__(self):
        super().__init__()

        self.frequency = 1
        self.gain = 1
        self.thread = None

        uic.loadUi("function_generator.ui", self)

        self.dial_gain.valueChanged.connect(self.on_gain_changed)
        self.dial_freq.valueChanged.connect(self.on_freq_changed)
        self.on_button.stateChanged.connect(self.on_on_off_changed)

    def on_gain_changed(self, value):
        self.gain = value
        self.lcd_gain.display(value)

    def on_freq_changed(self, value):
        self.frequency = value
        self.lcd_freq.display(value)

    def on_on_off_changed(self, state):
        if self.on_button.isChecked():
            self.thread = GeneratorThread(
                get_frequency=lambda: self.frequency,
                get_gain=lambda: self.gain,
            )
            self.thread.new_output.connect(self.handle_output)
            self.thread.start()
            print("Generator output ON")
        else:
            if self.thread:
                self.thread.stop()
                self.thread = None
            print("Generator output OFF")

    def handle_output(self, value):
        print(f"Output: {value}")


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = FunctionGenerator()
    window.show()
    sys.exit(app.exec_())
