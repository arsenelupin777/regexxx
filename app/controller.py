import json
import sys
from pathlib import Path
from PyQt6.QtCore import QObject, QProcess, QTimer, pyqtSignal


class Controller(QObject):
    """Qt's asynchronous pipes never wait for process I/O on the GUI thread."""
    finished = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.revision = 0
        self.process = None
        self.busy = False
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.setInterval(2000)
        self.timer.timeout.connect(self.timeout)

    def cancel(self):
        self.revision += 1
        self.timer.stop()
        if self.busy:
            self.dispose()
        self.busy = False

    def dispose(self):
        process = self.process
        self.process = None
        if process:
            process.kill()
            # Keep ownership until the asynchronous exit; no waitForFinished.
            process.finished.connect(process.deleteLater)
            if process.state() == QProcess.ProcessState.NotRunning:
                process.deleteLater()

    def submit(self, request):
        self.cancel()
        revision = self.revision
        if self.process is None:
            process = QProcess(self)
            process.setWorkingDirectory(str(Path(__file__).resolve().parent.parent))
            process.setProgram(sys.executable)
            process.setArguments(['-u', '-m', 'app.worker_process'])
            self.process = process
            process.readyReadStandardOutput.connect(lambda: self.read(process))
            process.errorOccurred.connect(lambda _: self.failed(process))
            process.finished.connect(lambda *_: self.failed(process))
            process.start()
        self.busy = True
        self.process.write((json.dumps(dict(revision=revision, input=request)) + '\n').encode('utf-8'))
        self.timer.start()

    def read(self, process):
        while process.canReadLine():
            message = json.loads(bytes(process.readLine()))
            if process is self.process and self.busy and message['revision'] == self.revision:
                self.busy = False
                self.timer.stop()
                self.finished.emit(message['result'])

    def failed(self, process):
        if process is self.process:
            self.dispose()
            if self.busy:
                self.busy = False
                self.timer.stop()
                self.finished.emit(dict(state='worker_error', error='El trabajador se interrumpió.', position=None))

    def timeout(self):
        self.cancel()
        self.finished.emit(dict(state='timeout', error='Tiempo agotado (2 s). Reduce el texto o modifica el patrón.', position=None))

    def close(self):
        self.cancel()
        self.dispose()
