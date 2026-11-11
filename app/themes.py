"""Shared colors for styles and custom editor painting."""
from pathlib import Path

THEMES = {
    'dark': dict(
        background='#101722', surface='#171e29', text='#d6deeb', muted='#98a8bc',
        border='#43536a', button='#243248', hover='#30445f', accent='#83b8ff',
        selected='#345478', disabled='#8492a5',
        match='#285465', group1='#51446c', group2='#365c48',
        group3='#634936', group4='#3b4969', active='#866329', marker='#ffcf60',
        error='#ff7b72', error_background='#663333',
        escape='#79c0ff', comment='#98a8bc', group='#d2a8ff',
        repeat='#ffa657', anchor='#7ee787', **{'class': '#a5d6ff'}),
    'light': dict(
        background='#f1f4f8', surface='#ffffff', text='#202d40', muted='#52647c',
        border='#8a9ab0', button='#e4eaf2', hover='#d3e2f5', accent='#175bb5',
        selected='#b6d5ff', disabled='#64748b',
        match='#c4e8ed', group1='#e3d5f5', group2='#d1ebd8',
        group3='#f3dfc9', group4='#d5e0f5', active='#f4d58a', marker='#805400',
        error='#b42318', error_background='#ffe0dc',
        escape='#075ca8', comment='#52647c', group='#7136a8',
        repeat='#954500', anchor='#236b35', **{'class': '#126479'}),
}


def stylesheet(colors):
    source = Path(__file__).with_name('styles.qss').read_text(encoding='utf-8')
    for name, color in colors.items():
        source = source.replace('@' + name + '@', color)
    return source
