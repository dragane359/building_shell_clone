class TrieNode:
    def __init__(self, val):
        self.val = val
        self.children = {}


class Trie:
    def __init__(self):
        self.root = TrieNode('-1')
        self.triewords = []
        self.trie_startwith_words = []

    def add_word(self, node, word, word_idx):
        if word_idx > len(word) - 1:
            self.triewords.append(word)
            new_node = TrieNode('.')
            node.children['.'] = new_node
            return
        curr_char = word[word_idx]
        if curr_char in node.children:
            child_node = node.children[curr_char]
            self.add_word(child_node, word, word_idx + 1)
        else:
            new_node = TrieNode(curr_char)
            node.children[curr_char] = new_node
            self.add_word(new_node, word, word_idx + 1)

    def check_prefix_in_trie(self, node, word, word_idx):
        if word_idx > len(word) - 1:
            return True
        bol = False
        for child_char in node.children:
            child_node = node.children[child_char]
            if child_char == word[word_idx]:
                bol = bol or self.check_prefix_in_trie(child_node, word, word_idx + 1)
        return bol
    
    def check_word_in_trie(self, node, word, word_idx):
        if word_idx > len(word) - 1 and '.' in node.children:
            return True
        bol = False
        for child_char in node.children:
            child_node = node.children[child_char]
            if child_char == word[word_idx]:
                bol = bol or self.check_word_in_trie(child_node, word, word_idx + 1)
        return bol
    
    def get_words_start_with_wrapper(self, word):
        self.trie_startwith_words = []
        self.get_words_start_with(self.root, word, 0, '')
        return self.trie_startwith_words
    
    def get_words_start_with(self, node, word, word_idx, curr_str):
        if '.' in node.children and word_idx > len(word) - 1:
            self.trie_startwith_words.append(curr_str)
        if word_idx <= len(word) - 1:
            child_char = word[word_idx]
            child_node = node.children[child_char]
            self.get_words_start_with(child_node, word, word_idx +  1, curr_str + child_char)
        else:
            for child_char in node.children:
                child_node = node.children[child_char]
                self.get_words_start_with(child_node, word, word_idx + 1, curr_str + child_char)
    
    def get_node_where_prefix_ends(self, node, word, word_idx):
        if word_idx > len(word) - 1:
            return node
        curr_char = word[word_idx]
        if curr_char not in node.children:
            return None
        child_node = node.children[curr_char]
        return self.get_node_where_prefix_ends(child_node, word, word_idx + 1)
    
    def get_max_word_formed_with_singular_chain(self, node, prefix):
        eligible_length = len(node.children)
        if '.' in node.children:
            self.prefix = max(self.prefix, prefix)
            return
        elif eligible_length == 1:
            for child_char in node.children:
                if child_char != '.':
                    self.get_max_word_formed_with_singular_chain(node.children[child_char], prefix + child_char)
    
    def get_lcp(self, node, word):
        first_node = self.get_node_where_prefix_ends(node, word, 0)
        if first_node:
            self.prefix = word
            self.get_max_word_formed_with_singular_chain(first_node, word)
            # print(self.prefix, 'gegegew')
            return self.prefix
        else:
            return word





