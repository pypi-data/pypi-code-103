#! /usr/bin/env python
# %% 
import subprocess
import argparse
print("All packages loaded")
# %%
name = input("[+]Please insert your name:")
print("[+]Your name is:",name)

# %%
def hello():
    return "Hello "+name