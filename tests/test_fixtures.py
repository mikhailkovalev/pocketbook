import pytest


def test_spam_fixture(
        testdir,
):
    testdir.makeini(
        '[pytest]\n'
        'addopts = -p no:django -s -vv\n'
    )
    testdir.makeconftest(
        'pytest_plugins = ["pytester", "tests.fixtures.fixtures"]\n'
    )
    testdir.makepyfile(
        'import pytest\n'
        '\n'
        '@pytest.mark.parametrize("spam", ("eggs",), indirect=True)\n'
        'def test_spam_parametrized(spam):\n'
        '    assert spam == "eggs"\n'
        '\n'
        'def test_spam_no_params(spam):\n'
        '    pass\n'
    )
    result = testdir.runpytest()
    result.assert_outcomes(passed=1, errors=1)

