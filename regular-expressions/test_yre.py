import pytest
import yre


@pytest.mark.parametrize(['pattern', 'string', 'groups'], [
    ('test',
        'test',
        ('test',)),

    ('(test)',
        'test',
        ('test', 'test')),
])
def test_stuff(pattern, string, groups):
    expression = yre.compile(pattern)
    match = expression.match(string)
    assert match, '%r did not match %r' % (pattern, string)
    assert match.groups() == groups
