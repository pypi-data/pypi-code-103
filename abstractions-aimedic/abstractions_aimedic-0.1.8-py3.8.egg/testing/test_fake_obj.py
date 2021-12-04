# import pytest
#
# import sys
# from pathlib import Path
# HERE = Path(__file__).parent
# src_path = HERE.parent.joinpath('src')
# sys.path.append('src')

# from dataset.fake_objs import Obj1, Obj2


# @pytest.fixture(scope="module")
# def result_holder():
#     return {}
#
#
# @pytest.mark.faketest
# def test_obj1(result_holder):
#     obj1 = Obj1('object 1')
#     # request.config.cache.set('obj1', obj1)
#     result_holder['obj1'] = obj1
#     assert True
#
#
# @pytest.mark.faketest
# def test_obj2(result_holder):
#     obj1 = result_holder['obj1']
#     obj2 = Obj2(obj1)
#     assert True
