import os


def get_local_file(file):
    return os.path.join(os.path.split(__file__)[0], file)
