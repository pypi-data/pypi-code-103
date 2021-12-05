from dojahcore import financial
from dojahcore.messaging import Messaging
from dojahcore.identification import Identification
from dojahcore.verification import Verification
from dojahcore.financial import Financial
from dojahcore.general import General

try:
    a = "/9j/4AAQSkZJRgABAQEASABIAAD/4gI0SUNDX1BST0ZJTEUAAQEAAAIkYXBwbAQAAABtbnRyUkdCIFhZWiAH4QAHAAcADQAWACBhY3NwQVBQTAAAAABBUFBMAAAAAAAAAAAAAAAAAAAAAAAA9tYAAQAAAADTLWFwcGzKGpWCJX8QTTiZE9XR6hWCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAApkZXNjAAAA/"
    resp =  General.my_dojah_balance()
    print(resp)
    
except Exception as e:
    print(str(e))