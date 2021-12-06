from itertools import islice

class UtilsTimeSeries():

    def _dataPointsToString(dataPoints:dict) -> str:
        """Converts a dictionary of datapoints to graphQL string"""

        _dataPoints = ''
        for timestamp, value in dataPoints.items():
            if value == None:
                _dataPoints += f'''{{
                    timestamp: "{timestamp}"
                    value: 0
                    flag: MISSING
                    }}\n'''
            else: 
                _dataPoints += f'''{{
                        timestamp: "{timestamp}"
                        value: {value}
                        }}\n'''

        return _dataPoints

    def _sliceDataPoints(dataPoints:dict, start:int, stop:int):
        """Return a slice of the dataPoints dictionary"""

        return dict(islice(dataPoints, start, stop))