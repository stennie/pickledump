import os
import pickle

import pytest
from click.testing import CliRunner

from pickledump import pickle_cli


class Animal:
    """Custom class used in the test pickles."""


@pytest.fixture
def runner():
    return CliRunner()


def _dump(path, obj, protocol):
    with open(path, 'wb') as f:
        pickle.dump(obj, f, protocol=protocol)
    return str(path)


def test_summary_reports_file_size_and_pickle_protocol(runner, tmp_path):
    path = tmp_path / 'data.pkl'
    obj = {"answer": 42}
    with open(path, 'wb') as f:
        pickle.dump(obj, f, protocol=5)

    result = runner.invoke(pickle_cli, ['--summary', str(path)])

    assert result.exit_code == 0
    assert f"  Size:              {path.stat().st_size} bytes" in result.output
    assert "  Pickle protocol:   5" in result.output
    assert "  Operations:" in result.output


@pytest.mark.parametrize(
    'protocol,expected_protocol_line',
    [
        (0, '  Pickle protocol:   0'),
        (1, '  Pickle protocol:   1'),
        (2, '  Pickle protocol:   2'),
        (3, '  Pickle protocol:   3'),
        (4, '  Pickle protocol:   4'),
        (5, '  Pickle protocol:   5'),
    ],
)
def test_summary_detects_pickle_protocol(runner, tmp_path, protocol, expected_protocol_line):
    path = _dump(tmp_path / f'data_proto{protocol}.pkl', {"answer": 42}, protocol=protocol)

    result = runner.invoke(pickle_cli, ['--summary', path])

    assert result.exit_code == 0
    assert expected_protocol_line in result.output


def test_summary_reports_custom_object_classes(runner, tmp_path):
    path = _dump(tmp_path / 'custom.pkl', Animal(), protocol=5)

    result = runner.invoke(pickle_cli, ['--summary', path])

    assert result.exit_code == 0
    assert "Custom object classes:" in result.output
    assert "Animal" in result.output


def test_summary_no_custom_object_classes_for_plain_data(runner, tmp_path):
    path = _dump(tmp_path / 'plain.pkl', {"answer": 42}, protocol=4)

    result = runner.invoke(pickle_cli, ['--summary', path])

    assert result.exit_code == 0
    assert "Custom object classes:" not in result.output


def test_summary_multiple_files(runner, tmp_path):
    path_a = _dump(tmp_path / 'a.pkl', {"answer": 42}, protocol=2)
    path_b = _dump(tmp_path / 'b.pkl', [1, 2, 3], protocol=3)

    result = runner.invoke(pickle_cli, ['--summary', path_a, path_b])

    assert result.exit_code == 0
    assert f"File: {path_a}" in result.output
    assert f"File: {path_b}" in result.output
    assert "Pickle protocol:   2" in result.output
    assert "Pickle protocol:   3" in result.output


def test_summary_invalid_file(runner, tmp_path):
    path = tmp_path / 'invalid.pkl'
    path.write_bytes(b'this is not a pickle at all')

    result = runner.invoke(pickle_cli, ['--summary', str(path)])

    assert result.exit_code == 0
    assert "Error summarising" in result.output


def test_summary_writes_to_output_file(runner, tmp_path):
    path = _dump(tmp_path / 'data.pkl', {"answer": 42}, protocol=5)
    output_path = tmp_path / 'summary.txt'

    result = runner.invoke(
        pickle_cli,
        ['--summary', '-o', str(output_path), str(path)]
    )

    assert result.exit_code == 0
    assert f"  Size:              {os.path.getsize(path)} bytes" in output_path.read_text()
    assert "Pickle protocol:   5" in output_path.read_text()


def test_summary_single_file_includes_filename(runner, tmp_path):
    path = _dump(tmp_path / 'data.pkl', {"answer": 42}, protocol=2)

    result = runner.invoke(pickle_cli, ['--summary', str(path)])

    assert result.exit_code == 0
    assert f"File: {path}" in result.output
    assert "Pickle protocol:   2" in result.output


def test_dump_prints_object(runner, tmp_path):
    path = _dump(tmp_path / 'data.pkl', {"answer": 42}, protocol=4)

    result = runner.invoke(pickle_cli, ['--dump', str(path)])

    assert result.exit_code == 0
    assert "'answer': 42" in result.output


def test_default_mode_is_summary(runner, tmp_path):
    path = _dump(tmp_path / 'data.pkl', {"answer": 42}, protocol=4)

    result = runner.invoke(pickle_cli, [str(path)])

    assert result.exit_code == 0
    assert "Pickle protocol:   4" in result.output
    assert "Custom object classes:" not in result.output


def test_disassemble_works(runner, tmp_path):
    path = _dump(tmp_path / 'data.pkl', {"answer": 42}, protocol=4)

    result = runner.invoke(pickle_cli, ['--disasm', str(path)])

    assert result.exit_code == 0
    assert 'PROTO' in result.output


def test_disasm_short_flag_alias(runner, tmp_path):
    path = _dump(tmp_path / 'data.pkl', {"answer": 42}, protocol=4)

    result = runner.invoke(pickle_cli, ['--disasm', str(path)])

    assert result.exit_code == 0
    assert 'PROTO' in result.output


def test_disasm_short_flag_alias_short_form(runner, tmp_path):
    path = _dump(tmp_path / 'data.pkl', {"answer": 42}, protocol=4)

    result = runner.invoke(pickle_cli, ['-x', str(path)])

    assert result.exit_code == 0
    assert 'PROTO' in result.output


def test_dump_short_flag_alias(runner, tmp_path):
    path = _dump(tmp_path / 'data.pkl', {"answer": 42}, protocol=4)

    result = runner.invoke(pickle_cli, ['--dump', str(path)])

    assert result.exit_code == 0
    assert "'answer': 42" in result.output