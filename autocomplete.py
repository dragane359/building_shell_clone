import sys
import readline
import os
from app import Trie
import logging

def make_completer(executives_trie, cwd_files_hm):
    last_text = None
    tab_press_count = 0
    def completer(text, state):
        exec_bol = True
        line_buffer = readline.get_line_buffer()
        # "command ", "command xx/d"
        if ' ' in line_buffer.strip() or line_buffer.endswith(' '):
            exec_bol = False
            if '/' in text:
                sub_path, _, text = text.rpartition('/')
                cwd = os.path.join(os.getcwd(), sub_path)

            else:
                sub_path = ''
                cwd = os.getcwd()
            filenames = os.listdir(cwd)
            filepaths_trie = Trie.Trie()
            filepaths_root = filepaths_trie.root
            for filename in filenames:
                filepaths_trie.add_word(filepaths_root, filename, 0)
            cwd_files_hm[cwd] = filepaths_trie
            search_trie = cwd_files_hm[cwd]
        else:
            search_trie = executives_trie
        nonlocal last_text, tab_press_count
        if text != last_text:
            tab_press_count = 0
            last_text = text
        trie_root = search_trie.root
        if text in ('', ' '):
            all_word_options = filenames
        if search_trie.check_prefix_in_trie(trie_root, text, 0):
            all_word_options = sorted(search_trie.get_words_start_with_wrapper(text))
            all_word_options_str = ''
            for word in all_word_options:
                end_symbol = ' '
                if not exec_bol:
                    if '.' not in word:
                        # directory
                        end_symbol = '/ '
                all_word_options_str += f'{word}{end_symbol}'
            all_word_options_str = all_word_options_str[:-1]
        if len(all_word_options) == 0:
            sys.stdout.write("\x07")
            sys.stdout.flush()
        elif len(all_word_options) > 1:
            prefix = search_trie.get_lcp(search_trie.root, text)
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
                if not exec_bol:
                    if '.' not in all_word_options[state]:
                        # directory
                        end_symbol = '/'
                    return os.path.join(sub_path, all_word_options[state]) + end_symbol
                else:
                    # command
                    return all_word_options[state] + end_symbol
        return None
    
    return completer