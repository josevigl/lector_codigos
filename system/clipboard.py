import ctypes
import time
from ctypes import wintypes


CF_UNICODETEXT = 13
GMEM_MOVEABLE = 0x0002

_user32 = ctypes.WinDLL("user32", use_last_error=True)
_kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

_user32.OpenClipboard.argtypes = [wintypes.HWND]
_user32.OpenClipboard.restype = wintypes.BOOL
_user32.EmptyClipboard.argtypes = []
_user32.EmptyClipboard.restype = wintypes.BOOL
_user32.SetClipboardData.argtypes = [wintypes.UINT, wintypes.HANDLE]
_user32.SetClipboardData.restype = wintypes.HANDLE
_user32.CloseClipboard.argtypes = []
_user32.CloseClipboard.restype = wintypes.BOOL

_kernel32.GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]
_kernel32.GlobalAlloc.restype = wintypes.HANDLE
_kernel32.GlobalLock.argtypes = [wintypes.HANDLE]
_kernel32.GlobalLock.restype = ctypes.c_void_p
_kernel32.GlobalUnlock.argtypes = [wintypes.HANDLE]
_kernel32.GlobalUnlock.restype = wintypes.BOOL
_kernel32.GlobalFree.argtypes = [wintypes.HANDLE]
_kernel32.GlobalFree.restype = wintypes.HANDLE


def copy_text(text):
    if not isinstance(text, str) or not text:
        raise ValueError("El texto del portapapeles debe ser una cadena no vacía.")
    encoded = ctypes.create_unicode_buffer(text)
    allocation_size = ctypes.sizeof(encoded)
    memory = _kernel32.GlobalAlloc(GMEM_MOVEABLE, allocation_size)
    if not memory:
        raise ctypes.WinError(ctypes.get_last_error())

    try:
        pointer = _kernel32.GlobalLock(memory)
        if not pointer:
            raise ctypes.WinError(ctypes.get_last_error())
        try:
            ctypes.memmove(pointer, encoded, allocation_size)
        finally:
            _kernel32.GlobalUnlock(memory)

        deadline = time.monotonic() + 1.0
        while not _user32.OpenClipboard(None):
            if time.monotonic() >= deadline:
                raise ctypes.WinError(ctypes.get_last_error())
            time.sleep(0.005)

        try:
            if not _user32.EmptyClipboard():
                raise ctypes.WinError(ctypes.get_last_error())
            if not _user32.SetClipboardData(CF_UNICODETEXT, memory):
                raise ctypes.WinError(ctypes.get_last_error())
            memory = None
        finally:
            _user32.CloseClipboard()
    finally:
        if memory:
            _kernel32.GlobalFree(memory)
