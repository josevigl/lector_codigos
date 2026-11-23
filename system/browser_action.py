import ctypes
import time


_user32 = ctypes.WinDLL("user32", use_last_error=True)
_user32.SetCursorPos.argtypes = [ctypes.c_int, ctypes.c_int]
_user32.SetCursorPos.restype = ctypes.c_int
_user32.mouse_event.argtypes = [
    ctypes.c_ulong,
    ctypes.c_ulong,
    ctypes.c_ulong,
    ctypes.c_ulong,
    ctypes.c_size_t,
]
_user32.keybd_event.argtypes = [
    ctypes.c_ubyte,
    ctypes.c_ubyte,
    ctypes.c_ulong,
    ctypes.c_size_t,
]

_MOUSEEVENTF_LEFTDOWN = 0x0002
_MOUSEEVENTF_LEFTUP = 0x0004
_KEYEVENTF_KEYUP = 0x0002
_VK_CONTROL = 0x11
_VK_A = 0x41
_VK_V = 0x56


def paste_and_continue(code_field, continue_button, page_wait_ms=250):
    if page_wait_ms < 0:
        raise ValueError("automation.page_wait_ms no puede ser negativo.")

    click_at(code_field)
    _press_control_key(_VK_A)
    _press_control_key(_VK_V)
    time.sleep(page_wait_ms / 1000)
    click_at(continue_button)


def click_at(point):
    if (
        not isinstance(point, (list, tuple))
        or len(point) != 2
        or not all(isinstance(value, int) for value in point)
        or any(value < 0 for value in point)
    ):
        raise ValueError("Las coordenadas de automatización deben ser [x, y] positivos.")

    if not _user32.SetCursorPos(point[0], point[1]):
        raise ctypes.WinError(ctypes.get_last_error())
    _user32.mouse_event(_MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    _user32.mouse_event(_MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)


def _press_control_key(key):
    _user32.keybd_event(_VK_CONTROL, 0, 0, 0)
    _user32.keybd_event(key, 0, 0, 0)
    _user32.keybd_event(key, 0, _KEYEVENTF_KEYUP, 0)
    _user32.keybd_event(_VK_CONTROL, 0, _KEYEVENTF_KEYUP, 0)
