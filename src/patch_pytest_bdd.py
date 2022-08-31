"""
This script  patch pytest_bdd.parses to keep @ from tags in Gherkins feature
files. This patch is to have pytest generated proper cucumber results
for Jira Zephyr Scale.
"""
import pytest_bdd
import re

parser_file = open(pytest_bdd.parser.__file__).read()
if 'tag.lstrip("@")' in parser_file:
    parser_patched = re.sub(r'tag.lstrip\("@"\)', 'tag', parser_file)
    save_parser_file = open(pytest_bdd.parser.__file__, 'w')
    save_parser_file.writelines(parser_patched)
    save_parser_file.close()
