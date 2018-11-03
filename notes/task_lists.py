import re


def compute_task_counts(text):
    """
    This closely mirrors the markdown2 implementation at
    https://github.com/trentm/python-markdown2/blob/master/lib/markdown2.py#L1657
    """
    task_list_item_re = re.compile(r'''
        ^\s* [*-] \s+
        (\[[\ x]\])
        [ \t]+.
    ''', re.X | re.M | re.S)

    total = 0
    completed = 0

    for line in text.splitlines():
        for m in task_list_item_re.finditer(line):
            marker = m.group(1)
            total = total + 1

            if marker == '[x]':
                completed = completed + 1

    return completed, total
