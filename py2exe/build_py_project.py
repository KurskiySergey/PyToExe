import os, re
import subprocess
import importlib
import shutil
import sys
from config import *
execute = importlib.import_module('execute')

# PROJECT_DIR = os.path.dirname(__file__)
# PROJECT_CURRENT_DIR = os.path.curdir
# PYUIC_FOLDER = 'ui_to_py'
# START_FILENAME = "main.py"
# FINAL_PYPROJECT_FOLDER = "build_py"
# PY_ENCODING = "utf-8"


def write_start_execute():
    py_generator("main")


def uic_to_py():
    pyfiles_path = f"{PROJECT_CURRENT_DIR}/" + f"{PYUIC_FOLDER}/"
    os.mkdir(PYUIC_FOLDER)

    ui_filenames = find_ui_files()
    print(ui_filenames)
    for file in ui_filenames:
        python_command = "pyuic5 {}.ui -o {}.py".format(os.path.join(PROJECT_CURRENT_DIR, file), os.path.join(pyfiles_path, f"ui_{file}"))
        print(python_command)
        command_list = python_command.split(' ')
        result = subprocess.run(command_list, shell=True)
        print(result.returncode)


def find_pyqt_windows():
    
    py_files = find_py_files()
    pyqt_files = []
    uic_pattern = "^.*import uic.*$"
    
    imported_files = find_imported_files(py_files)
    
    for imp_file in imported_files:
        
        with open(f"{imp_file}.py", "r", encoding = PY_ENCODING) as file:
            lines = file.readlines()
            for line in lines:
                if re.search(uic_pattern, line):
                    pyqt_files.append(imp_file)
                    break
            
    return pyqt_files


def find_imported_files(py_files):
    
    imported_modules = find_imported_modules(START_FILENAME, py_files)
    imported_files = set(imported_modules)
    
    current_len = 0
    
    while len(imported_files) != current_len:
        tmp = []
        current_len = len(imported_files)
        for file in imported_modules:
            tmp += find_imported_modules(f"{file}.py", py_files)
          
        tmp = set(tmp)
        
        imported_modules = tmp
        imported_files.update(imported_modules)
    #print(imported_files)
    
    return imported_files


def find_imported_modules(filename, py_files):
    
    import_pattern = "^.* *import .+$"
    imported_modules = []
    
    with open(filename, "r", encoding = PY_ENCODING) as file:
        lines = file.readlines()
        
        for line in lines:
            if re.search(import_pattern, line):
                result = line.split(" ")
                
                if result[0] == "from":
                    if result[1] in py_files:
                        imported_modules.append(result[1])
                elif result[0] == "import":
                    for file in result[1:]:
                        if file[-1] == "," or file[-1] == "\n":
                            py_file = file[:-1]
                        else:
                            py_file = file
                        
                        if py_file in py_files:
                            imported_modules.append(py_file)
                    
    return imported_modules


def find_ui_files():
    ui_pattern = "^.*\.ui$"
    cwd = os.getcwd()
    list_dir = os.listdir(cwd)
    ui_filenames = []
    
    for list_el in list_dir:
        if re.search(ui_pattern, list_el):
            ui_filenames.append(list_el.split('.')[0])
            
    return ui_filenames


def find_py_files():
    py_pattern = "^.*\.py$"
    cwd = os.getcwd()
    list_dir = os.listdir(cwd)
    py_files = []
    
    for file in list_dir:
        if re.search(py_pattern, file):
            py_files.append(file[:-3])

    return py_files


def py_generator(pyui_form, class_link=None):
    filename = "execute.py"
    pyfile = f"ui_{pyui_form}.py"
    import_name = "ui"
    func_name = "setUi"
    ui_class = None
   
    ui_class = decode_ui_class(pyfile)

    with open(filename, 'w') as file:
        new_lines = []
        import_line = f"from {PYUIC_FOLDER} import ui_{pyui_form} as {import_name}\n"
        new_lines.append(import_line)
        ui = f"{import_name}.{ui_class}"
        
        #file.write(import_line)
        def_line = f"def {func_name}(class_link):\n"
        new_lines.append(def_line)
        #file.write(def_line)
        
        init_line = f"\tform = {ui}()\n"
        new_lines.append(init_line)
        #file.write(init_line)
        
        setup_line = "\tform.setupUi(class_link)\n"
        new_lines.append(setup_line)
        #file.write(setup_line)
        
        test_line = "\tprint(form.__dict__)\n"
        new_lines.append(test_line)
        #file.write(test_line)
        
        update_line = "\tclass_link.__dict__.update(form.__dict__)\n"
        new_lines.append(update_line)
        #file.write(update_line)
        
        return_line = "\treturn class_link\n"
        new_lines.append(return_line)
        #file.write(return_line)

        file.seek(0)
        file.writelines(new_lines)


