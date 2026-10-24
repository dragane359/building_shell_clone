import sys
import os
import subprocess
from pathlib import Path
import shlex
from app import Trie
import readline
from app.autocomplete import make_completer

def parse_text(arg, get_exec_bool = False):
    i = 0
    res = ''
    while i <= len(arg) - 1:
        if arg[i] == "'":
            temp = ''
            i += 1
            while i <= len(arg) - 1 and arg[i] != "'":
                temp += arg[i]
                i += 1
            if get_exec_bool:
                return temp
            res += temp
            i += 1
        elif arg[i] == '"':
            temp = ''
            i += 1
            while i <= len(arg) - 1 and arg[i] != '"':
                if arg[i] == '\\' and arg[i + 1] in ('"', '\\', '$', '`'):
                    i += 1
                temp += arg[i]
                i += 1
            if get_exec_bool:
                return temp
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
            if get_exec_bool:
                return temp
            res += temp
    return res

def process_stdout_stderr_output_file(output, action, out_file, error = None):
    # out_file_has_content = os.path.exists(out_file) and os.path.getsize(out_file) > 0
    if action == ' 2>> ':
        if len(output) > 0:
            sys.stdout.write(output)
        with open(out_file, "a", encoding="utf-8") as f:
            if error:
                f.write(error)
    elif action in (' 1>> ', ' >> '):
        if error:
            sys.stdout.write(error)
        with open(out_file, "a", encoding="utf-8") as f:
            if output:
                f.write(output)
    elif action == ' 2> ':
        sys.stdout.write(output)
        if output:
            if not output.endswith('\n'):
                sys.stdout.write('\n')
        with open(out_file, "w", encoding="utf-8") as f:
            if error:
                f.write(error)
    elif action in (' 1> ', ' > '):
        if error:
            sys.stdout.write(error)
        if error:
            if not error.endswith('\n'):
                sys.stdout.write('\n')
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(output)


def eval_command(command, executives_trie):
    out_file, action = None, None
    for act_opt in [' 2>> ', ' 1>> ', ' >> ', ' 2> ', ' 1> ', ' > ']:
        if act_opt in command:
            left = command.split(act_opt)[0]
            out_file = command.split(act_opt)[1]
            command = left
            action = act_opt
            break
    exec_name = parse_text(command, True)
    if exec_name == 'cat':
        args = shlex.split(command)
        result = subprocess.run(
            args, 
            capture_output=True, 
            text=True
        )
        output = result.stdout
        error = result.stderr
        if action:
            process_stdout_stderr_output_file(output, action, out_file, error)
        else:
            sys.stdout.write(result.stdout)
            if not result.stdout.endswith('\n'):
                sys.stdout.write("\n")

    elif exec_name == 'echo':
        arg = command[5:]
        res = parse_text(arg)
        if not res.endswith('\n'):
            res += '\n'
        if action:
            process_stdout_stderr_output_file(res, action, out_file)
        else:
            sys.stdout.write(res)
    elif exec_name == 'type':
        if command.split(' ')[1] in ('echo', 'type', 'exit', 'pwd', 'cd'):
            sys.stdout.write(f'{command.split(' ')[1]} is a shell builtin')
            sys.stdout.write("\n")

        else:
            found = False
            path_dirs = os.environ['PATH'].split(os.pathsep)
            for path in path_dirs:
                if not os.path.exists(path):
                    continue
                files_in_path = os.listdir(path)
                for file in files_in_path:
                    full_file_path = os.path.join(path, file)
                    if file == command.split(' ')[1] and os.access(full_file_path, os.X_OK):
                        sys.stdout.write(f'{command.split(' ')[1]} is {full_file_path}')
                        sys.stdout.write("\n")
                        found = True
                        break
            if not found:
                sys.stdout.write(f'{command.split(' ')[1]}: not found')
                sys.stdout.write("\n")

    elif exec_name == 'pwd':
        sys.stdout.write(os.getcwd()) 
        if not os.getcwd().endswith('\n'):
            sys.stdout.write("\n")

    elif exec_name == 'cd':
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
            sys.stdout.write("\n")
    else:
        found = False
        if not command.startswith(exec_name):
            command = command[1:]
        command = command[len(exec_name):]
        
        args = command.split(' ')[1:] if len(command.split(' ')) > 1 else []
        args = [arg for arg in args if arg]
        path_dirs = os.environ['PATH'].split(os.pathsep)
        for path in path_dirs:
            if not os.path.exists(path):
                continue
            files_in_path = os.listdir(path)
            for file in files_in_path:
                full_file_path = os.path.join(path, file)
                if file == exec_name and os.access(full_file_path, os.X_OK):
                    result = subprocess.run(
                        [exec_name] + args, 
                        capture_output=True, 
                        text=True
                    )
                    output = result.stdout
                    error = result.stderr
                    if action:
                        process_stdout_stderr_output_file(output, action, out_file, error)
                    else:
                        if result.stdout:
                            sys.stdout.write(result.stdout)
                    # subprocess.run([exec_name] + args, cwd = path)
                    found = True
                    break
            if found:
                return
        if not found:
            sys.stdout.write(f'{exec_name}: not found')
            sys.stdout.write("\n")

    # sys.stdout.flush()

def get_exec_list():
    path_dirs = os.environ['PATH'].split(os.pathsep)
    all_execs_list = []
    for path in path_dirs:
        if not os.path.exists(path):
            continue
        files_in_path = os.listdir(path)
        for file in files_in_path:
            full_file_path = os.path.join(path, file)
            if os.access(full_file_path, os.X_OK):
                all_execs_list.append(file)
    return all_execs_list

def main():
    
    executives_trie = Trie.Trie()
    trie_root = executives_trie.root
    # to handle tab
    readline.set_completer(make_completer(executives_trie))
    readline.parse_and_bind('tab: complete')
    # Add execs to trie
    words = ['echo', 'exit']
    words.extend(get_exec_list())
    for word in words:
        executives_trie.add_word(trie_root, word, 0)
    while True:
        sys.stdout.write("$ ")
        command = input()
        if command == 'exit':
            break
        eval_command(command, executives_trie)

if __name__ == "__main__":
    main()
