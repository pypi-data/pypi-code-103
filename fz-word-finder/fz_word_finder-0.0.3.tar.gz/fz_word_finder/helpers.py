
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

#Helper methods. Not suggested for use outside of this package.


def is_supported_target_word_type(target_words):
    supported_types = set([str, list])
    return type(target_words) in supported_types

def is_punct(char):
    if type(char) != str:
        return False
    
    if len(char) > 1 or char == "":
        return False

    return (char.isalpha() or (char.isnumeric() or char.isspace())) == False


def is_alpha_numeric(char):

    return char.isalpha() or char.isnumeric()


def generate_search_candidates(char):
    upper = char.upper() if char.islower() else char
    lower = char.lower() if char.upper() else char

    if upper == lower:
        return [char]

    return [upper, lower]

class ss_len_manager():
    def __init__(self):
        self.value = 0
        
    def increment(self):
        self.value+=1

    def reset(self):
        self.value = 0

class search_nodes_manager():
    def __init__(self):
        self.nodes = []

    def update(self, new_nodes):
        self.nodes = new_nodes

    def add(self, new_node):
        self.nodes.append(new_node)

class search_results_manager():
    def __init__(self):
        self.results = []

    def add(self, result):
        self.results.append(result)

    def reset(self):
        self.results = []

    def get_results(self):
        if len(self.results) > 0:
            return self.results
        
        return False

    def count(self):
        return len(self.results)
