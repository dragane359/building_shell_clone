import sys

def make_completer(executives_trie):
    last_text = None
    tab_press_count = 0
    def completer(text, state):
        nonlocal last_text, tab_press_count
        if text != last_text:
            tab_press_count = 0
            last_text = text
        trie_root = executives_trie.root
        if executives_trie.check_prefix_in_trie(trie_root, text, 0):
            all_word_options = sorted(executives_trie.get_words_start_with_wrapper(text))
            all_word_options_str = ''
            for word in all_word_options:
                all_word_options_str += f'{word}  '
                all_word_options_str = all_word_options_str[:-2]
        if len(all_word_options) > 1:
            prefix = executives_trie.get_lcp(executives_trie.root, text)
            if prefix != text:
                if state == 0:
                    if len(executives_trie.get_words_start_with_wrapper(prefix)) > 1:
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
                    sys.stdout.write("$ " + text)
                    sys.stdout.flush()
                return None
        else:
            # Readline calls this function with state = 0, 1, 2... 
            # to cycle through the options. Return the option at 'state', or None if out of bounds.
            if state < len(all_word_options):
                return all_word_options[state] + ' '
        
        return None
    
    return completer