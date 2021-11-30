from typing import List, Optional, Dict
import hoss

import requests
import re

import os
import time
import datetime
from pathlib import Path
from enum import Enum

from rich import box
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.style import Style
from rich.text import Text
from rich.live import Live
from rich.table import Table
from rich.align import Align
from rich.layout import Layout

import humanize

from hoss.console import console


class TaskStatus(Enum):
    """Enum for setting the state of tasks"""
    WAITING = 0
    RUNNING = 1
    DONE = 2
    ERROR = -1


def _get_task_status(tasks: List[str], status: List[TaskStatus]) -> Align:
    """Take a list of task statuses and render a table

    Args:
        tasks: list of tasks
        status: list of TaskStatus values

    Returns:
        the rendered Table
    """
    table = Table(box=box.SIMPLE_HEAVY, show_footer=False)
    table_centered = Align.center(table)

    table.add_column("Status", no_wrap=True)
    table.add_column("Tasks", no_wrap=True)

    for t, s in zip(tasks, status):
        if s == TaskStatus.WAITING:
            table.add_row(":hourglass:", t)
        elif s == TaskStatus.RUNNING:
            table.add_row(":face_with_monocle:", t)
        elif s == TaskStatus.DONE:
            table.add_row(":white_check_mark:", t)
        elif s == TaskStatus.ERROR:
            table.add_row(":x:", t)
        else:
            table.add_row(":question:", t)

    return table_centered


