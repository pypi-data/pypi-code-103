from nbgitpuller.plugin_helper import handle_files_helper
from nbgitpuller.plugin_hook_specs import hookimpl
import asyncio

@hookimpl
def handle_files(helper_args, query_line_args):
    """
    :param dict helper_args: the function, helper_args["progress_func"], that writes messages to
    the progress stream in the browser window and the download_q, helper_args["download_q"] the progress function uses.
    :param dict query_line_args: this includes all the arguments included on the nbgitpuller URL
    :return two parameter json unzip_dir and origin_repo_path
    :rtype json object
    """
    loop = asyncio.get_event_loop()
    tasks = handle_files_helper(helper_args, query_line_args), helper_args["wait_for_sync_progress_queue"]()
    result_handle, _ = loop.run_until_complete(asyncio.gather(*tasks))
    return result_handle
