import os


def delete(filename):
    try:
        os.remove(filename)
    except OSError:
        pass
