"""
This module makes it possible to batch execute almost every program that runs from command line
on files in input directory and outputs those into output directory (include directory structure).
Settings are taken from config.json file. In the future there will be new features added.
"""

# Version of Module
__version__ = '0.0.5'

import argparse
import datetime
import subprocess
import json
import shutil
import pathlib


class UniversalBatchExecuter:
    input_dir = pathlib.Path('input')
    include_subdirs = True
    dir_mask = '*'
    file_masks = '*.*'
    output_dir = pathlib.Path('output')
    app_dir = pathlib.Path('app')
    app_name = app_dir / pathlib.Path('app.exe')
    app_args = ''
    app_input_parameter = ''
    app_output_parameter = '-o'
    app_output_file_extension = ''
    replace_files = True
    replaced_files_backup = True
    output_to = pathlib.Path('stdout.log')
    error_output_to = pathlib.Path('stderr.log')

    def __init__(self, config_file_name='config.json'):
        config_file_name = pathlib.Path(config_file_name)
        if not config_file_name.is_file():
            raise IOError(
                f'the config file: {config_file_name} does NOT exist. Create it based on documentation and run again.'
            )
        else:
            with open(config_file_name, 'r') as config_file:
                data = json.load(config_file)
                data_or_error_msg = self.process_data(data)
                if isinstance(data_or_error_msg, dict):
                    self.__dict__.update(data_or_error_msg)
                else:
                    raise ValueError(data_or_error_msg)

    def process_data(self, data):
        error_msg = ''
        data['input_dir'] = pathlib.Path(data['input_dir']).resolve()
        if not data['input_dir'].is_dir():
            error_msg += f'Input dir: "{data["input_dir"]}" does NOT exist.\n'
        data['include_subdirs'] = data.get('include_subdirs', True)
        if not isinstance(data['include_subdirs'], bool):
            error_msg += f'include_subdirs option: "{data["include_subdirs"]}" should be true or false.\n'
        data['dir_mask'] = data.get('dir_mask', '*')
        if not isinstance(data['dir_mask'], str):
            error_msg += f'dir_mask option: "{data["dir_mask"]}" should be a string.\n'
        data['file_masks'] = data.get('file_masks', ['*.*'])
        if not isinstance(data['file_masks'], list) and all(
            isinstance(file_mask, str) for file_mask in data['file_masks']
        ):
            error_msg += f'file_masks option: "{data["file_masks"]}" should be a list of strings.\n'
        data['output_dir'] = pathlib.Path(data.get('output_dir', 'output')).resolve()
        if not data['output_dir'].is_dir():
            data['output_dir'].mkdir(parents=True, exist_ok=True)
        data['app_dir'] = pathlib.Path(data.get('app_dir', 'app')).resolve()
        if not data['app_dir'].is_dir():
            error_msg += f'App dir: "{data["app_dir"]}" does NOT exist.\n'
        data['app_name'] = (data['app_dir'] / pathlib.Path(data.get('app_name', 'app.exe'))).resolve()
        if not data['app_name'].is_file():  # todo: add data['app_full_path']
            error_msg += f'App name: "{data["app_name"]}" does NOT exist.\n'
        data['app_args'] = data.get('app_args', '')
        if not isinstance(data['app_args'], str):
            error_msg += f'Application arguments (app_args): "{data["app_args"]}" should be a string.\n'
        data['app_input_parameter'] = data.get('app_input_parameter', '')
        if not isinstance(data['app_input_parameter'], str):
            error_msg += f'Application input parameter(app_input_parameter): "{data["app_input_parameter"]}" '
            'should be a string.\n'
        data['app_output_parameter'] = data.get('app_output_parameter', '-o')
        if not isinstance(data['app_output_parameter'], str):
            error_msg += f'Application output parameter(app_output_parameter): "{data["app_output_parameter"]}" '
            'should be a string.\n'
        data['app_output_file_extension'] = data.get('app_output_file_extension', '')
        if not isinstance(data['app_output_file_extension'], str):
            error_msg += f'Output file extension (app_output_file_extension): "{data["app_output_file_extension"]}" '
            'should be a string.\n'
        if data['app_output_file_extension'][0] != '.':
            data['app_output_file_extension'] = '.' + data['app_output_file_extension']
        data['replace_files'] = data.get('replace_files', True)
        if not isinstance(data['replace_files'], bool):
            error_msg += f'replace_files option: "{data["replace_files"]}" should be true or false.\n'
        data['replaced_files_backup'] = data.get('replaced_files_backup', True)
        if not isinstance(data['replaced_files_backup'], bool):
            error_msg += f'replaced_files_backup option: "{data["replaced_files_backup"]}" should be true or false.\n'
        data['output_to'] = data.get('output_to', 'stdout.log')

        if not isinstance(data['output_to'], str):
            error_msg += f'Output stream (output_to): "{data["output_to"]}" should be a string.\n'

        data['output_to'] = pathlib.Path(data['output_to']).resolve()
        data['error_output_to'] = data.get('error_output_to', 'stderr.log')

        if not isinstance(data['error_output_to'], str):
            error_msg += f'Error output stream (error_output_to): "{data["error_output_to"]}" should be a string.\n'

        data['error_output_to'] = pathlib.Path(data['error_output_to']).resolve()
        return data if not error_msg else error_msg

    def run(self, additional_args=''):
        subdirs = '**/' if self.include_subdirs else ''
        file_stdout = open(self.output_to, 'a+', encoding='utf8')
        file_stdout.write(80 * '=' + '\n')
        file_stdout.write((datetime.datetime.now()).strftime('%d/%m/%Y %H:%M:%S') + '\n')
        # todo: use option is_append or sth to choose whether append or overwrite log files
        file_stderr = open(self.error_output_to, 'a+', encoding='utf8')
        file_stderr.write(80 * '=' + '\n')
        file_stderr.write((datetime.datetime.now()).strftime('%d/%m/%Y %H:%M:%S') + '\n')
        # todo: case sensitive file masks
        files = []
        for file_mask in self.file_masks:
            files.extend(self.input_dir.glob(subdirs + file_mask))
        for f in files:
            relative_file_path = f.relative_to(self.input_dir)
            if self.app_output_file_extension:
                output_file_path = self.output_dir.joinpath(relative_file_path).with_suffix(
                    self.app_output_file_extension
                )
            else:
                output_file_path = self.output_dir.joinpath(relative_file_path)
            relative_output_dir_path = output_file_path.parent
            if not relative_output_dir_path.exists():
                relative_output_dir_path.mkdir(parents=True, exist_ok=True)
            if output_file_path.is_file() and not self.replace_files:
                continue
            if output_file_path.is_file() and self.replaced_files_backup:
                suffix = output_file_path.suffixes[-1] + '.bak'
                shutil.move(output_file_path, output_file_path.with_suffix(suffix))
            print(f'processing file: {f}')
            print(40 * '-', file=file_stdout)
            print(40 * '-', file=file_stderr)
            process = subprocess.Popen(
                [
                    self.app_name,
                    *self.app_args.split(),
                    *additional_args.split(),
                    self.app_input_parameter,
                    f,
                    self.app_output_parameter,
                    output_file_path,
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False,
                universal_newlines=True,
            )
            while True:
                outs = process.stdout.readline()
                errs = process.stderr.readline()
                if process.poll() is not None:
                    break
                if outs:
                    print(outs.strip(), file=file_stdout)
                if errs:
                    print(errs.strip(), file=file_stderr)
            cmd_string = subprocess.list2cmdline(process.args)
            print(f'the commandline: {cmd_string}', file=file_stdout)
            print(f'the commandline: {cmd_string}', file=file_stderr)
        file_stdout.close()
        file_stderr.close()


if __name__ == 'main':

    parser = argparse.ArgumentParser(
        description='Execute batch command on every selected file from the input_dir'
        'folder with options from configuration file.'
    )
    parser.add_argument(
        'config_file', default='config.json', help='file with config parameters to batch execute command.'
    )
    parser.add_argument('-p', '--parameters', help='optional additional app parameters.')
    args = parser.parse_args()
    print(args)
    batch_executer = UniversalBatchExecuter(config_file_name=args.config_file)
    batch_executer.run()
