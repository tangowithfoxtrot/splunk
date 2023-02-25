#!/usr/bin/env python3

"""
./build.py --task build --os all --version 1.0.0 --tar
"""

import os
import argparse
import shutil

# Setup

parser = argparse.ArgumentParser()
parser.add_argument(
    '--task',
    default='',
    help='Task to execute: build or clean.')
parser.add_argument(
    '--os',
    default='',
    help='Operating system: all, lin, mac, or win.')
parser.add_argument('--output', default='', help='Output directory.')
parser.add_argument('--tar', action='store_true', help='Create tar file.')
parser.add_argument(
    '--version',
    default='',
    help='Version of the application.')
args = parser.parse_args()

if not args.output:
    script_path = os.path.abspath(__file__)
    dir_path = os.path.dirname(script_path)
    output_dir = os.path.join(dir_path, 'build')
else:
    output_dir = args.output

win_rids = ["win-x64", "win-x86"]
lin_rids = ["linux-x64", "linux-musl-x64", "linux-arm", "linux-arm64"]
mac_rids = ["osx-x64", "osx.11.0-arm64", "osx.12-arm64"]
all_rids = win_rids + lin_rids + mac_rids

# Functions

def get_os_rids():
    rids = []
    if args.os == 'all':
        rids = all_rids
    if args.os == 'lin':
        rids = lin_rids
    elif args.os == 'mac':
        rids = mac_rids
    elif args.os == 'win':
        rids = win_rids
    else:
        print('ERROR: "os" param should be all, lin, mac, or win.')
    return rids

def build_app():
    rids = get_os_rids()
    for rid in rids:
        app_out = os.path.join(output_dir, 'app', rid, 'bitwarden_event_logs')
        app_bin_out = os.path.join(app_out, 'bin')
        app_lib_out = os.path.join(app_out, 'lib', 'Bitwarden_Splunk')
        shutil.rmtree(app_out, ignore_errors=True)

        print(f'### Building app for {rid} to {app_out}')
        shutil.copytree(
            os.path.join(
                dir_path,
                'app',
                'bitwarden_event_logs'),
            app_out)

        os.makedirs(app_lib_out, exist_ok=True)
        os.makedirs(app_bin_out, exist_ok=True)
        shutil.copy(
            os.path.join(
                dir_path,
                'src/Splunk/program.py'),
            os.path.join(
                app_bin_out,
                'program.py'))
        shutil.rmtree(os.path.join(app_lib_out, 'bin'), ignore_errors=True)
        shutil.rmtree(os.path.join(app_lib_out, 'obj'), ignore_errors=True)

        if 'win' in rid:
            with open(os.path.join(app_out, 'default', 'inputs.conf'), 'r+') as f:
                content = f.read()
                f.seek(0)
                f.write(
                    content.replace(
                        'Bitwarden_Splunk',
                        'Bitwarden_Splunk.exe'))

        if args.version:
            with open(os.path.join(app_out, 'default', 'app.conf'), 'r+') as f:
                content = f.read()
                f.seek(0)
                f.write(
                    content.replace(
                        'version = 1.0.0',
                        'version = %s' % args.version))

def tar_app():
    rids = get_os_rids()
    for rid in rids:
        app_out = os.path.join(output_dir, 'app', rid)
        app_tar_out = os.path.join(
            output_dir, 'app', rid, 'bitwarden_event_logs.tar.gz')
        shutil.rmtree(app_tar_out, ignore_errors=True)
        print(f'### Creating tar for {rid} to {app_out}.tar.gz')
        shutil.make_archive(app_out, 'gztar', app_out)

def clean():
    shutil.rmtree(output_dir, ignore_errors=True)

# Main


if args.task == 'build':
    build_app()
if args.tar:
    tar_app()
elif args.task == 'clean':
    clean()
else:
    print('ERROR: "task" param should be build or clean.')
