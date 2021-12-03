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

import os
import warnings
import requests
import json

variants = {}
root = "https://rairye.github.io/variant_lists/"

try:
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "variants.json")) as jsf:
        variants = json.load(jsf)
        
except:
      warnings.warn("Could not load variants.json. A new version can be downloaded using update_variant_list()")
    
def get_variant_names():
    return [name for name in variants.keys()]

def download_variant(name, file_path = None):
    if file_path == None:
        file_path = os.path.dirname(os.path.abspath(__file__))
        
    file_name = variants.get(name)
    
    if file_name == None:
        warnings.warn("Could not download {}. Reason: The filename does not exist.".format(name))
        return {}
    
    else:
        try:
            response = requests.get(root + file_name)
            lines = response.text.splitlines()

            with open(os.path.join(file_path, file_name), 'w', encoding='utf-8') as f:
                for line in lines:
                    f.write(line + "\n")
            
            
        except Exception as e:
            warnings.warn("Could not download {}. Reason: {}".format(name, e))
            
    
def download_variants(file_path = None):
    for variant in variants.keys():
        download_variant(variant, file_path)

def get_variant_dict(name, offline = True, reverse = False, file_path = None):
    if file_path == None:
        file_path = os.path.dirname(os.path.abspath(__file__))
        
    file_name = variants.get(name)
    
    if file_name == None:
        warnings.warn("Could not load {}. Reason: The filename does not exist.".format(name))
        return {}
    else:
        variant_dict = {}
        f = None
        try:

            if offline == True:
                f = open(os.path.join(file_path, file_name) , encoding='utf-8')

            else:
                response = requests.get(root + file_name)
                f = response.text.splitlines()

            if reverse == False:

                for line in f:

                    strip = line.strip()
                    letters = strip.split(" ")
                    if len(letters) == 2:
                        if len(letters[0]) == 1 and len(letters[1]) == 1:
                            key = letters[0].strip()
                            value = letters[1].strip()
                    
                            if key not in variant_dict:
                                variant_dict[key] = [value]
                            else:
                                temp = variant_dict[key]
                                if value not in temp:
                                    temp.append(value)
                                    variant_dict[key] = temp
            else:
                for line in f:

                    strip = line.strip()
                    letters = strip.split(" ")
                    if len(letters) == 2:
                        if len(letters[0]) == 1 and len(letters[1]) == 1:
                            key = letters[1].strip()
                            value = letters[0].strip()
                    
                            if key not in variant_dict:
                                variant_dict[key] = [value]
                            else:
                                temp = variant_dict[key]
                                if value not in temp:
                                    temp.append(value)
                                    variant_dict[key] = temp

            if offline == True:
                f.close()

        except Exception as e:
          warnings.warn("Could not load {}. Reason: {}".format(name, e))
          if offline == True and f != None:
              f.close()
        
    return variant_dict

def update_variant_list(file_path = None):
    if file_path == None:
        file_path = os.path.dirname(os.path.abspath(__file__))
                                                 
    try:
        response = requests.get(root + "variants.json")
        text = response.text

        with open(os.path.join(file_path, "variants.json"), 'w', encoding='utf-8') as f:
            f.write(text)

        variants = json.loads(text)
        
    except Exception as e:
        warnings.warn("Could not download variants.json. Reason: {}".format(e))

