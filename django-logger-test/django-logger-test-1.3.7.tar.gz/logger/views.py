from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from .signals import signal_list


def index(request):
    signal_list["pizza_done"].send(sender=object,
                                   cose="Cose",
                                   task_id=123,
                                   category='pizza'
                                   )
    return HttpResponse("PIZZA PAGE.")


def react_index(request):
    signal_list["react"].send(sender=object,
                              version=17,
                              name="React V.",
                              category='react'
                              )
    return HttpResponse("REACT PAGE.")
