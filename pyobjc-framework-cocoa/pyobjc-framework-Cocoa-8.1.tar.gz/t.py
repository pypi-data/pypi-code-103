import AppKit
import gc
import time

app = AppKit.NSApplication.sharedApplication()  # noqa: F841

img = AppKit.NSBitmapImageRep.alloc().initWithBitmapDataPlanes_pixelsWide_pixelsHigh_bitsPerSample_samplesPerPixel_hasAlpha_isPlanar_colorSpaceName_bitmapFormat_bytesPerRow_bitsPerPixel_(  # noqa: B950
    None, 255, 255, 8, 4, True, False, AppKit.NSCalibratedRGBColorSpace, 0, 0, 0
)

context = None
context = AppKit.NSGraphicsContext.graphicsContextWithBitmapImageRep_(img)
current = AppKit.NSGraphicsContext.currentContext()
try:
    AppKit.NSGraphicsContext.setCurrentContext_(context)
    AppKit.NSRectFill(((0, 0), (1, 2)))
finally:
    AppKit.NSGraphicsContext.setCurrentContext_(current)


print(5); gc.collect()
del img
print(5,1); gc.collect()
del context
time.sleep(1)
print("done")
