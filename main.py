import sys
import os
import subprocess
from pathlib import Path

def parse_text_for_cat_no_quotes(arg):
    res = []
    i = 0
    while i <= len(arg) - 1:
        temp = ""
        while i <= len(arg) - 1 and arg[i] != ' ':
            if arg[i] == "'":
                i += 1
                while i <= len(arg) - 1 and arg[i] != "'":
                    if arg[i] == '\\':
                        temp += '\\\\'
                    else:
                        temp += arg[i]
                    i += 1
                i += 1
            else:
                if arg[i] == '\\':
                    temp += '\\\\'
                else:
                    temp += arg[i]
                i += 1
        i += 1
        res.append(temp)
    return res

def parse_text_for_cat(arg):
    # print(arg) 
    i = 0
    res = []
    while i <= len(arg) - 1:
        while i <= len(arg) - 1 and arg[i] not in ("'", '"'):
            i += 1
        if arg[i] in("'", '"'):
            char = arg[i]
            temp = ''
            i += 1
            while i <= len(arg) - 1 and arg[i] != char:
                if arg[i] == "\\":
                    i += 1
                if i <= len(arg) - 1:
                    temp += arg[i]
                i += 1
            res.append(temp)
            i += 1
    return res

def parse_text(arg):
    i = 0
    res = ''
    while i <= len(arg) - 1:
        if arg[i] == "'":
            temp = ''
            i += 1
            while i <= len(arg) - 1 and arg[i] != "'":
                temp += arg[i]
                i += 1
            res += temp
            i += 1
        elif arg[i] == '"':
            temp = ''
            i += 1
            while i <= len(arg) - 1 and arg[i] != '"':
                if arg[i] == '\\' and arg[i + 1] in ('"', '\\', '$', '`'):
                    i += 1
                    temp += arg[i]
            res += temp
            i += 1
        elif arg[i] == ' ':
            while i <= len(arg) - 1 and arg[i] == ' ':
                i += 1
            res += ' '
        else:
            temp = ''
            while i <= len(arg) - 1 and arg[i] not in ("'", '"', " "):
                if arg[i] == '\\':
                    i += 1
                if i <= len(arg) - 1:
                    temp += arg[i]
                i += 1
            res += temp
    return res

def eval_command(command):
    if command.split(' ')[0] == 'cat':
        arg = command[4:]

        # print(arg)
        res = parse_text_for_cat_no_quotes(arg)
        # print(res)

        result = subprocess.run(["cat"] + res, capture_output = True, text = True, check = True)
        sys.stdout.write(result.stdout) 
        return

    if command.split(' ')[0] == 'echo':
        arg = command[5:]
        res = parse_text(arg)
        sys.stdout.write(res)
    elif command.split(' ')[0] == 'type':
        if command.split(' ')[1] in ('echo', 'type', 'exit', 'pwd', 'cd'):
            sys.stdout.write(f'{command.split(' ')[1]} is a shell builtin')
        else:
            found = False
            exec_to_search = command.split(' ')[1]
            path_dirs = os.environ['PATH'].split(os.pathsep)
            for path in path_dirs:
                if not os.path.exists(path):
                    continue
                files_in_path = os.listdir(path)
                for file in files_in_path:
                    full_file_path = os.path.join(path, file)
                    if file == exec_to_search and os.access(full_file_path, os.X_OK):
                        sys.stdout.write(f'{exec_to_search} is {full_file_path}')
                        found = True
                        break
            if not found:
                sys.stdout.write(f'{command.split(' ')[1]}: not found')
    elif command.split(' ')[0] == 'pwd':
        sys.stdout.write(os.getcwd()) 
    elif command.split(' ')[0] == 'cd':
        new_dir = command.split(' ')[1]
        if new_dir == '~':
            home_path = os.environ['HOME']
            os.chdir(home_path)
            return
        elif os.path.exists(new_dir):
            os.chdir(new_dir)
            return
        else:
            sys.stdout.write(f'cd: {new_dir}: No such file or directory')
    else:
        found = False
        exec_to_search = command.split(' ')[0]
        args = command.split(' ')[1:] if len(command.split(' ')) > 1 else []
        path_dirs = os.environ['PATH'].split(os.pathsep)
        for path in path_dirs:
            if not os.path.exists(path):
                continue
            files_in_path = os.listdir(path)
            for file in files_in_path:
                full_file_path = os.path.join(path, file)
                if file == exec_to_search and os.access(full_file_path, os.X_OK):
                    subprocess.run(command.split(' '), cwd = path)
                    found = True
                    break
            if found:
                return
        if not found:
            sys.stdout.write(f'{command.split(' ')[0]}: not found')
    sys.stdout.write("\n")

def main():
    # TODO: Uncomment the code below to pass the first stage
    while True:
        sys.stdout.write("$ ")
        command = input()
        if command == 'exit':
            break
        eval_command(command)

if __name__ == "__main__":
    main()
