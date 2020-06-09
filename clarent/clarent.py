from textblob.sentiments import PatternAnalyzer


class Clarent(object):

    def __init__(self, text: str):
        self.text = str(text)
        self.subjectivity = Clarent.get_subjectivity(text)

    @staticmethod
    def get_subjectivity(line: str) -> float:
        return PatternAnalyzer().analyze(line)[1]

    @property
    def objectivity(self) -> float:
        return float(1 - self.subjectivity)
