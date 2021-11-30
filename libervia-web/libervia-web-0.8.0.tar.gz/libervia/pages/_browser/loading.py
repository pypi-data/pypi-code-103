"""manage common dialogs"""

from browser import document

def remove_loading_screen():
    print("removing loading screen")
    document['loading_screen'].remove()
