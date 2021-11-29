def polygon_area(polygon):
    countPolygons = len(polygon)    
    if countPolygons < 3:
        raise Exception("To solve this problem, you need at least 3 points")
        
    firstSum = sum([polygon[i].x * polygon[i+1].y for i in range(countPolygons - 1)]) +  polygon[countPolygons - 1].x * polygon[0].y
    secondSum = sum([polygon[i+1].x * polygon[i].y for i in range(countPolygons - 1)]) +  polygon[countPolygons - 1].y * polygon[0].x
    return (firstSum - secondSum) / 2