import re
from app.themes import THEMES, stylesheet
from typing import Any

from PyQt6.QtCore import QTimer, Qt, QSignalBlocker
from PyQt6.QtGui import QColor, QTextCursor, QTextCharFormat, QShortcut, QKeySequence, QPalette
from PyQt6.QtWidgets import (QApplication, QMenu, QCheckBox, QDockWidget, QHBoxLayout, QButtonGroup,
                            QLabel, QMainWindow, QPlainTextEdit, QToolButton,
                            QSplitter, QTextEdit, QTreeWidget, QTreeWidgetItem,
                            QVBoxLayout, QWidget)
from app.editor import TextEditor
from app.regex_engine import MAX_PATTERN, MAX_TEXT
from app.syntax_highlighter import PatternHighlighter
from app.cheat_sheet import CHEAT_SHEET
from app.controller import Controller
from app.positions import Positions


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle('Regexxx · Python re')
        self.resize(1100, 760)
        self.setMinimumSize(640, 480)
        self.controller = Controller(self)
        self.controller.finished.connect(self.render)
        self.positions = Positions('')
        self.results = []
        self.error_position = None
        self.evaluation_status = ''
        self.base_selections = []
        self.theme_name = 'dark'
        self.colors = THEMES[self.theme_name]
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        pattern_header = QHBoxLayout()
        pattern_header.addWidget(QLabel('Expresión regular · Python re'), 1)
        self.theme_button = QToolButton()
        self.theme_button.clicked.connect(self.toggle_theme)
        self.theme_button.setToolTip('Alternar entre tema claro y oscuro')
        pattern_header.addWidget(self.theme_button)
        self.guide_button = QToolButton()
        self.guide_button.setText('?')
        self.guide_button.setToolTip('Guía rápida · Ayuda local')
        self.guide_button.setAccessibleName('Mostrar Guía rápida')
        self.guide_button.setCheckable(True)
        pattern_header.addWidget(self.guide_button)
        layout.addLayout(pattern_header)
        self.pattern = QPlainTextEdit()
        self.pattern.setFixedHeight(65)
        self.highlighter = PatternHighlighter(self.pattern.document())
        layout.addWidget(self.pattern)
        controls = QHBoxLayout()
        self.mode_group = QButtonGroup(self)
        self.mode_buttons = {}
        for operation, label in [('match', 'Coincidencias'), ('substitution', 'Sustitución')]:
            button = QToolButton()
            button.setText(label)
            button.setCheckable(True)
            self.mode_group.addButton(button)
            self.mode_buttons[operation] = button
            controls.addWidget(button)
        self.mode_buttons['match'].setChecked(True)
        self.mode_group.buttonClicked.connect(self.mode_changed)
        self.flags = {}
        flag_labels = dict(IGNORECASE='i', MULTILINE='m', DOTALL='s', VERBOSE='x', ASCII='a')
        for name in ('IGNORECASE', 'MULTILINE', 'DOTALL', 'VERBOSE', 'ASCII'):
            box = QCheckBox(flag_labels[name])
            box.setToolTip(f're.{name}')
            box.setAccessibleName(name)
            self.flags[name] = box
            box.setChecked(name == 'MULTILINE')
            controls.addWidget(box)
            box.toggled.connect(self.flags_changed)
        self.status = QLabel('')
        self.status.setWordWrap(True)
        self.status.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        controls.addWidget(self.status, 1)
        self.locate_error = QToolButton()
        self.locate_error.setText('Localizar error')
        self.locate_error.hide()
        self.locate_error.clicked.connect(self.jump_error)
        controls.addWidget(self.locate_error)
        self.info_button = QToolButton()
        self.info_button.setText('Grupos')
        self.info_button.setToolTip('Mostrar u ocultar Detalle de coincidencias')
        self.info_button.setCheckable(True)
        self.info_button.setChecked(True)
        controls.addWidget(self.info_button)
        layout.addLayout(controls)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        self.editors = QSplitter(Qt.Orientation.Vertical)
        original_panel = QWidget()
        original_layout = QVBoxLayout(original_panel)
        original_layout.setContentsMargins(0, 0, 0, 0)
        original_layout.addWidget(QLabel('Texto de prueba'))
        self.text = TextEditor()
        original_layout.addWidget(self.text)
        self.editors.addWidget(original_panel)
        self.substitution_panel = QWidget()
        substitution_layout = QVBoxLayout(self.substitution_panel)
        substitution_layout.setContentsMargins(0, 0, 0, 0)
        substitution_layout.addWidget(QLabel('Sustitución'))
        self.replacement = QPlainTextEdit()
        self.replacement.setAccessibleName('Sustitución')
        self.replacement.setFixedHeight(65)
        substitution_layout.addWidget(self.replacement)
        result_header = QHBoxLayout()
        result_header.addWidget(QLabel('Resultado'), 1)
        self.copy_result = QToolButton()
        self.copy_result.setText('Copiar')
        self.copy_result.setToolTip('Copiar el resultado completo')
        self.copy_result.setEnabled(False)
        self.copy_result.clicked.connect(self.copy_output)
        result_header.addWidget(self.copy_result)
        substitution_layout.addLayout(result_header)
        self.output = TextEditor()
        self.output.setAccessibleName('Resultado')
        self.output.setReadOnly(True)
        self.preview_text = None
        substitution_layout.addWidget(self.output)
        self.editors.addWidget(self.substitution_panel)
        self.editors.setChildrenCollapsible(False)
        self.substitution_panel.hide()
        left_layout.addWidget(self.editors)
        self.info_panel = QWidget()
        right_layout = QVBoxLayout(self.info_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.addWidget(QLabel('Detalle de coincidencias'))
        self.matches = QTreeWidget()
        self.matches.setHeaderLabels(['Elemento', 'Texto / valor', 'span()'])
        right_layout.addWidget(self.matches)
        self.splitter.addWidget(left)
        self.splitter.addWidget(self.info_panel)
        self.splitter.setCollapsible(0, False)
        self.splitter.setCollapsible(1, False)
        self.splitter.setStretchFactor(0, 3)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setSizes([780, 320])
        layout.addWidget(self.splitter, 1)
        self.info_button.toggled.connect(self.info_panel.setVisible)
        self.guide = QDockWidget('Guía rápida', self)
        self.guide.setObjectName('cheatSheet')
        self.guide.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetClosable)
        guide_text = QPlainTextEdit()
        guide_text.setReadOnly(True)
        guide_text.setPlainText(CHEAT_SHEET)
        self.guide.setWidget(guide_text)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.guide)
        self.guide.hide()
        self.guide_button.toggled.connect(self.guide.setVisible)
        self.guide.visibilityChanged.connect(self.guide_button.setChecked)
        self.setCentralWidget(container)
        self.debounce = QTimer(self)
        self.debounce.setSingleShot(True)
        self.debounce.setInterval(200)
        self.debounce.timeout.connect(self.execute)
        self.pattern.textChanged.connect(self.schedule)
        self.text.textChanged.connect(self.schedule)
        self.replacement.textChanged.connect(self.schedule)
        self.matches.itemSelectionChanged.connect(self.select_match)
        self.matches.itemExpanded.connect(self.expand_groups)
        self.matches.itemActivated.connect(self.locate_match)
        self.matches.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.matches.customContextMenuRequested.connect(self.copy_menu)
        self.text.clicked.connect(self.select_at)
        for key, direction in [('F3', 1), ('Shift+F3', -1)]:
            shortcut = QShortcut(QKeySequence(key), self)
            shortcut.activated.connect(lambda d=direction: self.navigate(d))
        self.highlighter.flags = self.current_flags()
        for label in self.findChildren(QLabel):
            if label is not self.status:
                label.setProperty('section', True)
        for panel in (left_layout, original_layout, substitution_layout, right_layout):
            panel.setSpacing(8)
        self.pattern.setAccessibleName('Expresión regular')
        self.text.setAccessibleName('Texto de prueba')
        self.apply_theme()

    def toggle_theme(self):
        self.apply_theme('light' if self.theme_name == 'dark' else 'dark')

    def apply_theme(self, name=None):
        # Rehighlighting can emit textChanged even though the text is unchanged.
        blockers = [QSignalBlocker(editor) for editor in
                    (self.pattern, self.replacement, self.text, self.output)]
        previous = self.colors
        self.theme_name = name or self.theme_name
        self.colors = THEMES[self.theme_name]
        mapping = {value: self.colors[key] for key, value in previous.items()}

        def recolor(selections):
            for selection in selections:
                fmt = selection.format
                for prop in (QTextCharFormat.Property.BackgroundBrush,
                             QTextCharFormat.Property.TextUnderlineColor):
                    if fmt.hasProperty(prop):
                        color = (fmt.background().color() if prop == QTextCharFormat.Property.BackgroundBrush
                                 else fmt.underlineColor())
                        replacement = QColor(mapping.get(color.name(), color.name()))
                        if prop == QTextCharFormat.Property.BackgroundBrush:
                            fmt.setBackground(replacement)
                        else:
                            fmt.setUnderlineColor(replacement)
                selection.format = fmt
            return selections

        # Repaint existing decorations without rebuilding results or submitting work.
        for editor in (self.pattern, self.replacement, self.text, self.output):
            editor.setExtraSelections(recolor(editor.extraSelections()))
        recolor(self.base_selections)
        self.text.markers = [(pos, mapping.get(color, color)) for pos, color in self.text.markers]
        self.base_markers = [(pos, mapping.get(color, color))
                             for pos, color in getattr(self, 'base_markers', [])]
        palette = QPalette(self.palette())
        for role, key in ((QPalette.ColorRole.Window, 'background'),
                          (QPalette.ColorRole.Base, 'surface'),
                          (QPalette.ColorRole.Text, 'text'),
                          (QPalette.ColorRole.WindowText, 'text'),
                          (QPalette.ColorRole.Button, 'button'),
                          (QPalette.ColorRole.ButtonText, 'text'),
                          (QPalette.ColorRole.Highlight, 'selected'),
                          (QPalette.ColorRole.HighlightedText, 'text')):
            palette.setColor(role, QColor(self.colors[key]))
        self.setPalette(palette)
        self.setStyleSheet(stylesheet(self.colors))
        self.text.set_theme(self.colors)
        self.output.set_theme(self.colors)
        self.highlighter.set_theme(self.colors)
        label = 'oscuro' if self.theme_name == 'dark' else 'claro'
        self.theme_button.setText(f'Tema: {label}')
        self.theme_button.setAccessibleName(f'Tema: {label}. Alternar tema')
        del blockers

    def current_operation(self):
        return 'substitution' if self.mode_buttons['substitution'].isChecked() else 'match'

    def mode_changed(self):
        substitution = self.current_operation() == 'substitution'
        self.substitution_panel.setVisible(substitution)
        if substitution:
            self.editors.setSizes([300, 300])
        self.schedule()
        self.debounce.stop()
        self.execute()

    def copy_output(self):
        if self.preview_text is not None:
            QApplication.clipboard().setText(self.preview_text)

    def clear_preview(self):
        self.preview_text = None
        self.output.clear()
        self.copy_result.setEnabled(False)

    def flags_changed(self):
        self.highlighter.flags = self.current_flags()
        self.highlighter.rehighlight()
        self.schedule()
        self.debounce.stop()
        self.execute()

    def current_flags(self):
        flags = 0
        for name, box in self.flags.items():
            if box.isChecked():
                flags |= getattr(re, name)
        return int(flags)

    def schedule(self) -> None:
        self.controller.cancel()
        self.matches.clear()
        self.results = []
        self.base_selections = []
        self.text.markers = []
        self.text.viewport().update()
        self.text.setExtraSelections([])
        self.pattern.setExtraSelections([])
        self.replacement.setExtraSelections([])
        self.clear_preview()
        self.locate_error.hide()
        self.error_position = None
        self.status.setText('Pendiente…')
        self.debounce.start()

    def execute(self) -> None:
        self.positions = Positions(self.text.toPlainText())
        self.status.setText('Evaluando…')
        request = dict(pattern=self.pattern.toPlainText(), text=self.text.toPlainText(),
                       flags=self.current_flags(), operation=self.current_operation(),
                       replacement=self.replacement.toPlainText())
        if len(request['pattern']) > MAX_PATTERN or len(request['text']) > MAX_TEXT:
            self.render(dict(state='limit', error='Límite: 4 000 caracteres de patrón y 100 000 de texto.', position=None))
            return
        self.controller.submit(request)

    def selection(self, span: tuple[int, int], color: str) -> QTextEdit.ExtraSelection:
        start, end = span
        selection = QTextEdit.ExtraSelection()
        cursor = QTextCursor(self.text.document())
        cursor.setPosition(self.positions.qt(start))
        cursor.setPosition(self.positions.qt(end), QTextCursor.MoveMode.KeepAnchor)
        selection.cursor = cursor
        selection.format.setBackground(QColor(color))
        return selection

    def render(self, result: dict[str, Any]) -> None:
        self.clear_preview()
        self.pattern.setExtraSelections([])
        self.replacement.setExtraSelections([])
        self.error_position = None
        self.locate_error.hide()
        self.matches.clear()
        self.base_selections = []
        self.results = result.get('matches', [])
        self.positions = Positions(self.text.toPlainText())
        self.text.markers = []
        if 'error' in result:
            self.status.setText(result['error'])
            position = result.get('position')
            if position is not None:
                self.error_editor = self.replacement if result.get('error_source') == 'replacement' else self.pattern
                self.error_position = Positions(self.error_editor.toPlainText()).qt(position)
                self.status.setText(self.status.text() + f" · posición {position}, línea {result.get('line')}, columna {result.get('column')}")
                cursor = QTextCursor(self.error_editor.document())
                cursor.setPosition(self.error_position)
                cursor.movePosition(QTextCursor.MoveOperation.NextCharacter, QTextCursor.MoveMode.KeepAnchor)
                mark = QTextEdit.ExtraSelection()
                mark.cursor = cursor
                mark.format.setUnderlineStyle(QTextCharFormat.UnderlineStyle.WaveUnderline)
                mark.format.setUnderlineColor(QColor(self.colors['error']))
                if not cursor.hasSelection():
                    mark.format.setBackground(QColor(self.colors['error_background']))
                    mark.format.setProperty(QTextCharFormat.Property.FullWidthSelection, True)
                self.error_editor.setExtraSelections([mark])
                self.locate_error.show()
        else:
            count = '500 visibles; hay más' if result.get('truncated') else f'{len(self.results)} coincidencias'
            self.status.setText(f're.finditer() · {count}')
            if not self.results:
                self.status.setText('Sin coincidencias · Se busca en todo el texto, incluidos sus saltos de línea.')
                if self.flags['MULTILINE'].isChecked():
                    self.status.setText(self.status.text() + ' MULTILINE modifica ^ y $; no divide el texto en cadenas.')
            if self.current_operation() == 'substitution' and result.get('output') is not None:
                self.preview_text = result['output']
                self.output.setPlainText(self.preview_text)
                self.copy_result.setEnabled(True)
                self.status.setText(f"{result['substitution_count']} sustituciones · {count}")
        for index, match in enumerate(self.results):
            empty = match['span'][0] == match['span'][1]
            item = QTreeWidgetItem(self.matches, [str(index + 1) + (' ∅' if empty else ''), repr(match['text']), str(tuple(match['span']))])
            item.setData(0, Qt.ItemDataRole.UserRole, match['span'])
            item.setData(0, Qt.ItemDataRole.UserRole + 1, match['text'])
            item.setData(0, Qt.ItemDataRole.UserRole + 2, index)
            if match['groups']:
                item.setChildIndicatorPolicy(QTreeWidgetItem.ChildIndicatorPolicy.ShowIndicator)
            for span, color in [(match['span'], self.colors['match'])] + [(g['span'], self.group_color(g['number'])) for g in match['groups'] if g['span'][0] >= 0]:
                if span[0] == span[1]:
                    self.text.markers.append((self.positions.qt(span[0]), color))
                else:
                    self.base_selections.append(self.selection(span, color))
        self.evaluation_status = self.status.text()
        self.base_markers = list(self.text.markers)
        self.text.setExtraSelections(self.base_selections)
        self.text.viewport().update()

    def group_color(self, number):
        return self.colors[f'group{(number - 1) % 4 + 1}']

    def expand_groups(self, item):
        if item.parent() is not None or item.childCount():
            return
        index = item.data(0, Qt.ItemDataRole.UserRole + 2)
        for group in self.results[index]['groups']:
            child = QTreeWidgetItem(item, [f"Grupo {group['number']} {group['name'] or ''}", repr(group['text']), str(tuple(group['span']))])
            if group['span'][0] >= 0:
                child.setData(0, Qt.ItemDataRole.UserRole, group['span'])
            child.setData(0, Qt.ItemDataRole.UserRole + 1, group['text'])

    def select_match(self) -> None:
        item = self.matches.currentItem()
        span = item.data(0, Qt.ItemDataRole.UserRole) if item else None
        self.text.setExtraSelections(self.base_selections + ([self.selection(span, self.colors['active'])] if span and span[0] != span[1] else []))
        self.text.markers = list(getattr(self, 'base_markers', []))
        if span and span[0] == span[1]:
            self.text.markers.append((self.positions.qt(span[0]), self.colors['marker']))
        self.text.viewport().update()
        if item:
            root = item.parent() or item
            self.status.setText(self.evaluation_status + f' · {self.matches.indexOfTopLevelItem(root) + 1} de {len(self.results)} visibles')

    def locate_match(self, *args):
        item = self.matches.currentItem()
        span = item.data(0, Qt.ItemDataRole.UserRole) if item else None
        if span:
            cursor = QTextCursor(self.text.document())
            cursor.setPosition(self.positions.qt(span[0]))
            self.text.setTextCursor(cursor)
            self.text.ensureCursorVisible()

    def navigate(self, direction):
        if not self.results:
            return
        item = self.matches.currentItem()
        index = self.matches.indexOfTopLevelItem(item.parent() or item) if item else (-1 if direction > 0 else 0)
        self.matches.setCurrentItem(self.matches.topLevelItem((index + direction) % len(self.results)))
        self.locate_match()

    def select_at(self, position):
        position = self.positions.python(position)
        for index, match in enumerate(self.results):
            start, end = match['span']
            if start == end == position or start <= position < end:
                self.matches.setCurrentItem(self.matches.topLevelItem(index))
                return

    def copy_menu(self, point):
        item = self.matches.itemAt(point)
        if item is None:
            return
        text = item.data(0, Qt.ItemDataRole.UserRole + 1)
        menu = QMenu(self)
        action = menu.addAction('Copiar texto exacto')
        action.setEnabled(text is not None)
        if menu.exec(self.matches.viewport().mapToGlobal(point)) == action:
            QApplication.clipboard().setText(text)

    def jump_error(self):
        if self.error_position is not None:
            cursor = QTextCursor(self.error_editor.document())
            cursor.setPosition(self.error_position)
            self.error_editor.setTextCursor(cursor)
            self.error_editor.ensureCursorVisible()
            self.error_editor.setFocus()

    def closeEvent(self, event) -> None:
        self.debounce.stop()
        self.controller.close()
        event.accept()
