# TODO: Remove this file once we no longer support a version of Django
#       prior to 1.7.
#
# This is Django 1.6.11's django/core/files/locks.py.
#
# Copyright (c) Django Software Foundation and individual contributors.  All
# rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     1. Redistributions of source code must retain the above copyright notice,
#     this list of conditions and the following disclaimer.
#
#     2. Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#
#     3. Neither the name of Django nor the names of its contributors may be
#     used to endorse or promote products derived from this software without
#     specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
"""
Portable file locking utilities.

Based partially on an example by Jonathan Feignberg in the Python
Cookbook [1] (licensed under the Python Software License) and a ctypes port by
Anatoly Techtonik for Roundup [2] (license [3]).

[1] http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/65203
[2] http://sourceforge.net/p/roundup/code/ci/default/tree/roundup/backends/portalocker.py
[3] http://sourceforge.net/p/roundup/code/ci/default/tree/COPYING.txt
"""
import os

__all__ = ('LOCK_EX', 'LOCK_SH', 'LOCK_NB', 'lock', 'unlock')


def _fd(f):
    """Get a filedescriptor from something which could be a file or an fd."""
    return f.fileno() if hasattr(f, 'fileno') else f


if os.name == 'nt':
    import msvcrt
    from ctypes import (sizeof, c_ulong, c_void_p, c_int64,
                        Structure, Union, POINTER, windll, byref)
    from ctypes.wintypes import BOOL, DWORD, HANDLE

    LOCK_SH = 0  # the default
    LOCK_NB = 0x1  # LOCKFILE_FAIL_IMMEDIATELY
    LOCK_EX = 0x2  # LOCKFILE_EXCLUSIVE_LOCK

    # --- Adapted from the pyserial project ---
    # detect size of ULONG_PTR
    if sizeof(c_ulong) != sizeof(c_void_p):
        ULONG_PTR = c_int64
    else:
        ULONG_PTR = c_ulong
    PVOID = c_void_p

    # --- Union inside Structure by stackoverflow:3480240 ---
    class _OFFSET(Structure):
        _fields_ = [
            ('Offset', DWORD),
            ('OffsetHigh', DWORD)]

    class _OFFSET_UNION(Union):
        _anonymous_ = ['_offset']
        _fields_ = [
            ('_offset', _OFFSET),
            ('Pointer', PVOID)]

    class OVERLAPPED(Structure):
        _anonymous_ = ['_offset_union']
        _fields_ = [
            ('Internal', ULONG_PTR),
            ('InternalHigh', ULONG_PTR),
            ('_offset_union', _OFFSET_UNION),
            ('hEvent', HANDLE)]

    LPOVERLAPPED = POINTER(OVERLAPPED)

    # --- Define function prototypes for extra safety ---
    LockFileEx = windll.kernel32.LockFileEx
    LockFileEx.restype = BOOL
    LockFileEx.argtypes = [HANDLE, DWORD, DWORD, DWORD, DWORD, LPOVERLAPPED]
    UnlockFileEx = windll.kernel32.UnlockFileEx
    UnlockFileEx.restype = BOOL
    UnlockFileEx.argtypes = [HANDLE, DWORD, DWORD, DWORD, LPOVERLAPPED]

    def lock(f, flags):
        hfile = msvcrt.get_osfhandle(_fd(f))
        overlapped = OVERLAPPED()
        ret = LockFileEx(hfile, flags, 0, 0, 0xFFFF0000, byref(overlapped))
        return bool(ret)

    def unlock(f):
        hfile = msvcrt.get_osfhandle(_fd(f))
        overlapped = OVERLAPPED()
        ret = UnlockFileEx(hfile, 0, 0, 0xFFFF0000, byref(overlapped))
        return bool(ret)
else:
    try:
        import fcntl
        LOCK_SH = fcntl.LOCK_SH  # shared lock
        LOCK_NB = fcntl.LOCK_NB  # non-blocking
        LOCK_EX = fcntl.LOCK_EX
    except (ImportError, AttributeError):
        # File locking is not supported.
        LOCK_EX = LOCK_SH = LOCK_NB = 0

        # Dummy functions that don't do anything.
        def lock(f, flags):
            # File is not locked
            return False

        def unlock(f):
            # File is unlocked
            return True
    else:
        def lock(f, flags):
            ret = fcntl.flock(_fd(f), flags)
            return (ret == 0)

        def unlock(f):
            ret = fcntl.flock(_fd(f), fcntl.LOCK_UN)
            return (ret == 0)
