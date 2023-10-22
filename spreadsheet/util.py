import regex

def format_frames(frames: int) -> str:
    prefix = ""
    if frames == 0:
        prefix = " "
    elif frames > 0:
        prefix = "+"
    return f"{prefix}{frames}f"


_delta_time: float = 0.017
_re_chapter_time1: regex.Pattern = regex.compile(r"(?:ChapterTime|FileTime)\:\s*(\d+):(\d+):(\d+)\.(\d+)") # "ChapterTime: 1:00:40.562"
_re_chapter_time2: regex.Pattern = regex.compile(r"(?:ChapterTime|FileTime)\:\s*(\d+):(\d+)\.(\d+)")       # "ChapterTime: 6:40.562"
_re_chapter_time3: regex.Pattern = regex.compile(r"(?:ChapterTime|FileTime)\:\s*(\d+)\.(\d+)")             # "ChapterTime: 40.562"
_re_time_comment1: regex.Pattern = regex.compile(r"#\s*(\d+):(\d+):(\d+)\.(\d+)")                          # "#1:00:40.562"
_re_time_comment2: regex.Pattern = regex.compile(r"#\s*(\d+):(\d+)\.(\d+)")                                # "#6:40.562"
_re_time_comment3: regex.Pattern = regex.compile(r"#\s*(\d+)\.(\d+)")                                      # "#40.562"

class ChapterTime:
    def __init__(self, hours: int, minutes: int, seconds: int, millis: int, frames: int, negative=False):
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds
        self.millis = millis
        self.frames = frames
        self.negative = negative
        
    def __str__(self):
        prefix = "-" if self.negative else ""
        if self.hours != 0:
            return f"{prefix}{str(self.hours)}:{str(self.minutes).zfill(2)}:{str(self.seconds).zfill(2)}.{str(self.millis).zfill(3)}({self.frames})"
        else:
            return f"{prefix}{str(self.minutes)}:{str(self.seconds).zfill(2)}.{str(self.millis).zfill(3)}({self.frames})"

    def __repr__(self):
        return str(self)

    @staticmethod
    def parse(text: str):
        m = _re_chapter_time1.match(text)
        if not m:
            m = _re_time_comment1.match(text)

        hours: int = None
        minutes: int = None
        seconds: int = None
        millis: int = None

        if m:
            hours = int(m.group(1))
            minutes = int(m.group(2))
            seconds = int(m.group(3))
            millis = int(m.group(4))
        else:
            m = _re_chapter_time2.match(text)
        if not m:
            m = _re_time_comment2.match(text)

        if m:
            minutes = int(m.group(1))
            seconds = int(m.group(2))
            millis = int(m.group(3))
        else:
            m = _re_chapter_time3.match(text)
        if not m:
            m = _re_time_comment3.match(text)

        if m:
            seconds = int(m.group(2))
            millis = int(m.group(3))
        else:
            return None

        if hours is None:
            hours = 0
        if minutes is None:
            minutes = 0

        frames = round((millis * 0.001 + seconds + minutes * 60 + hours * 3600) / _delta_time)
        return ChapterTime(hours, minutes, seconds, millis, frames)
    
    @staticmethod
    def from_frames(frames: int):
        seconds_millis = abs(frames) * 0.017
        millis = round((seconds_millis - int(seconds_millis)) * 1000)
        seconds = int(seconds_millis)
        minutes = int(seconds / 60)
        hours = int(minutes / 60)
        seconds = seconds % 60
        minutes = minutes % 60

        return ChapterTime(hours, minutes, seconds, millis, abs(frames), negative=frames < 0)

