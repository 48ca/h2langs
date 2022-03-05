import wave
import contextlib

LANGUAGES = {
        'de': 'German',
        'en': 'English',
        'es': 'Spanish',
        'fr': 'French',
        'it': 'Italian',
        'jp': 'Japanese',
        'kr': 'Korean',
        'zh': 'Chinese',
}

class SoundFile:
    def __init__(self, filename, gd):
        self.level = gd['level']
        self.index = int(gd['index'], 10)
        self.speaker = gd['speaker']
        self.variant = gd['variant']
        with contextlib.closing(wave.open(filename, 'rb')) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            self.duration = frames / rate

    def apply_correction(self, correction):
        self.duration *= correction

class MissionLang:
    def __init__(self):
        self._extra_files = []
        self.files = {} # Dict[int, Set[SoundFile]]

    def add_file(self, fle: SoundFile):
        if fle.index not in self.files:
            self.files[fle.index] = set()
        self.files[fle.index].add(fle)

    def get_indices(self):
        return self.files.keys()

    def matches(self, other) -> bool:
        return self.get_indices() == other.get_indices()

    def __repr__(self):
        return str(self)
    def __str__(self):
        return "<MissionLang: files: {}>".format(len(self.files))


class Mission:
    def __init__(self, id):
        self.languages = {} # Dict[str, MissionLang]
        self._name = id.name
        self._level = id.level

    def add_language(self, code, m_lang):
        if code in self.languages:
            raise RuntimeError(
                    'Tried to add two languages with the same code: {} to {}'.format(
                        code, self._name))
        self.languages[code] = m_lang

    def check_matching(self) -> bool:
        if len(self.languages) < 2:
            return True
        ordered_languages = list(self.languages.values())
        check_m_lang = ordered_languages[0]
        for m_lang in ordered_languages[1:]:
            if not m_lang.matches(check_m_lang):
                return False
        return True

    def __repr__(self):
        return str(self)
    def __str__(self):
        return "<Mission: {}, langs: {}>".format(self._name, self.languages)
