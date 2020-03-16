from nbconvert import PythonExporter
from traitlets.config import Config
import nbformat
from typing import Set, List, Tuple, Dict
from difflib import Differ
import re


class Converter:
    @classmethod
    def _get_notebook_data(cls, filepath: str) -> str:
        with open(filepath) as f:
            return nbformat.reads(f.read(), as_version=4)

    @classmethod
    def _get_pycode(cls, nb_node: str, removed_tags: Set[str] = set()) -> str:
        c = Config()
        c.TagRemovePreprocessor.remove_cell_tags = removed_tags
        c.TemplateExporter.exclude_input_prompt = True
        c.TemplateExporter.exclude_output_prompt = True
        c.TemplateExporter.exclude_markdown = True

        exporter = PythonExporter(config=c)
        code, _ = exporter.from_notebook_node(nb_node)
        code = re.sub('\n+', '\n', code)
        return code

    @classmethod
    def _get_diff_lines(cls, removed: str, full: str) -> List[str]:
        diff = Differ().compare(removed.split('\n'), full.split('\n'))
        return [l[2:] for l in diff if l.startswith('+') and len(l) > 2]

    @classmethod
    def _get_name_and_type(cls, name: str, value: str) -> Tuple[str, str]:
        if ':' in name:
            n, t = [x.strip() for x in name.split(':')]
            return (n, t)
        else:
            if '"' in value or "'" in value:
                return (name, 'str')
            elif '.' in value:
                return (name, 'float')
            elif value.isdigit():
                return (name, 'int')
            else:
                return (name, 'str')

    @classmethod
    def _get_params(cls, param_lines: List[str]) -> str:
        result = ['import argparse', 'parser = argparse.ArgumentParser()']
        for line in param_lines:
            if '=' not in line:
                continue
            if line.strip().startswith('#'):
                continue
            name, v = line.split('=')
            name = name.strip()
            v = v.split('#')[0].strip()  # for inline comment
            n, t = cls._get_name_and_type(name, v)
            result.append(f"parser.add_argument('--{n}', type={t}, default={v})")
        result.extend([
            'args, _ = parser.parse_known_args()',
            'globals().update(vars(args))'
        ])

        return '\n'.join(result)

    @classmethod
    def _modify_shell(cls, code: str, do_remove: bool) -> str:
        # remove or replace shell command ("!") in notebook
        prefix = '' if do_remove else 'import subprocess\n'
        ptn = re.compile(r"get_ipython\(\).system\((.+)\)\n")
        after = '' if do_remove else r'subprocess.run(\1, shell=True)\n'
        return prefix + ptn.sub(after, code)

    @classmethod
    def get_code(cls, filepath: str, remove_shell_command: bool = True) -> str:
        nb_node = cls._get_notebook_data(filepath)
        removed = cls._get_pycode(nb_node, {'parameters', 'sagemaker'})
        full = cls._get_pycode(nb_node, {'sagemaker'})
        params = cls._get_params(cls._get_diff_lines(removed, full))

        removed = removed.replace('#!/usr/bin/env python\n# coding: utf-8', '')
        return cls._modify_shell(f"{params}\n{removed}", remove_shell_command)

    @classmethod
    def generate_pyfile(cls, src: str, dest: str) -> None:
        code = cls.get_code(src)
        with open(dest, 'w') as f:
            f.write(code)

    @classmethod
    def process_args(cls, params: Dict) -> List[str]:
        result = []
        for k, v in params.items():
            result.extend([f'--{k}', str(v)])
        return result
