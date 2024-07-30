import argparse
import ast
import json
import os
from pathlib import Path
from typing import Optional, TextIO

import jsonschema
import yaml
from pathvalidate import is_valid_filepath
from pathvalidate.argparse import validate_filepath_arg

from app.utils.main_schema_gen import generate_main_schema
from app.utils.model_generator import generate_model
from app.utils.rest_generator import generate_router
from app.utils.schema_validate import is_subset

main_schema_filename = os.path.dirname(os.path.abspath(__file__)) + "/schemas/main_schema.json"


def main(argv: Optional[list[str]] = None) -> int:
    if not Path(main_schema_filename).exists():
        print(f"Main schema file '{main_schema_filename}' doesn't exist, generating it...")
        generate_main_schema(main_schema_filename)

    parser = init_parser()
    args = parser.parse_args(argv)

    validate_arguments(parser, args)

    if args.subcommand == 'gen-models':
        gen_models(parser, args)
    elif args.subcommand == 'gen-rest':
        gen_rest(parser, args)

    return 1


def validate_arguments(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    if args.subcommand == 'gen-models':
        # if not is_valid_filename(args.json_schema):
        #     parser.error(f'--json-schema {args.json_schema} is not a valid filename')
        if args.json_schema == '':
            parser.error('--json-schema is missing required argument')
        elif not is_valid_filepath(args.out_dir):
            parser.error(f'--out-dir {args.out_dir} is not a valid filepath')

    elif args.subcommand == 'gen-rest':
        if args.models == '':
            parser.error('--models is missing required argument')
        if not is_valid_filepath(args.models):
            parser.error(f'--models {args.models} is not a valid filepath')
        elif not is_valid_filepath(args.rest_routes):
            parser.error(f'--rest-routes {args.rest_routes} is not a valid filepath')


def create_output_dir_if_not_exists(path: str) -> None:
    abs_path = Path(path).resolve()
    if not abs_path.is_dir():
        while True:
            print(f"Directory {path} doesn't exist, would you like to create it? (y/n)")
            response = input().lower().strip()
            if response == 'y' or response == 'yes':
                abs_path.mkdir(parents=True)
                break
            elif response == 'n' or response == 'no' or response == 'q' or response == 'quit':
                exit(0)
    init_file = abs_path / '__init__.py'
    if not init_file.exists():
        init_file.touch()


def gen_models(parser: argparse.ArgumentParser, args: argparse.Namespace) -> int:
    create_output_dir_if_not_exists(args.out_dir)

    try:
        with open(main_schema_filename) as main_schema_file, open(args.json_schema) as user_schema_file:
            main_schema = json.load(main_schema_file)
            jsonschema.Draft202012Validator.check_schema(main_schema)

            user_schema = get_user_schema(args.json_schema, user_schema_file)
            jsonschema.Draft202012Validator.check_schema(user_schema)

            if is_subset(user_schema, main_schema):
                generate_model(user_schema, args.json_schema, args.out_dir)
            else:
                print(f"{args.json_schema} is not a subset of {main_schema_filename}")
                return 1

    except FileNotFoundError as fnf:
        parser.error(f"{fnf.filename} not found")
    except json.decoder.JSONDecodeError:
        parser.error(f"{args.json_schema} is not a valid JSON file")
    except jsonschema.exceptions.ValidationError as ve:
        parser.error(ve.message)

    return 0


def gen_rest(parser: argparse.ArgumentParser, args: argparse.Namespace) -> int:
    create_output_dir_if_not_exists(args.rest_routes)
    abs_directory = Path(args.models).resolve()
    print(f"abs_directory: {abs_directory}")
    routers = []
    for path in abs_directory.glob("*.py"):
        if path.name == "__init__.py":
            continue
        print(path.resolve())
        filename = path.name
        try:
            module_name, _ = filename.split(".py")
            kind, _ = module_name.split("Model")
        except ValueError:
            parser.error(f"{path.resolve()} is not a valid model file. The filename must be <ModelKind>Model.py")
            exit(1)
        print(f"filename: {filename}, module_name: {module_name}, kind: {kind}")
        if not filename or not module_name or not kind:
            parser.error(f"{path.resolve()} is not a valid model file. The filename must be <ModelKind>Model.py")
        if not is_valid_python_file(path.resolve()):
            parser.error(f"{path.resolve()} is not a valid Python file")
        model_dir = get_module_dir(abs_directory, module_name)
        print(f"model_dir: {model_dir}")
        values = {
            'model_dir': model_dir,
            'main_model': kind,
            'config_model': 'Configuration',
            'kind': kind.lower(),
        }
        print(f"generating router for {path.resolve()} with values: {values}")
        generate_router(values, kind, args.rest_routes)
        router_dir = get_module_dir(Path(args.rest_routes).resolve(), kind + "Router")
        routers.append((router_dir, kind + "Router"))
    insert_routers_into_init_file(routers)
    return 0


def insert_routers_into_init_file(routers: list[tuple[str, str]]) -> None:
    with open('__init__.py', 'w') as f:
        for router_dir, router in routers:
            f.write(f'from {router_dir} import router as {router}\n')
        f.write(f"\n\n__all__ = [{', '.join(r[1] for r in routers)}]\n")


def get_module_dir(abs_directory: Path, module_name: str) -> str:
    dir_array = abs_directory.parts
    app_index = dir_array.index("app")
    module_dir = ".".join(dir_array[app_index:]) + "." + module_name
    return module_dir


def is_valid_python_file(path: Path) -> bool:
    with open(path) as f:
        source = f.read()
    valid = True
    try:
        ast.parse(source)
    except SyntaxError:
        valid = False
    return valid


def init_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="subcommand", required=True)
    model_subparser = subparsers.add_parser("gen-models", help="Generate model from JSON Schema")

    model_subparser.add_argument(
        "-j", "--json-schema", type=validate_filepath_arg, required=True, help="Path to JSON Schema"
    )
    model_subparser.add_argument(
        "-o", "--out-dir", type=validate_filepath_arg, default="rest/models", help="Output directory to store models"
    )

    rest_subparser = subparsers.add_parser("gen-rest", help="Generate REST API from JSON Schema")

    rest_subparser.add_argument(
        "-m", "--models", type=validate_filepath_arg, required=True, help="Path to models directory"
    )
    rest_subparser.add_argument(
        "-o",
        "--rest-routes",
        type=validate_filepath_arg,
        default="rest/routes",
        help="Output directory to store REST routes",
    )

    return parser


def get_user_schema(filename: str, user_schema_file: TextIO) -> dict:
    if filename.endswith(".yaml"):
        user_schema = yaml.safe_load(user_schema_file)
    else:
        user_schema = json.load(user_schema_file)

    return user_schema


if __name__ == '__main__':
    exit(main())
