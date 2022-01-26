#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
from os import _Environ, environ
from typing import Any, Dict, Union, List
from pathlib import Path
from jsonschema import validate, ValidationError
import logging


def validate_json(json_data, json_schema):
    try:
        logging.error(json_data)
        validate(instance=json_data, schema=json_schema)
    except ValidationError as err:
        logging.error(err)
        raise err


def use_average_embedding() -> bool:
    return props_to_bool("AVERAGE_EMBEDDING", environ)


def use_semantic_deduplication() -> bool:
    return props_to_bool("SEMANTIC_DEDUP", environ)


def extract_alphanumeric(input_string: str) -> str:
    from string import ascii_letters, digits, whitespace

    return "".join(
        [ch for ch in input_string if ch in (ascii_letters + digits + whitespace)]
    )


def get_shared_root() -> str:
    return environ.get("SHARED_ROOT") or "shared"


def file_last_updated_at(file_path: str) -> int:
    return int(Path(file_path).stat().st_mtime)


def normalize_strings(strings: List[str]) -> List[str]:
    ret = []
    for string in strings:
        string = sanitize_string(string)
        ret.append(string)
    return ret


def sanitize_string(input_string: str) -> str:
    input_string = input_string.strip()
    input_string = input_string.casefold()
    input_string = input_string.replace("\u00a0", " ")
    input_string = extract_alphanumeric(input_string)
    return input_string


def props_to_bool(
    name: str, props: Union[Dict[str, Any], _Environ], dft: bool = False
) -> bool:
    if not (props and name in props):
        return dft
    v = props[name]
    return str(v).lower() in ["1", "t", "true"]
