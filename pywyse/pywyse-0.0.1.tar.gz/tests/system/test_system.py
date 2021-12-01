from pywyse.system import CallBack, Member, Board
import pytest 

def test_callback(): 

    resp = CallBack().get_callbacks(pageSize=100)
    assert isinstance(resp, list)
    assert len(resp) == 100
    assert CallBack().endpoint == '/system/callbacks/'
    


def test_boards(): 

    resp = Board().get_boards(pageSize=5)
    assert isinstance(resp, list)
    assert len(resp) == 5 
    
def test_members(): 

    resp = Member().get_members(pageSize=100, conditions="inactiveFlag=False")
    assert isinstance(resp, list)
    
    
    resp = Member().get_members(pageSize=5)
    assert isinstance(resp, list)
    assert len(resp) == 5 