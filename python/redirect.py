def redirect_std():
    from contextlib import contextmanager
    import ctypes
    import io
    import os
    import sys
    import tempfile

    import ctypes.util
    import platform

    if platform.system() == "Linux":
        libc = ctypes.CDLL(None)
        c_stdout = ctypes.c_void_p.in_dll(libc, 'stdout')
    if platform.system() == "Windows":
        class FILE(ctypes.Structure):
            _fields_ = [
                ("_ptr", ctypes.c_char_p),
                ("_cnt", ctypes.c_int),
                ("_base", ctypes.c_char_p),
                ("_flag", ctypes.c_int),
                ("_file", ctypes.c_int),
                ("_charbuf", ctypes.c_int),
                ("_bufsize", ctypes.c_int),
                ("_tmpfname", ctypes.c_char_p),
            ]

        # Gives you the name of the library that you should really use (and then load through ctypes.CDLL
        #msvcrt = CDLL(ctypes.util.find_msvcrt())
        if sys.version_info < (3, 5):
            msvcrt = ctypes.CDLL(ctypes.util.find_library('c'))
        else:
            if hasattr(sys, 'gettotalrefcount'): # debug build
                msvcrt = ctypes.CDLL('ucrtbased')
            else:
                msvcrt = ctypes.CDLL('api-ms-win-crt-stdio-l1-1-0')

        libc = msvcrt # libc was used in the original example in _redirect_stdout()

        iob_func = msvcrt.__acrt_iob_func
        iob_func.restype = ctypes.POINTER(FILE)
        iob_func.argtypes = []

        array = iob_func()

        s_stdin = ctypes.addressof(array[0])
        c_stdout = ctypes.addressof(array[1])


    @contextmanager
    def stdout_redirector(stream):
        # The original fd stdout points to. Usually 1 on POSIX systems.
        original_stdout_fd = sys.stdout.fileno()

        def _redirect_stdout(to_fd):
            """Redirect stdout to the given file descriptor."""
            # Flush the C-level buffer stdout
            libc.fflush(c_stdout)
            # Flush and close sys.stdout - also closes the file descriptor (fd)
            sys.stdout.close()
            # Make original_stdout_fd point to the same file as to_fd
            os.dup2(to_fd, original_stdout_fd)
            # Create a new sys.stdout that points to the redirected fd
            sys.stdout = io.TextIOWrapper(os.fdopen(original_stdout_fd, 'wb'))

        # Save a copy of the original stdout fd in saved_stdout_fd
        saved_stdout_fd = os.dup(original_stdout_fd)
        try:
            # Create a temporary file and redirect stdout to it
            tfile = tempfile.TemporaryFile(mode='w+b')
            _redirect_stdout(tfile.fileno())
            # Yield to caller, then redirect stdout back to the saved fd
            yield
            _redirect_stdout(saved_stdout_fd)
            # Copy contents of temporary file to the given stream
            tfile.flush()
            tfile.seek(0, io.SEEK_SET)
            stream.write(tfile.read())
        finally:
            tfile.close()
            os.close(saved_stdout_fd)
