from nbconvert import PythonExporter
from traitlets.config import Config
import nbformat
from typing import Set, List, Tuple
from difflib import Differ


def get_notebook_data(filepath: str) -> str:
    with open(filepath) as f:
        return nbformat.reads(f.read(), as_version=4)


def get_pycode(nb_node: str, removed_tags: Set[str] = set()) -> str:
    c = Config()
    c.TagRemovePreprocessor.remove_cell_tags = removed_tags
    c.TemplateExporter.exclude_input_prompt = True
    c.TemplateExporter.exclude_output_prompt = True
    c.TemplateExporter.exclude_markdown = True

    exporter = PythonExporter(config=c)
    res = exporter.from_notebook_node(nb_node)
    return res[0]


def get_diff_lines(removed: str, full: str) -> List[str]:
    diff = Differ().compare(removed.split('\n'), full.split('\n'))
    return [l[2:] for l in diff if l.startswith('+') and len(l) > 2]


def get_name_and_type(name: str, value: str) -> Tuple[str, str]:
    if ':' not in name:
        if '"' in value or "'" in value:
            return (name, 'str')
        elif '.' in value:
            return (name, 'float')
        elif value.isdigit():
            return (name, 'int')
        else:
            return (name, 'str')
    n, t = [x.strip() for x in name.split(':')]
    return (n, t)


def get_params(param_lines: List[str]) -> str:
    result = ['import argparse', 'parser = argparse.ArgumentParser()']
    for line in param_lines:
        if '=' not in line:
            continue
        name, v = [l.strip() for l in line.split('=')]
        n, t = get_name_and_type(name, v)
        result.append(f"parser.add_argument('--{n}', type={t}, default={v})")
    result.extend([
        'args, _ = parser.parse_known_args()',
        'globals().update(vars(parser.parse_args()))'
    ])

    return '\n'.join(result)


def get_final_code(filepath: str):
    nb_node = get_notebook_data(filepath)
    removed = get_pycode(nb_node, {'parameters', 'sagemaker'})
    full = get_pycode(nb_node, {'sagemaker'})
    params = get_params(get_diff_lines(removed, full))
    return params + '\n' + removed.replace('#!/usr/bin/env python\n# coding: utf-8', '')


print(get_final_code('./Untitled.ipynb'))
