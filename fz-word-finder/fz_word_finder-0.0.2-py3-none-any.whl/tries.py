'''
Copyright 2021 Rairye
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

from fz_word_finder.helpers import *

class node():
    
    def __init__(self, name):
        self.name = name
        self.children = {}
        self.word_end = False
        self.target_word = None
        
    def add_child(self, child):
            self.children[child] = node(child)

    def has_child(self, child):
            return child in self.children
        
    def has_children(self):
            return self.children != {}
        
    def get_name(self):
        return self.name


class trie():

    def __init__(self, target_words = None):
        self.trie_dict = {}
        if is_supported_target_word_type(target_words):
            for word in target_words:
                self.add(word)

        self.match_case = False
        self.ignore_ws = True
        self.ignore_punct = True
        self.use_punct_as_variant = False
        self.variants = {}

    def add_variants(self, variants):
        if not type(variants) == dict:
            return

        for key, value in variants.items():
            if key in self.variants:
                temp = variants[key]
                self.variants[key] += [str(element) for element in value if value not in temp] if type(value) == list else [str(value)]
            else:
                self.variants[str(key)] = [str(element) for element in value] if type(value) == list else [str(value)]    

    def clear_variants(self):
        self.variants = {}

    def clear_target_words(self):
        self.trie_dict = {}

    def get_variant_dict(self):
        return self.variants

    def delete_variant(variant):
        if type(variant) != str:
            return
        else:
            try:
                delete(self.variants[variant])
            except:
                pass

    def delete_variants(self, variants):
        if type(variants) == dict:
            for variant in variants:
                self.delete_variant(variant)
        else:
            if type(variants) == str:
                self.delete_variant(variant)


    def add_target_words(self, target_words):
        if is_supported_target_word_type(target_words):
            for word in target_words:
                self.add(word)
        else:
            self.add(word)

    def delete_target_words(self, target_words):
        if is_supported_target_word_type(target_words):
            for word in target_words:
                self.delete(word)
        else:
            self.delete(word)

    def set_match_case(self, value):
        if type(value) != bool:
            return
        else:
            self.match_case = value
        
    def set_use_punct_as_variant(self, value):
        if type(value) != bool:
            return
        else:
            self.use_punct_as_variant = value

    def set_ignore_punct_ws(self, value):
        if type(value) != bool:
            return
        else:
            self.ignore_ws = value
            self.ignore_punct = value

    def set_ignore_punct(self, value):
        if type(value) != bool:
            return
        else:
            self.ignore_punct = value

    def set_ignore_ws(self, value):
        if type(value) != bool:
            return
        else:
            self.ignore_ws = value

    def get_variants(self, char):

        variants = set(self.variants.get(char, []))

        if len(variants) > 0:
            sub_search = [variant for variant in variants if variant in self.variants and variant != char]
            
            while True:
                if len(sub_search) == 0:
                    break
                else:
                     current_variants = set([])
                     for variant in sub_search:
                         results = self.variants.get(variant, [])
                         if len(results) > 0:
                             for result in results:
                                 if result not in variants:
                                     current_variants.add(result)
                                 
                     sub_search = [variant for variant in current_variants if (variant != char and (variant in self.variants and not variant in variants))]
                     variants.update(current_variants)
                    
        return variants
        

    def add(self, word):

        if type (word) != str:
            return False
        
        word_len = len(word)
        
        if not word[0] in self.trie_dict:
            self.trie_dict[word[0]] = node(word[0])
        current_node = self.trie_dict[word[0]]

        if word_len == 1:
            current_node.word_end = True
            current_node.target_word = word
            return True

        i = 1

        while i < word_len - 1:           
            if not current_node.has_child(word[i]):
                current_node.add_child(word[i])
            current_node = current_node.children[word[i]]
            i+=1
        if not current_node.has_child(word[i]):
                current_node.add_child(word[i])
                
        current_node = current_node.children[word[i]]
        current_node.word_end = True
        current_node.target_word = word
        
        return True


    def delete(self, word):

        if type (word) != str:
            return False

        word_len = len(word)
        node_list = []
        
        if not word[0] in self.trie_dict:
            return False
        
        current_node = self.trie_dict[word[0]]
        if word_len == 1 and current_node.word_end:
            if not curent_node.has_children_():
                try:
                    del(trie_dict[word])
                except:
                    return False

            return True

        else:

            node_list.append(current_node)
            
            i = 1
            while i < word_len -1:
                if not current_node.has_child(word[i]):
                    return False

                current_node = current_node.children[word[i]]
                node_list.append(current_node)
                i+=1
                
            try:
                current_node = current_node.children[word[i]]
            except:   
                return False

            temp = [n.get_name() for n in node_list]
            temp.append(current_node.get_name())
            
            if current_node.word_end and not current_node.has_children():
                current_node.word_end = False
                current_node.target_word = None
                delete_last = None
                last_node = current_node.get_name()

                node_count = len(node_list)

                while node_count >= 0:
                    if current_node.word_end:
                        return True
                    
                    if delete_last == True:
                        try:
                            del(current_node.children[last_node])
                        except:
                            pass
                            
                    delete_last = True if  not current_node.has_children() else False
                    last_node = current_node.get_name()
                    node_count-=1
                    current_node = node_list[node_count]

            
                if delete_last == True:
                    try:
                        del(self.trie_dict[last_node])
                    except:
                        return False

                return True
                    
            elif current_node.word_end and current_node.has_children():
                current_node.word_end = False
                current_node.target_word = None
                return True
                
            else:
                
                return False
 
            return False


    def has_key(self, key, ss_len, search_nodes, srm):
        current_chars = set([])
        ss_len.reset()
        srm.reset()
        search_nodes.update([])
        
        if (self.use_punct_as_variant == True and is_punct(key)) and key not in self.variants:
            search_nodes.update([value for value in self.trie_dict.values()])
            ss_len.increment()
            return True

        else:
            if key.isalpha() and self.match_case == False:
                for char in generate_search_candidates(key):
                    current_chars.add(key)
            else:
                current_chars.add(key)

            
            if len(self.variants) > 0:
                additions = []
                for char in current_chars:
                    result = self.get_variants(char)
                    for sub in result:
                        if sub in self.trie_dict:
                            additions.append(sub)

            if self.match_case == False:
                additions = []
                for char in current_chars:
                    if char.isalpha() and self.match_case == False:
                        results = generate_search_candidates(char)
                        for result in results:
                            additions.append(result)

                for addition in additions:
                    current_chars.add(addition)

            if self.ignore_punct == False or self.ignore_ws == False:
                for char in self.trie_dict:
                    if (char.isspace() and self.ignore_ws == False) or (is_punct(char) and self.ignore_punct == False):
                        current_chars.append(char)
                
            if len(current_chars) == 0:
                return False
            
            else:
                new_nodes = [self.trie_dict[key] for key in current_chars if key in self.trie_dict]
                for node in new_nodes:
                    if node.word_end:
                        srm.add([node.target_word, 1])
                        
                    search_nodes.add(node)

                if len(search_nodes.nodes) == 0:
                    return False

                ss_len.increment()
                return True

        return False


    def has_next_key(self, key, ss_len, search_nodes, srm):
        current_chars = set([])
        new_nodes = []
        ss_len.increment()

        if (self.use_punct_as_variant == True and is_punct(key)) and key not in self.variants:
            for node in search_nodes.nodes:
                for child in node.children.values():
                    if child.word_end:
                        srm.add([node.target_word, ss_len.value])

                    if child.has_children:
                        new_nodes.append(child)

            if len(new_nodes) > 0:
                search_nodes.update(new_nodes)
                return True
                                
            else:
                return False if srm.count() == 0 else srm.get_results()

        elif not is_alpha_numeric(key) and (self.ignore_punct == True or self.ignore_ws == True):

        
            for node in search_nodes.nodes:
                for child in node.children.values():
                    if child.word_end:
                        srm.add([child.word_end, ss_len.value])

                    if child.has_children:
                        new_nodes.append(child)
                        
            node_names = set([node.get_name() for node in new_nodes])

            variants = [key] if key not in self.variants else self.get_variants(key)
        
            if not any (key in node_names for key in variants):
                return True

            else:

                if len(new_nodes) > 0:
                    search_nodes.update(new_nodes)
                    return True

                else:
                    return False if srm.count() == 0 else srm.get_results()
            
        else:

            if key.isalpha() and self.match_case == False:
                for char in generate_search_candidates(key):
                    current_chars.add(key)
            else:
                current_chars.add(key)

            
            if len(self.variants) > 0:
                additions = []
                for char in current_chars:
                    result = self.get_variants(char)
                    for sub in result:
                        additions.append(sub)

                for addition in additions:
                    current_chars.add(addition)

            if self.match_case == False:
                additions = []
                for char in current_chars:
                    if char.isalpha() and self.match_case == False:
                        results = generate_search_candidates(char)
                        for result in results:
                            additions.append(result)
                            
                for addition in additions:
                    current_chars.add(addition)
  
            addable = lambda x: x in current_chars or (x.isspace() and self.ignore_ws == False) or (is_punct(x) and self.ignore_punct == False)
            
            for node in search_nodes.nodes:
                
                children = [child for child in node.children.values() if addable(child.get_name())]

                for child in children:
                    if child.word_end:
                        srm.add([child.target_word, ss_len.value])

                    if child.has_children:
                        new_nodes.append(child)
                                        
            if len(new_nodes) > 0:
                search_nodes.update(new_nodes)
                return True

            return False if srm.count() == 0 else srm.get_results()

        return False        

    def get_target_words(self):
        results = set([])        
        
        def find_end(node):
            if not node.has_children():
                results.add(node.target_word)   
                return
            else:
                if node.word_end:       
                    results.add(node.target_word)
                children = node.children   
                for child in children:
                    temp = children[child]             
                    find_end(temp)

        for key in self.trie_dict:
            current_node = self.trie_dict[key]   
            if current_node.word_end:
                results.add(key)
            children = current_node.children

            for child in children:
                temp = children[child]             
                find_end(temp)

        return results

