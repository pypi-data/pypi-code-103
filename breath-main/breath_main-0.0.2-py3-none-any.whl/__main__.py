import sys

from .session_manager import ProcessSessionManager


if __name__ == '__main__':

    session_manager = ProcessSessionManager()
    session_manager.create_service("ConsoleApplication")
    
    while True:
        session_manager.run()
