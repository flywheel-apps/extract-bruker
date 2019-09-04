#!/usr/bin/env python3
"""Extract header metadata from Bruker ParaVision subject/acqp/method files."""
import glob
import logging
import os
import sys
import zipfile

import flywheel
from flywheel_migration import bruker


log = logging.getLogger('flywheel:extract-bruker')


def main(context):
    bruker_filepath = context.get_input_path('bruker_file')
    bruker_filename = os.path.basename(bruker_filepath)

    if bruker_filepath.endswith('.zip'):
        log.info('Extracting zipped Bruker file "%s"', bruker_filename)
        with zipfile.ZipFile(bruker_filepath) as zf:
            zf.extractall(context.work_dir)
        filepaths = []
        for filename in ('acqp', 'method'):
            filepath = os.path.join(context.work_dir, filename)
            if not os.path.exists(filepath):
                log.error('Invalid Bruker zip: "%s" file not found', filename)
                sys.exit(1)
            filepaths.append(filepath)
    else:
        filepaths = [bruker_filepath]

    file_metadata = {'info': {'header': {}}}
    for filepath in filepaths:
        filename = os.path.basename(filepath)
        log.info('Parsing file "%s"', filename)
        with open(filepath, mode='rt') as f:
            params = bruker.parse_bruker_params(f)
        log.info('Setting file.info.header.%s', filename)
        file_metadata['info']['header'][filename] = params

    log.info('Saving extracted metadata')
    context.update_file_metadata(bruker_filename, **file_metadata)


if __name__ == '__main__':  # pragma: no cover
    with flywheel.GearContext() as context:
        context.init_logging()
        context.log_config()
        main(context)