def decode_ui_class(pyui_file):
    
    pattern = "Ui_*"
    ui_class = None
    with open(os.path.join(PYUIC_FOLDER, pyui_file), 'r' , encoding= PY_ENCODING) as pyui_file:
        lines = pyui_file.readlines()
        
        for line in lines:
            if re.search(pattern, line):
                ui_class = line.split(" ")[1].split("(")[0]
                print(ui_class)
                break
    
    return ui_class


def loadUi(ui_form, class_link):

    global execute
    print("class_dict_before")
    print(class_link.__dict__)
    print()
    pyfile = ui_form.split(".")[0]
    py_generator(pyfile, class_link)

    del sys.modules['execute']
    del execute
    execute = importlib.import_module('execute')
    upd_class = execute.setUi(class_link)
    print("class_dict_after")
    print(upd_class.__dict__)
    print()
    # os.remove("execute.py")


def create_project_folder():
    project_folder = PROJECT_CURRENT_DIR + "/" + FINAL_PYPROJECT_FOLDER
    try:
        os.mkdir(project_folder)
    except FileExistsError:
        for (path, dir_names, files) in os.walk(project_folder, False):
            for filename in files:
                os.remove(path + "/" + filename)
            for dir_name in dir_names:
                os.rmdir(path + "/" + dir_name)


def copy_work_files():
    cwd = os.getcwd()
    list_dir = os.listdir(cwd)
    #print(list_dir)
    for file in list_dir:
        if os.path.isfile(cwd + "/" + file):
            #print("file")
            shutil.copy(PROJECT_DIR + "/" + file, PROJECT_DIR + "/" + FINAL_PYPROJECT_FOLDER)


def change_to_project_directory():
    global PROJECT_CURRENT_DIR
    current_dir = PROJECT_CURRENT_DIR + "/" + FINAL_PYPROJECT_FOLDER
    os.chdir(current_dir)
    PROJECT_CURRENT_DIR = current_dir
    print(PROJECT_CURRENT_DIR)

def change_to_base_directory():
    global PROJECT_CURRENT_DIR
    os.chdir(PROJECT_DIR)
    PROJECT_CURRENT_DIR = PROJECT_DIR
    print(PROJECT_CURRENT_DIR)


def delete_ui_files(ui_files = None):
    
    if ui_files is None:
        ui_files = find_ui_files()
        
    for ui_file in ui_files:
        os.remove(f"{ui_file}.ui")


def change_ui_to_py():
    import_line = "from build_py_project import loadUi\n"
    uic_load_pattern = "^.*uic\.loadUi(.*)$"
    
    pyqt_windows = find_pyqt_windows()
    
    for pyqt_window in pyqt_windows:
        with open(f"{pyqt_window}.py", "r+", encoding = PY_ENCODING) as pyqt:
            lines = pyqt.readlines()
            lines.insert(0, import_line)
            for i, line in enumerate(lines):
                if re.search(uic_load_pattern, line):
                    print(line)
                    ui_form = line.split("(")[1].split(",")[0]
                    tab = line.split("u")[0]
                    print(tab)
                    print(ui_form)
                    lines[i] = f"{tab}loadUi({ui_form}, self)\n"
            pyqt.seek(0)
            pyqt.writelines(lines)
                    
    print(pyqt_windows)


def create_execute_file():
    filename = "execute.py"
    pyfile = f"main.py"
    import_name = "ui"
    func_name = "setUi"
    ui_class = None

    ui_class = decode_ui_class(pyfile)

    with open(filename, 'w') as file:
        import_line = f"from {PYUIC_FOLDER} import main as {import_name}\n"
        ui = f"{import_name}.{ui_class}"
        file.write(import_line)

        def_line = f"def {func_name}(class_link):\n"
        file.write(def_line)

        init_line = f"\tform = {ui}()\n"
        file.write(init_line)

        setup_line = "\tform.setupUi(class_link)\n"
        file.write(setup_line)

        test_line = "\tprint(form.__dict__)\n"
        file.write(test_line)

        update_line = "\tclass_link.__dict__.update(form.__dict__)\n"
        file.write(update_line)

        return_line = "\treturn class_link\n"
        file.write(return_line)


def start_build():

    change_to_base_directory()
    create_project_folder()
    copy_work_files()
    change_to_project_directory()
    uic_to_py()
    delete_ui_files()
    change_ui_to_py()
    change_to_base_directory()


if __name__ == "__main__":
    start_build()
    


