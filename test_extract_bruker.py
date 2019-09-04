from unittest.mock import MagicMock
import zipfile

import pytest

import extract_bruker


def test_extract_bruker_text(tmpdir):
    subject = tmpdir.join('subject')
    subject.write(bruker_sample)
    context = MagicMock()
    context.get_input_path.return_value = str(subject)

    extract_bruker.main(context)

    context.get_input_path.assert_called_once_with('bruker_file')
    context.update_file_metadata.assert_called_once_with(
        subject.basename, info={'header': {'subject': bruker_parsed}})


def test_extract_bruker_invalid_zip(tmpdir):
    pv6_zip = tmpdir.join('test.pv6.zip')
    with zipfile.ZipFile(str(pv6_zip), mode='w') as zf:
        with zf.open('test', mode='w') as text:
            text.write(b'test')
    context = MagicMock()
    context.get_input_path.return_value = str(pv6_zip)
    context.work_dir = str(tmpdir.mkdir('work_dir'))

    with pytest.raises(SystemExit):
        extract_bruker.main(context)


def test_extract_bruker_zip(tmpdir):
    pv6_zip = tmpdir.join('test.pv6.zip')
    with zipfile.ZipFile(str(pv6_zip), mode='w') as zf:
        with zf.open('acqp', mode='w') as acqp:
            acqp.write(bruker_sample.encode('utf8'))
        with zf.open('method', mode='w') as method:
            method.write(bruker_sample.encode('utf8'))
    context = MagicMock()
    context.get_input_path.return_value = str(pv6_zip)
    context.work_dir = str(tmpdir.mkdir('work_dir'))

    extract_bruker.main(context)

    context.get_input_path.assert_called_once_with('bruker_file')
    context.update_file_metadata.assert_called_once_with(
        pv6_zip.basename, info={'header': {'acqp': bruker_parsed,
                                           'method': bruker_parsed}})


bruker_parsed = {'TOP_KEY': 'TEST', 'KEY_ONE': 'One', 'KEY_TWO': 'Two', 'END': ''}
bruker_sample = '''
##TOP_KEY=TEST
##$KEY_ONE=One
##$KEY_TWO=( 1 )
Two
##END=
'''
