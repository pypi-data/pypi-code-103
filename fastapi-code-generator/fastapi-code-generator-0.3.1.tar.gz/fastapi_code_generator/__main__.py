from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

import typer
from datamodel_code_generator import PythonVersion, chdir
from datamodel_code_generator.format import CodeFormatter
from datamodel_code_generator.imports import Import, Imports
from datamodel_code_generator.reference import Reference
from datamodel_code_generator.types import DataType
from jinja2 import Environment, FileSystemLoader

from fastapi_code_generator.parser import OpenAPIParser, Operation

app = typer.Typer()

BUILTIN_TEMPLATE_DIR = Path(__file__).parent / "template"

@app.command()
def main(
    input_file: typer.FileText = typer.Option(..., "--input", "-i"),
    output_dir: Path = typer.Option(..., "--output", "-o"),
    model_file: str = typer.Option(None, "--model-file", "-m"),
    template_dir: Optional[Path] = typer.Option(None, "--template-dir", "-t"),
) -> None:
    input_name: str = input_file.name
    input_text: str = input_file.read()
    if model_file:
        model_path = Path(f"{model_file}.py")
    else:
        model_path = Path("models.py")
    return generate_code(input_name, input_text, output_dir, template_dir, model_path)


def _get_most_of_reference(data_type: DataType) -> Optional[Reference]:
    if data_type.reference:
        return data_type.reference
    for data_type in data_type.data_types:
        reference = _get_most_of_reference(data_type)
        if reference:
            return reference
    return None


def generate_code(
    input_name: str, input_text: str, output_dir: Path, template_dir: Optional[Path], model_path: Path
) -> None:
    if not output_dir.exists():
        output_dir.mkdir(parents=True)
    if not template_dir:
        template_dir = BUILTIN_TEMPLATE_DIR

    parser = OpenAPIParser(input_text)
    with chdir(output_dir):
        models = parser.parse()
    if not models:
        return
    elif isinstance(models, str):
        output = output_dir / model_path
        modules = {output: (models, input_name)}
    else:
        raise Exception('Modular references are not supported in this version')

    environment: Environment = Environment(
        loader=FileSystemLoader(
            template_dir if template_dir else f"{Path(__file__).parent}/template",
            encoding="utf8",
        ),
    )
    imports = Imports()
    imports.update(parser.imports)
    for data_type in parser.data_types:
        reference = _get_most_of_reference(data_type)
        if reference:
            imports.append(data_type.all_imports)
            imports.append(
                Import.from_full_path(f'.{model_path.stem}.{reference.name}')
            )
    for from_, imports_ in parser.imports_for_fastapi.items():
        imports[from_].update(imports_)
    results: Dict[Path, str] = {}
    code_formatter = CodeFormatter(PythonVersion.PY_38, Path().resolve())
    sorted_operations: List[Operation] = sorted(
        parser.operations.values(), key=lambda m: m.path
    )
    for target in template_dir.rglob("*"):
        relative_path = target.relative_to(template_dir)
        result = environment.get_template(str(relative_path)).render(
            operations=sorted_operations, imports=imports, info=parser.parse_info(),
        )
        results[relative_path] = code_formatter.format_code(result)

    timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    header = f"""\
# generated by fastapi-codegen:
#   filename:  {Path(input_name).name}
#   timestamp: {timestamp}"""

    for path, code in results.items():
        with output_dir.joinpath(path.with_suffix(".py")).open("wt") as file:
            print(header, file=file)
            print("", file=file)
            print(code.rstrip(), file=file)

    header = f'''\
# generated by fastapi-codegen:
#   filename:  {{filename}}'''
    #     if not disable_timestamp:
    header += f'\n#   timestamp: {timestamp}'

    for path, body_and_filename in modules.items():
        body, filename = body_and_filename
        if path is None:
            file = None
        else:
            if not path.parent.exists():
                path.parent.mkdir(parents=True)
            file = path.open('wt', encoding='utf8')

        print(header.format(filename=filename), file=file)
        if body:
            print('', file=file)
            print(body.rstrip(), file=file)

        if file is not None:
            file.close()


if __name__ == "__main__":
    typer.run(main)