def upload_directory(dataset_name: str, directory: str, namespace: str, endpoint: str,
                     skip: str, max_concurrency: int = 10, multipart_threshold: int = 45,
                     metadata: Optional[Dict[str, str]] = None) -> None:
    """Function to upload a directory with a CLI interface for status

    This method will sort files by size, starting with the smallest first, and then upload them
    one at a time.

    Args:
        dataset_name: Name of the dataset to upload into
        directory: The containing the files to upload. The directory name will be included.
        namespace: The namespace containing the dataset
        endpoint: The URL for the Hoss server you are uploading to
        skip: A regex string of files that should be skipped
        max_concurrency: max concurrency
        multipart_threshold: size in megabytes to use multipart uploads
        metadata: Optional dict of key-value pairs to write to all files as metadata

    Returns:
        None
    """
    log_msgs = list()

    def _log(msg: str, layout_obj: Layout, update_last=False) -> None:
        """Helper method to update and build the log window contents"""
        if update_last:
            del log_msgs[0]

        log_msgs.insert(0, f"{datetime.datetime.now().strftime('%H:%M:%S.%f %p')} - {msg}")
        log_panel = Panel(Text("\n".join(log_msgs)), title="[b]Status", border_style="#957299", padding=(1, 2),
                          expand=True)
        layout_obj["status"].update(log_panel)

    # Initialize the layout
    console.clear()
    layout = Layout(name="root")
    layout.split(
        Layout(name="title", size=3),
        Layout(name="header", size=10),
        Layout(name="main", ratio=1),
    )
    layout["header"].split_row(
        Layout(name="summary"),
        Layout(name="tasks", ratio=1, minimum_size=60),
    )
    layout["main"].split_column(
        Layout(name="progress", size=10),
        Layout(name="status"),
    )

    # Set title element
    title = Table.grid(expand=True)
    title.add_column(justify="center", ratio=1)
    title.add_row("[b]Hoss Upload Tool[/b]")
    layout["title"].update(Panel(title, style="white on #957299"))

    # Set summary element
    summary_grid = Table(box=box.SIMPLE_HEAVY, show_footer=False)
    summary_grid_centered = Align.center(summary_grid)
    summary_grid.add_column(justify="right")
    summary_grid.add_column("Settings", justify="left")
    summary_grid.add_row("[b]Server:[/b]", endpoint)
    summary_grid.add_row("[b]Namespace:[/b]", namespace)
    summary_grid.add_row("[b]Dataset:[/b]", dataset_name)
    summary_grid.add_row("[b]Directory:[/b]", directory)
    layout["summary"].update(summary_grid_centered)

    tasks = ["Check for credentials",
             "Check server connectivity",
             "Check dataset exists",
             "Process directory",
             "Upload data",
             ]

    layout["tasks"].update(_get_task_status(tasks,
                                            [TaskStatus.WAITING,
                                             TaskStatus.WAITING,
                                             TaskStatus.WAITING,
                                             TaskStatus.WAITING,
                                             TaskStatus.WAITING]))

    # Initialize Progress section
    job_progress = Progress(
        "{task.description}",
        SpinnerColumn(),
        BarColumn(pulse_style=Style(color="#957299"), complete_style=Style(color="#957299")),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%", style=Style(color="#957299")),
        expand=True
    )
    prepare_job_id = job_progress.add_task("[white]Preparing Upload", total=7)
    upload_job_id = job_progress.add_task("[white]Uploading Data", start=False)
    layout['progress'].update(
        Align.center(Panel(job_progress, title="[b]Progress", border_style="#957299", padding=(1, 2), expand=False),
                     vertical="middle"))

    _log("Starting...", layout)

    with Live(layout, console=console, refresh_per_second=30):
        # Check for PAT
        if not os.environ.get("HOS_PAT"):
            # No credentials set
            _log("Personal Access Token not found!", layout)
            layout["tasks"].update(_get_task_status(tasks,
                                                    [TaskStatus.ERROR,
                                                     TaskStatus.WAITING,
                                                     TaskStatus.WAITING,
                                                     TaskStatus.WAITING,
                                                     TaskStatus.WAITING]))
            layout['progress'].update(
                Align.center(Panel("Failed to get personal access token from environment variable.\n\n"
                                   "Make sure you have set the `HOS_PAT` environment variable and try again."),
                             style="white on red", height=6))
            return
        else:
            _log("Personal Access Token found.", layout)
            layout["tasks"].update(_get_task_status(tasks,
                                                    [TaskStatus.DONE,
                                                     TaskStatus.RUNNING,
                                                     TaskStatus.WAITING,
                                                     TaskStatus.WAITING,
                                                     TaskStatus.WAITING]))
            job_progress.advance(prepare_job_id)
            time.sleep(1)

        try:
            _log("Connecting to server and exchanging credentials...", layout)
            server = hoss.connect(endpoint)
            ns = server.get_namespace(namespace)
            _log("Server reachable and credentials ready.", layout)
            layout["tasks"].update(_get_task_status(tasks,
                                                    [TaskStatus.DONE,
                                                     TaskStatus.DONE,
                                                     TaskStatus.RUNNING,
                                                     TaskStatus.WAITING,
                                                     TaskStatus.WAITING]))
            job_progress.advance(prepare_job_id)
        except requests.exceptions.ConnectionError:
            layout["tasks"].update(_get_task_status(tasks,
                                                    [TaskStatus.DONE,
                                                     TaskStatus.ERROR,
                                                     TaskStatus.WAITING,
                                                     TaskStatus.WAITING,
                                                     TaskStatus.WAITING]))
            _log(f"Server unreachable. Verify your network connection or endpoint setting.", layout)
            layout['progress'].update(
                Align.center(Panel("Failed to reach server. \n\nCheck your endpoint and network connectivity.",
                                   style="white on red", height=6)))
            return
        except hoss.error.HOSException as err:
            layout["tasks"].update(_get_task_status(tasks,
                                                    [TaskStatus.DONE,
                                                     TaskStatus.ERROR,
                                                     TaskStatus.WAITING,
                                                     TaskStatus.WAITING,
                                                     TaskStatus.WAITING]))
            layout['progress'].update(Align.center(Panel(
                f"Failed to exchange credentials. \n\nVerify PAT with your Hoss server and try again. Error: \n\n {err}",
                style="white on red", height=10)))
            _log(f"Failed to exchange credentials.", layout)
            return

        try:
            _log(f"Checking if dataset exists in the specified server and namespace.", layout)
            ds = ns.get_dataset(dataset_name)
            layout["tasks"].update(_get_task_status(tasks,
                                                    [TaskStatus.DONE,
                                                     TaskStatus.DONE,
                                                     TaskStatus.DONE,
                                                     TaskStatus.RUNNING,
                                                     TaskStatus.WAITING]))
            _log(f"Dataset ready.", layout)
            job_progress.advance(prepare_job_id)
        except hoss.NotFoundException:
            # Dataset does not exist
            layout['progress'].update(Align.center(
                Panel(f"Specified dataset does not exist. \n\nVerify input or create dataset and try again.",
                      style="white on red", height=6)))
            layout["tasks"].update(_get_task_status(tasks,
                                                    [TaskStatus.DONE,
                                                     TaskStatus.DONE,
                                                     TaskStatus.DONE,
                                                     TaskStatus.ERROR,
                                                     TaskStatus.WAITING]))
            _log(f"Dataset not found. Please create it and try again.", layout)
            return

        # set transfer settings
        mb = 1000 ** 2
        ds.namespace.object_store.set_transfer_config(multipart_threshold * mb, max_concurrency)

        job_progress.advance(prepare_job_id)

        # list files
        _log(f"Scanning directory.", layout)
        files = filter(os.path.isfile, Path(directory).rglob('*'))
        job_progress.advance(prepare_job_id)

        # Sort files
        _log(f"Sorting files.", layout)
        files_sorted = sorted(files, key=lambda x: os.stat(x).st_size)
        job_progress.advance(prepare_job_id)

        # Find files to skip if you need to
        if skip != "":
            _log(f"Processing skipped files.", layout)
            skip_check = re.compile(r'{}'.format(skip))
            skip_files = [f for f in files_sorted if skip_check.match(f.name)]
            for f in skip_files:
                files_sorted.remove(f)
                if not skip:
                    files_sorted.append(f)

        job_progress.advance(prepare_job_id)
        layout["tasks"].update(_get_task_status(tasks,
                                                [TaskStatus.DONE,
                                                 TaskStatus.DONE,
                                                 TaskStatus.DONE,
                                                 TaskStatus.DONE,
                                                 TaskStatus.WAITING]))

        job_progress.update(upload_job_id, total=len(files_sorted), description="[white]Uploading Data")
        job_progress.start_task(upload_job_id)
        _log(f"Uploading {len(files_sorted)} files.", layout)

        # upload files
        errors = False
        session_folder = os.path.basename(directory)
        for cnt, f in enumerate(files_sorted):
            if f.name == ".DS_Store":
                _log(f"Skipping {f.relative_to(directory)}.", layout)
                job_progress.advance(upload_job_id)
                continue

            try:
                o = ds / session_folder / f.relative_to(directory).as_posix()
                if not o.exists():
                    _log(f"[{cnt+1}/{len(files_sorted)}] Uploading {f.relative_to(directory)}..."
                         f" ({humanize.naturalsize(f.stat().st_size)}).", layout)
                    o.write_from(f.as_posix(), metadata=metadata)
                    _log(f"[{cnt + 1}/{len(files_sorted)}] Uploading {f.relative_to(directory)}...done!"
                         f" ({humanize.naturalsize(f.stat().st_size)}).", layout, update_last=True)
                else:
                    _log(f"[{cnt+1}/{len(files_sorted)}] Skipping {f.relative_to(directory)}. File already exists.",
                         layout)
            except Exception as err:
                _log(f"ERROR: {f.relative_to(directory)} upload failed!", layout)
                _log(str(err), layout)
                errors = True

            job_progress.advance(upload_job_id)

        if not errors:
            _log(f"Upload complete!.", layout)
        else:
            _log(f"Upload completed with errors! Check for missing files.", layout)
        layout["tasks"].update(_get_task_status(tasks,
                                                [TaskStatus.DONE,
                                                 TaskStatus.DONE,
                                                 TaskStatus.DONE,
                                                 TaskStatus.DONE,
                                                 TaskStatus.DONE]))

        for cnt in range(15):
            _log(f"Exiting in {15-cnt} seconds...", layout, update_last=True)
            time.sleep(1)

    console.clear()
