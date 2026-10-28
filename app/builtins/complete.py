import sys

def handle(command, complete_builtin_hm):
    arr = []
    i = 0
    while i <= len(command) - 1:
        curr_str = ''
        while i <= len(command) - 1 and command[i] != ' ':
            curr_str += command[i]
            i += 1
        i += 1
        if curr_str:
            arr.append(curr_str)
    if arr[1] == '-p':
        completer_command = arr[2]
        if completer_command in complete_builtin_hm:
            path = complete_builtin_hm[completer_command]
            sys.stdout.write(f'complete -C \'{path}\' {completer_command}')
        else:
            sys.stdout.write(f'complete: {arr[2]}: no completion specification')
        sys.stdout.write('\n')
    elif arr[1] == '-C':
        path = arr[2]
        completer_command = arr[3]
        complete_builtin_hm[completer_command] = path
    elif arr[1] == '-r':
        completer_command = arr[2]
        if completer_command in complete_builtin_hm:
            del complete_builtin_hm[completer_command]
