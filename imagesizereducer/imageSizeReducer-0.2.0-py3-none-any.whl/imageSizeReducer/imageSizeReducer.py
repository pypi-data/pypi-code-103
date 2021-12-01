from PIL import Image
import math

def resize(a, b, c):
    try:
        foo = Image.open(a)
        x, y = foo.size
        x2, y2 = math.floor(x-50), math.floor(y-20)
        foo = foo.resize((x2,y2),Image.ANTIALIAS)
        foo.save(c,quality=b)
        return({
            "message": "successfully completed image resize",
            "actual-image-path":a,
            "quality-specified":b,
            "path-to-image":c
        })
    except Exception as e:
        return({
            "message": "image resize process failed",
            "error": e,
            "actual-image-path":a,
            "quality-specified":b,
            "path-to-image":c
        })