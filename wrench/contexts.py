import contextlib, os, shutil, sys, tempfile

from six import StringIO

# =============================================================================
# Context Managers
# =============================================================================

@contextlib.contextmanager
def replaced_directory(dirname):
    """This ``Context Manager`` is used to move the contents of a directory
    elsewhere temporarily and put them back upon exit.  This allows testing
    code to use the same file directories as normal code without fear of
    damage.

    The name of the temporary directory which contains your files is yielded.

    :param dirname:
        Path name of the directory to be replaced.


    Example:

    .. code-block:: python

        with replaced_directory('/foo/bar/') as rd:
            # "/foo/bar/" has been moved & renamed
            with open('/foo/bar/thing.txt', 'w') as f:
                f.write('stuff')
                f.close()


        # got here? => "/foo/bar/ is now restored and temp has been wiped, 
        # "thing.txt" is gone
    """
    if dirname[-1] == '/':
        dirname = dirname[:-1]

    full_path = os.path.abspath(dirname)
    if not os.path.isdir(full_path):
        raise AttributeError('dir_name must be a directory')

    base, name = os.path.split(full_path)

    # create a temporary directory, move provided dir into it and recreate the
    # directory for the user
    tempdir = tempfile.mkdtemp()
    shutil.move(full_path, tempdir)
    os.mkdir(full_path)
    try:
        yield tempdir

    finally:
        # done context, undo everything
        shutil.rmtree(full_path)
        moved = os.path.join(tempdir, name)
        shutil.move(moved, base)
        shutil.rmtree(tempdir)


@contextlib.contextmanager
def temp_directory():
    """This ``Context Manager`` creates a temporary directory and yields its
    path.  Upon exit the directory is removed.

    Example:

    .. code-block:: python

        with temp_directory() as td:
            filename = os.path.join(td, 'foo.txt')
            with open(filename, 'w') as f:
                f.write('stuff')

        # got here? => td is now gone, foo.txt is gone too
    """
    tempdir = tempfile.mkdtemp()
    try:
        yield tempdir
    finally:
        shutil.rmtree(tempdir)


@contextlib.contextmanager
def temp_file():
    """This ``Context Manager`` creates a temporary file which is readable and
    writable by the current user and yields its path.  Once the ``Context``
    exits, the file is removed.

    Example:

    .. code-block:: python

        with temp_file() as filename:
            with open(filename, 'w') as f:
                f.write('stuff')
                
        # got here? => file called "filename" is now gone
    """
    _, filename = tempfile.mkstemp()
    try:
        yield filename
    finally:
        os.remove(filename)


@contextlib.contextmanager
def capture_stdout():
    """This ``Context Manager`` redirects STDOUT to a ``StringIO`` objects
    which is returned from the ``Context``.  On exit STDOUT is restored.

    Example:

    .. code-block:: python

        with capture_stdout() as capture:
            print('foo')

        # got here? => capture.getvalue() will now have "foo\\n"
    """
    stdout = sys.stdout
    try:
        capture_out = StringIO()
        sys.stdout = capture_out
        yield capture_out
    finally:
        sys.stdout = stdout


@contextlib.contextmanager
def capture_stderr():
    """This ``Context Manager`` redirects STDERR to a ``StringIO`` objects
    which is returned from the ``Context``.  On exit STDERR is restored.

    Example:

    .. code-block:: python

        with capture_stderr() as capture:
            print('foo')

        # got here? => capture.getvalue() will now have "foo\\n"
    """
    stderr = sys.stderr
    try:
        capture_out = StringIO()
        sys.stderr = capture_out
        yield capture_out
    finally:
        sys.stderr = stderr
