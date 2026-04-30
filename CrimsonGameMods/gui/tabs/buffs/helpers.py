import os
import subprocess
from PySide6.QtWidgets import QFrame, QPushButton

try:
    from gui.utils import make_help_btn
except Exception:
    def make_help_btn(guide_key: str, show_guide_fn) -> QPushButton:
        btn = QPushButton("?")
        btn.setFixedSize(22, 22)
        if show_guide_fn:
            btn.clicked.connect(lambda: show_guide_fn(guide_key))
        return btn

def _can_write_game_dir(game_path: str) -> bool:
    try:
        _t = os.path.join(game_path, ".se_write_test")
        with open(_t, "w") as _f:
            _f.write("t")
        os.remove(_t)
        return True
    except Exception:
        return False


def _is_game_running() -> bool:
    try:
        out = subprocess.check_output(
            ["tasklist", "/FI", "IMAGENAME eq CrimsonDesert.exe", "/FO", "CSV", "/NH"],
            stderr=subprocess.DEVNULL, text=True, timeout=3,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        return "CrimsonDesert.exe" in out
    except Exception:
        return False

def _ui_add_line(shadow=False) -> QFrame:
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    if shadow:
        line.setFrameShadow(QFrame.Shadow.Sunken)
    return line