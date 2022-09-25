import subprocess


def start_convertation():
    command_list = "auto-py-to-exe"
    subprocess.run(command_list, shell=True)


if __name__ == "__main__":
    start_convertation()