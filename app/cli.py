import argparse
import json
from pathlib import Path
from typing import Optional, TextIO

import jsonschema
import yaml

from app.utils.main_schema_gen import generate_main_schema
from app.utils.model_generator import generate_model
from app.utils.schema_validate import is_subset

main_schema_filename = "schemas/main_schema.json"


def main(argv: Optional[list[str]] = None) -> int:
    if not Path(main_schema_filename).exists():
        print(f"Main schema file '{main_schema_filename}' doesn't exist, generating it...")
        generate_main_schema(main_schema_filename)

    parser = init_parser()
    args = parser.parse_args(argv)

    if args.subcommand == 'gen-models':
        return gen_models(parser, args)
    elif args.subcommand == 'gen-rest':
        return gen_rest(parser, args)

    return 1


def gen_models(parser: argparse.ArgumentParser, args: argparse.Namespace) -> int:
    if args.json_schema == '':
        parser.error('--json-schema is missing required argument')
    if not Path(args.out_dir).is_dir():
        while True:
            print(f"Directory {args.out_dir} doesn't exist, would you like to create it? (y/n)")
            response = input().lower().strip()
            if response == 'y' or response == 'yes':
                Path(args.json_schema).mkdir(parents=True)
                break
            elif response == 'n' or response == 'no' or response == 'q' or response == 'quit':
                return 0

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
    # TODO: Implement REST generator

    return 0


def init_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="subcommand", required=True)
    model_subparser = subparsers.add_parser("gen-models", help="Generate model from JSON Schema")

    model_subparser.add_argument("-j", "--json-schema", type=str, required=True, help="Path to JSON Schema")
    model_subparser.add_argument(
        "-o", "--out-dir", type=str, default="rest/models", help="Output directory to store models"
    )

    rest_subparser = subparsers.add_parser("gen-rest", help="Generate REST API from JSON Schema")

    rest_subparser.add_argument("-m", "--models", type=str, required=True, help="Path to models directory")
    rest_subparser.add_argument(
        "-o", "--rest-routes", type=str, default="rest/routes", help="Output directory to store REST routes"
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
