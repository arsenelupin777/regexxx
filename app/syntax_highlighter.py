from PyQt6.QtGui import QColor, QSyntaxHighlighter, QTextCharFormat
from app.pattern_lexer import tokens
from app.positions import Positions
from app.themes import THEMES

class PatternHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.flags = 0
        self.cached_key = None
        self.cached_tokens = []
        self.colors = THEMES['dark']

    def set_theme(self, colors):
        self.colors = colors
        self.rehighlight()

    def highlightBlock(self, text):
        source = self.document().toPlainText()
        key = (source, self.flags)
        if key != self.cached_key:
            positions = Positions(source)
            self.cached_tokens = [(positions.qt(a), positions.qt(b), kind) for a, b, kind in tokens(source, self.flags)]
            self.cached_key = key
        start = self.currentBlock().position()
        end = start + len(text.encode('utf-16-le')) // 2
        colors = self.colors
        for a, b, kind in self.cached_tokens:
            if a < end and b > start:
                format_ = QTextCharFormat()
                format_.setForeground(QColor(colors[kind]))
                self.setFormat(max(a,start)-start, min(b,end)-max(a,start), format_)
