from py2exe.build_py_project import start_build
from py2exe.convertation import start_convertation


def start():
    start_build()
    start_convertation()


if __name__ == "__main__":
    start()
