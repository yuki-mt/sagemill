import unittest
from sagemill import Converter
import os


class TestConverter(unittest.TestCase):
    def test_get_diff_lines(self):
        removed = 'foo\nbar'
        full = 'foo\n1234\nbar\nxyz'
        diff_lines = Converter._get_diff_lines(removed, full)
        self.assertEqual(diff_lines, ['1234', 'xyz'])

    def test_get_name_and_type(self):
        n, t = Converter._get_name_and_type('a: int', 'foo')
        self.assertEqual(n, 'a')
        self.assertEqual(t, 'int')

        n, t = Converter._get_name_and_type('myvar', '"foo"')
        self.assertEqual(n, 'myvar')
        self.assertEqual(t, 'str')

        n, t = Converter._get_name_and_type('myvar', "'foo'")
        self.assertEqual(n, 'myvar')
        self.assertEqual(t, 'str')

        n, t = Converter._get_name_and_type('myvar', '123')
        self.assertEqual(n, 'myvar')
        self.assertEqual(t, 'int')

        n, t = Converter._get_name_and_type('myvar', '12.3')
        self.assertEqual(n, 'myvar')
        self.assertEqual(t, 'float')

    def test_get_params(self):
        param_code = Converter._get_params([
            'foo = 100',
            '# some comments',
            'AA = "cc"',
            'B_C: float = 455',
        ])
        self.assertEqual(param_code, (
            "import argparse\n"
            "parser = argparse.ArgumentParser()\n"
            "parser.add_argument('--foo', type=int, default=100)\n"
            "parser.add_argument('--AA', type=str, default=\"cc\")\n"
            "parser.add_argument('--B_C', type=float, default=455)\n"
            "args, _ = parser.parse_known_args()\n"
            "globals().update(vars(args))"
        ))

    def test_get_pycode(self):
        nb_node = Converter._get_notebook_data(
            os.path.join(os.path.dirname(__file__), 'sample.ipynb')
        )
        self.assertEqual(Converter._get_pycode(nb_node), (
            "#!/usr/bin/env python\n"
            "# coding: utf-8\n"
            "A = 101\n"
            "b = 'f'\n"
            "K_K = 3.4\n"
            "f: float = 33.44\n"
            "get_ipython().system('pwd')\n"
            "print(A)\n"
            "get_ipython().system('ls')\n"
            "print(K_K)\n"
            "print(b)\n"
        ))
        self.assertEqual(Converter._get_pycode(nb_node, {'parameters', 'sagemaker'}), (
            "#!/usr/bin/env python\n"
            "# coding: utf-8\n"
            "get_ipython().system('pwd')\n"
            "print(A)\n"
            "get_ipython().system('ls')\n"
            "print(K_K)\n"
        ))

    def test_modify_shell(self):
        code = (
            "K_K = 3.4\n"
            "get_ipython().system('pwd')\n"
            "print(A)\n"
            "get_ipython().system('ls')\n"
        )
        self.assertEqual(Converter._modify_shell(code, do_remove=True), (
            "K_K = 3.4\n"
            "print(A)\n"
        ))
        self.assertEqual(Converter._modify_shell(code, do_remove=False), (
            "import subprocess\n"
            "K_K = 3.4\n"
            "subprocess.run('pwd', shell=True)\n"
            "print(A)\n"
            "subprocess.run('ls', shell=True)\n"
        ))

    def test_get_code(self):
        filepath = os.path.join(os.path.dirname(__file__), 'sample.ipynb')
        self.assertEqual(Converter.get_code(filepath), (
            "import argparse\n"
            "parser = argparse.ArgumentParser()\n"
            "parser.add_argument('--A', type=int, default=101)\n"
            "parser.add_argument('--b', type=str, default='f')\n"
            "parser.add_argument('--K_K', type=float, default=3.4)\n"
            "parser.add_argument('--f', type=float, default=33.44)\n"
            "args, _ = parser.parse_known_args()\n"
            "globals().update(vars(args))\n"
            "\n"
            "print(A)\n"
            "print(K_K)\n"
        ))
        self.assertEqual(Converter.get_code(filepath, remove_shell_command=False), (
            "import subprocess\n"
            "import argparse\n"
            "parser = argparse.ArgumentParser()\n"
            "parser.add_argument('--A', type=int, default=101)\n"
            "parser.add_argument('--b', type=str, default='f')\n"
            "parser.add_argument('--K_K', type=float, default=3.4)\n"
            "parser.add_argument('--f', type=float, default=33.44)\n"
            "args, _ = parser.parse_known_args()\n"
            "globals().update(vars(args))\n"
            "\n"
            "subprocess.run('pwd', shell=True)\n"
            "print(A)\n"
            "subprocess.run('ls', shell=True)\n"
            "print(K_K)\n"
        ))

    def test_process_args(self):
        args = Converter.process_args({'foo': 12, 'base': '/a/b'})
        self.assertEqual(args, ['--foo', '12', '--base', '/a/b'])
