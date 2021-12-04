import logging
from os import listdir
from pathlib import Path
from typing import Tuple

import click

logging.basicConfig(level="DEBUG", format="'%(asctime)s - %(name)s - %(levelname)s - %(message)s'")
logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "--input",
    "-i",
    default="./",
    help="Path where to find CSV files to be converted to JSON.",
    type=str,
)
@click.option(
    "--output",
    "-o",
    default="./",
    help="Path where the converted files will be saved.",
    type=str,
)
@click.option(
    "--mode",
    "-m",
    default="CSV",
    help="Choose CSV for CSV files to JSON, or JSON for JSON files to CSV.",
    type=click.Choice(["CSV", "JSON"], case_sensitive=False),
)
@click.option(
    "--delimiter",
    "-d",
    default=",",
    help="Separator used to split the files. ge: `;`.",
    type=click.Choice([",", ";", "t"]),
)
@click.option(
    "--prefix",
    "-p",
    prompt=True,
    prompt_required=False,
    default="file",
    help=(
        "Prefix used to prepend to the name of the converted file saved on disk."
        " The suffix will be a number starting from 0. ge: file_0.json."
    ),
    type=str,
)
def converter(
    input: str = "./",
    output: str = "./",
    delimiter: str = ",",
    prefix: str = None,
    mode: str = "CSV",
):
    input_path = Path(input)
    output_path = Path(output)
    if delimiter == "t":
        delimiter = "\t"
    logger.info("Input Path: %s", input_path)
    logger.info("Output Path: %s", output_path)

    for p in [input_path, output_path]:
        if not (p.is_file() or p.is_dir()):
            raise TypeError("Not a valid path of file name.")

    if input_path.is_file():
        if mode == "CSV":
            logger.info("Mode: CSV to JSON.")
            data = read_csv_file(source=input_path, delimiter=delimiter)
            json = parse_csv_to_json(data)
            if prefix is not None:
                filename = "{}_{}.json".format(prefix, "0")
            else:
                filename = "{}_{}.json".format(input_path, "0")
            write_json_data(json, Path(output_path, filename))
        else:
            logger.info("Mode: JSON to CSV.")
            data = read_json_file(source=input_path)
            csv = parse_json_to_csv(data, delimiter)
            if prefix is not None:
                filename = "{}_{}.csv".format(prefix, "0")
            else:
                filename = "{}_{}.csv".format(input_path, "0")
            write_csv_data(csv, Path(output_path, filename))
    else:
        if mode == "CSV":
            logger.info("Mode: CSV to JSON.")
            i = 0
            for file in Path.iterdir(input_path):
                data = read_csv_file(source=file, delimiter=delimiter)
                json = parse_csv_to_json(data)
                if prefix is not None:
                    filename = "{}_{}.json".format(prefix, i)
                else:
                    filename = "{}_{}.json".format(str(file).split(".")[0], i)
                write_json_data(json, Path(output_path, filename))
                i += 1
        else:
            logger.info("Mode: JSON to CSV.")
            i = 0
            for file in Path.iterdir(input_path):
                if prefix is not None:
                    filename = "{}_{}.csv".format(prefix, i)
                else:
                    filename = "{}_{}.csv".format(str(file).split(".")[0], i)
                data = read_json_file(source=file)
                csv = parse_json_to_csv(data, delimiter)
                write_csv_data(csv, Path(output_path, filename))
                i += 1


def read_csv_file(source: Path, delimiter: str = ",") -> list:
    """Load a single csv file or all files withing a directory."""
    with source.open(mode="r") as file:
        data = file.readlines()
    parsed_data = [line.strip().split(delimiter) for line in data]
    return parsed_data


def parse_csv_to_json(data: list) -> list:
    """Convert data list to dictionary format."""
    columns = data[0]
    lines = data[1:]
    result = [dict(zip(columns, line)) for line in lines]
    return result


def write_json_data(data: list, output_path: Path):
    """Write data list to json format."""
    with output_path.open(mode="w") as file:
        file.write("[\n")
        for d in data[:-1]:
            write_dictionary(d, file, append_comma=True)
        write_dictionary(d, file, append_comma=False)
        file.write("]\n")


def write_dictionary(data: dict, io, append_comma: bool = True):
    """Write json data to a file."""
    io.write("\t{\n")
    items = tuple(data.items())
    for line in items[:-1]:
        write_line(line, io, True)
    write_line(items[-1], io, False)
    io.write("\t}")
    if append_comma:
        io.write(",\n")
    else:
        io.write("\n")


def write_line(line: tuple, io, append_comma: bool = True):
    """Write line to a file."""
    key, value = line
    if append_comma:
        io.write(f"\t\t{key}: {value},\n")
    else:
        io.write(f"\t\t{key}: {value}\n")


def read_json_file(source: Path) -> list:
    """Load a single json file or all files withing a directory."""
    with source.open(mode="r") as file:
        data = file.readlines()
    parsed_data = [line.strip().replace(",", "") for line in data[1:-1]]  # remove \n \t , "
    while "{" in parsed_data:
        parsed_data.remove("{")

    data_list = []
    tmp: list = []
    for line in parsed_data:
        if line == "}" or line == "},":
            data_list.append(tmp)
            tmp = []
        else:
            tmp.append(line)
    return data_list


def parse_json_to_csv(data: list, delimiter: str) -> str:
    """Convert list of dictionaries to CSV string."""
    pairs = []
    for ls in data:
        pairs.append([line.split(":") for line in ls])
    header = [line[0] for line in pairs[0]]
    values: list = []
    for line in pairs:
        values.append([ls[1] for ls in line])
    csv = delimiter.join(header) + "\n"
    for line in values:
        converted_line = delimiter.join(line)
        csv = csv + converted_line + "\n"
    return csv


def write_csv_data(data: str, output_path: Path):
    with output_path.open(mode="w") as file:
        for line in data:
            file.write(line)
