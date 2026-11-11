from bisect import bisect_right


class Positions:
    """One code-point/UTF-16 map per document revision."""
    def __init__(self, text: str):
        self.offsets = [0]
        for char in text:
            self.offsets.append(self.offsets[-1] + (2 if ord(char) > 0xffff else 1))

    def qt(self, index: int) -> int:
        return self.offsets[max(0, min(index, len(self.offsets) - 1))]

    def python(self, position: int) -> int:
        return max(0, bisect_right(self.offsets, position) - 1)
