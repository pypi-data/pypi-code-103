from eagers.config.dataset import DATASET_TYPES
from eagers.class_definition.data_set import NodeDataTimeSeries, WeatherTimeSeries, OtherTimeSeries

def read_test_data(data):
    fn_args = tuple(data.pop(f'{x}_filename') for x in DATASET_TYPES) # nodedata_filename and weather_filename
    test_data = dict(nodedata=NodeDataTimeSeries(fn_args[0]), weather=WeatherTimeSeries(fn_args[1]), other=OtherTimeSeries(fn_args[2]))
    test_data['nodedata_network_info'] = data['nodedata_network_info']
    test_data['other_object_info'] = data['other_object_info']
    test_data['hist_prof'] = []
    test_data['_nodedata_filename'] = test_data['nodedata'].filepath.name
    test_data['_weather_filename'] = test_data['weather'].filepath.name
    test_data['_other_filename'] = test_data['other'].filepath.name
    return test_data