from PyQt6.QtCore import QRect, QSize, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QTextCursor
from PyQt6.QtWidgets import QPlainTextEdit, QWidget
from app.themes import THEMES


class Gutter(QWidget):
    def __init__(self, editor: 'TextEditor') -> None:
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self) -> QSize:
        return QSize(self.editor.gutter_width(), 0)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.fillRect(event.rect(), QColor(self.editor.colors['surface']))
        painter.setPen(QColor(self.editor.colors['muted']))
        block = self.editor.firstVisibleBlock()
        while block.isValid():
            top = int(self.editor.blockBoundingGeometry(block).translated(self.editor.contentOffset()).top())
            height = int(self.editor.blockBoundingRect(block).height())
            if top > event.rect().bottom():
                break
            if block.isVisible() and top + height >= event.rect().top():
                painter.drawText(0, top, self.width() - 6, height,
                                 Qt.AlignmentFlag.AlignRight, str(block.blockNumber() + 1))
            block = block.next()


class TextEditor(QPlainTextEdit):
    clicked = pyqtSignal(int)
    def __init__(self) -> None:
        super().__init__()
        self.colors = THEMES['dark']
        self.gutter = Gutter(self)
        self.blockCountChanged.connect(self.update_margin)
        self.updateRequest.connect(lambda *_: self.gutter.update())
        self.update_margin()
        self.markers = []

    def set_theme(self, colors):
        self.colors = colors
        self.update_margin()
        rect = self.contentsRect()
        self.gutter.setGeometry(QRect(rect.left(), rect.top(), self.gutter_width(), rect.height()))
        self.gutter.update()
        self.viewport().update()

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            point = event.position().toPoint()
            for position, color in self.markers:
                cursor = QTextCursor(self.document())
                cursor.setPosition(position)
                rect = self.cursorRect(cursor)
                if rect.adjusted(-4, 0, 4, 0).contains(point):
                    self.clicked.emit(position)
                    return
            self.clicked.emit(self.cursorForPosition(point).position())

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self.viewport())
        for position, color in self.markers:
            cursor = QTextCursor(self.document())
            cursor.setPosition(position)
            rect = self.cursorRect(cursor)
            painter.setPen(QColor(color))
            painter.drawLine(rect.topLeft(), rect.bottomLeft())

    def gutter_width(self) -> int:
        return 14 + self.fontMetrics().horizontalAdvance('9') * len(str(self.blockCount()))

    def update_margin(self) -> None:
        self.setViewportMargins(self.gutter_width(), 0, 0, 0)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        rect = self.contentsRect()
        self.gutter.setGeometry(QRect(rect.left(), rect.top(), self.gutter_width(), rect.height()))
