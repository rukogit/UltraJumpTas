import regex

def format_frames(frames: int) -> str:
    prefix = ""
    if frames == 0:
        prefix = " "
    elif frames > 0:
        prefix = "+"
    return f"{prefix}{frames}f"


_delta_time: float = 0.017
_re_chapter_time: regex.Pattern = regex.compile(r"(?:ChapterTime|FileTime)\:\s*(\d+):(\d+)\.(\d+)") # "ChapterTime: 0:40.562"

class ChapterTime:
    def __init__(self, minutes: int, seconds: int, millis: int, frames: int):
        self.minutes = minutes
        self.seconds = seconds
        self.millis = millis
        self.frames = frames

    def __str__(self):
        return f"{str(self.minutes)}:{str(self.seconds).zfill(2)}.{str(self.millis).zfill(3)}({self.frames})"

    def __repr__(self):
        return str(self)

    @staticmethod
    def parse(text: str):
        m = _re_chapter_time.match(text)

        if not m:
            return None
        
        minutes = int(m.group(1))
        seconds = int(m.group(2))
        millis = int(m.group(3))
        frames = round((millis * 0.001 + seconds + minutes * 60) / _delta_time)

        return ChapterTime(minutes, seconds, millis, frames)
    
    @staticmethod
    def from_frames(frames: int):
        seconds_millis = frames * 0.017
        millis = round((seconds_millis - int(seconds_millis)) * 1000)
        seconds = int(seconds_millis)
        minutes = int(seconds / 60)
        seconds = seconds % 60

        return ChapterTime(minutes, seconds, millis, frames)

