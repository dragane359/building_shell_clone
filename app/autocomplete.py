import sys
import readline
import os
from app import Trie
import logging
import subprocess
from pathlib import Path

def make_completer(executives_trie, cwd_files_hm, complete_builtins_hm):
    last_text = None
    tab_press_count = 0
    def completer(text, state):
        exec_bol = True
        completer_builtin_output = False
        line_buffer = readline.get_line_buffer()
        env_vars = os.environ.copy()
        env_vars["COMP_LINE"] = line_buffer
        env_vars["COMP_POINT"] = str(len(line_buffer.encode('utf-8')))
        # "command ", "command xx/d"
        if ' ' in line_buffer.strip() or line_buffer.endswith(' '):
            cwd = os.getcwd()
            sub_path = ''
            exec_bol = False
            arr = []
            i = 0
            while i <= len(line_buffer) - 1:
                curr_str = ''
                while i <= len(line_buffer) - 1 and line_buffer[i] != ' ':
                    curr_str += line_buffer[i]
                    i += 1
                i += 1
                if curr_str:
                    arr.append(curr_str)
            completer_command = arr[0]
            
            preceding_word = arr[-2] if len(arr) >= 2 else ''
            if completer_command in complete_builtins_hm:
                completer_path = complete_builtins_hm[completer_command]
                result = subprocess.run(
                    [completer_path] + [completer_command, text, preceding_word], 
                    env=env_vars,
                    capture_output=True,  # Capture stdout and stderr
                    text=True,            # Return output as a string instead of bytes
                    check=True            # Raise an error if the command fails (non-zero exit code)
                )
                # candidates = []
                candidates = result.stdout.split('\n')
                candidates = [i for i in candidates if i]
                # if result.stdout.rstrip():
                #     candidates = [result.stdout.rstrip()]
                completer_builtin_output = True
            else:
                if '/' in text:
                    sub_path, _, text = text.rpartition('/')
                    cwd = os.path.join(os.getcwd(), sub_path)
                candidates = os.listdir(cwd)
            candidates_trie = Trie.Trie()
            filepaths_root = candidates_trie.root
            for candidate in candidates:
                candidates_trie.add_word(filepaths_root, candidate, 0)
            cwd_files_hm[cwd] = candidates_trie
            search_trie = cwd_files_hm[cwd]
        else:
            search_trie = executives_trie
        nonlocal last_text, tab_press_count
        if text != last_text:
            tab_press_count = 0
            last_text = text
        trie_root = search_trie.root
        if text in ('', ' '):
            all_word_options = candidates
        if search_trie.check_prefix_in_trie(trie_root, text, 0):
            all_word_options = sorted(search_trie.get_words_start_with_wrapper(text))
            all_word_options_str = ''
            for word in all_word_options:
                end_symbol = ' '
                if not exec_bol:
                    if '.' not in word and not completer_builtin_output:
                        # directory
                        end_symbol = '/ '
                all_word_options_str += f'{word}{end_symbol}'
            all_word_options_str = all_word_options_str[:-1]
        # print('hh', all_word_options)
        if len(all_word_options) == 0:
            sys.stdout.write("\x07")
            sys.stdout.flush()
        elif len(all_word_options) > 1:
            prefix = search_trie.get_lcp(search_trie.root, text)
            # print('jjj', prefix, all_word_options, text)
            if prefix != text:
                if state == 0:
                    if len(search_trie.get_words_start_with_wrapper(prefix)) > 1:
                        return prefix
                    return prefix + ' '

            if tab_press_count == 0:
                tab_press_count += 1
                sys.stdout.write("\x07")
                sys.stdout.flush()
            else:
                if state == 0:
                    sys.stdout.write('\n')
                    sys.stdout.write(all_word_options_str)
                    sys.stdout.write('\n')
                    sys.stdout.write("$ " + line_buffer)
                    sys.stdout.flush()
                return None
        else:
            # Readline calls this function with state = 0, 1, 2... 
            # to cycle through the options. Return the option at 'state', or None if out of bounds.
            if state < len(all_word_options):
                # stat bee/, stat bee/ff/
                end_symbol = ' '
                if not completer_builtin_output and not exec_bol:
                    if '.' not in all_word_options[state]:
                        # directory
                        end_symbol = '/'
                    return os.path.join(sub_path, all_word_options[state]) + end_symbol
                else:
                    # command
                    return all_word_options[state] + end_symbol
        return None
    
    return completer