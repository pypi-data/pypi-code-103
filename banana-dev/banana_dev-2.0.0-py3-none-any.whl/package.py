from .generics import run_main, start_main, check_main
import asyncio
import sys

# Generics
def run(api_key, model_key, model_parameters):
    out = run_main(
        api_key = api_key, 
        model_key = model_key, 
        model_parameters = model_parameters
    )
    return out

def start(api_key, model_key, model_parameters):
    out = start_main(
        api_key = api_key, 
        model_key = model_key, 
        model_parameters = model_parameters
    )
    return out
    
def check(api_key, task_id):
    out_dict = check_main(
        api_key = api_key,
        task_id = task_id
    )
    return out_dict