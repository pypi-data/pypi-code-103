#!/usr/bin/env python
# coding: utf-8

'''
Model and Descriptor module
'''

import datetime
from decimal import Decimal

from .abstract import RegularField, EnumField, ReferenceField

     
class DateTime(RegularField):
    def __init__(self, **kwargs) -> None:
        super().__init__(datetime.datetime, **kwargs) 
        self.tag = 'input:datetime-local'
        
        
class Text(RegularField):
    def __init__(self, **kwargs) -> None:
        super().__init__(str, **kwargs) 
        self.tag = 'textarea'

        
class SemicolonStrToList(RegularField):
    def __init__(self, **kwargs) -> None:
        super().__init__(str, **kwargs) 
        self.tag = 'textarea'
    
    def parse(self, obj, value):
        trim = lambda x: x.strip()
        split = lambda x: x.split(";")
        process = lambda x: [i for i in sorted([trim(w) for w in split(x) if w not in ['', None]]) if i not in ['', None]]
        if value:
            return process(value)
        return value

    
class String(RegularField):
    def __init__(self,**kwargs) -> None:
        super().__init__(str, **kwargs) 


    def parse(self, obj, value):
        return value

        
class Choice(EnumField):
    '''
    Receive enumeration name to store in db. 
    The __get__ method return the enumeration member instance.
    '''
    
    def __init__(self,enumeration, **kwargs) -> None:
        super().__init__(enumeration, **kwargs) 
        self.tag = "select"
        
    def  parse(self, obj, value):
        if value:
            return {e.name: e for e in self.owner.__members__.values()}[value]
        return value 
    
    
class Date(RegularField):
    '''
    Receive date as a isoformat string to store in db. 
    The __get__ method return the datetime.date instance.
    '''
    
    def __init__(self, **kwargs) -> None:
        super().__init__(datetime.date, **kwargs) 
        self.tag = 'input:date'

    def  parse(self, obj, value):
        return datetime.date.fromisoformat(value) if isinstance(value, str) else value  


class Title(RegularField):
    '''
    Receive a string to store in db formated to title().
    The __get__ method return the string.
    '''
    
    def __init__(self, **kwargs) -> None:
        super().__init__(str, **kwargs) 

    def parse(self, obj, value):
        if isinstance(value, str):
            return value.title()
        return value 

    
class Number(RegularField):
    def __init__(self, **kwargs) -> None:
        super().__init__(float, **kwargs) 
        self.tag = 'input:number'

    def parse(self, obj, value):
        return float(value) if isinstance(value, str) else value  

    
class Integer(RegularField):
    def __init__(self,**kwargs) -> None:
        super().__init__(int, **kwargs) 
        self.tag = 'input:number'

    def parse(self, obj, value):
        return int(value) if isinstance(value, str) else value  

    
class Float(RegularField):
    def __init__(self, **kwargs) -> None:
        super().__init__(float, **kwargs) 
        self.tag = 'input:number'

    def parse(self, obj, value):
        return float(value) if isinstance(value, str) else value  

    
class Real(RegularField):
    def __init__(self,**kwargs) -> None:
        super().__init__(Decimal, **kwargs) 
        self.tag = 'input:number'   
        
    def parse(self, obj, value):
        if value:
            return Decimal(value)
        return value


class Key(ReferenceField):
    def __init__(self,table, **kwargs) -> None:
        super().__init__(table, **kwargs) 
        self.tag = 'select'

