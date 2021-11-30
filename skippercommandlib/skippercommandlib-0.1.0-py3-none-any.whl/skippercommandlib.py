import asyncio
import subprocess
import os
import time
import pprint
from contextlib import contextmanager
import pty
import threading
import colorama

colorama.init()

def change_directory(directory_string):
    starting_directory = execute_command('pwd')

    os.chdir(directory_string)
    time.sleep(1)

    print(f"cd {directory_string}", flush=True)
    ending_directory = execute_command('pwd')

    if starting_directory == ending_directory:
        return False

    return True

def execute_command(command_string):
    print(command_string, flush=True)
    return subprocess.check_output(command_string, shell=True).decode('utf-8').split("\n")


async def run_two_terminal_commands_in_parallel(cmd_1, cmd_2, delay=None, duration=None):
    # a follower thread will run command 1 and the leader thread will run command 2
    # delay: the time for the leader command to wait for the follower command to run
    # duration: the expected time for the follower command to run

    @contextmanager
    def _make_follower_pty():
        leader_pty, follower_pty = pty.openpty()
        yield follower_pty
        os.close(follower_pty)
        os.close(leader_pty)

    async def run_command_on_follower(cmd, duration=None):

        with _make_follower_pty() as follower_pty:
            kwargs = {
                "stdout": asyncio.subprocess.PIPE,
                "stderr": asyncio.subprocess.PIPE,
                "stdin": follower_pty,
            }

            process = await asyncio.create_subprocess_exec(
                *cmd,
                **kwargs
            )

            stdout, stderr = await asyncio.wait_for(process.communicate(), duration)

            pp = pprint.PrettyPrinter(indent=4)
            pp.pprint(stdout)

            return {
                "cmd": cmd,
                "stdout": stdout,
                "stderr": stderr,
                "returncode": process.returncode,
                "pid": process.pid
            }

    def between_follower_callback(cmd):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # TODO: this often fails - in a way that doesn't seem to prevent functionality.
        loop.run_until_complete(run_command_on_follower(cmd, duration))
        loop.close()

    if __name__ == '__main__':

        assert threading.current_thread() is threading.main_thread()
        asyncio.get_event_loop()
        asyncio.get_child_watcher()

        x = threading.Thread(target=between_follower_callback, args=([cmd_1.split()]),
                             name="follower_thread")
        x.start()

        if delay != None:
            time.sleep(delay)

        x.join()

        pp = pprint.PrettyPrinter(indent=4)
        try:
            pptext = execute_command(cmd_2)
        except Exception as e:
            pptext = colorama.Fore.RED + "There was an exception: " + str(
                e) + colorama.Fore.WHITE
        pp.pprint(pptext)

