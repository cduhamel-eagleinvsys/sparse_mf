#!/usr/bin/env python3

import os
import yaml
import sys
from subprocess import check_call
from subprocess import SubprocessError


def run_and_forward_error(cmd):
    try:
        check_call(cmd)
    except SubprocessError as run_err:
        sys.exit(run_err)


if __name__ == '__main__':
    curr_path = os.path.dirname(os.path.realpath(__file__))
    file = os.path.join(curr_path, os.path.splitext(os.path.basename(__file__))[0]) + '.yml'
    try:
        with open(file, 'r') as yml:
            try:
                yml = yaml.safe_load(yml)
                repo = yml['repo']
                clone = ['git', 'clone', '-n', repo]
                d = yml['directory']
                if d:
                    d = os.path.abspath(str(d))
                    clone.append(d)
                else:
                    try:
                        i = repo.rindex('/', 0, len(repo) - 2)
                    except ValueError:
                        sys.exit('/ character not found in repo url')
                    d = repo[i + 1:]
                run_and_forward_error(clone)
                curr_path = os.path.join(os.getcwd(), d)
                try:
                    os.chdir(curr_path)
                except EnvironmentError as chdir_err:
                    sys.exit('Error moving to folder ' + curr_path + ': ' + chdir_err.strerror)
                run_and_forward_error(['git', 'config', 'lfs.url', yml['lfs']])
                run_and_forward_error(['git', 'config', 'core.sparseCheckout', 'true'])
                try:
                    with open('.git/info/sparse-checkout', 'w+') as sparse:
                        for p in yml['sparse']:
                            sparse.write('\n' + p)
                        sparse.write('\n')
                    run_and_forward_error(['git', 'checkout', '-f', 'HEAD'])
                except EnvironmentError as sparse_err:
                    sys.exit('Error writing to .git/info/sparse-checkout: ' + sparse_err.strerror)
            except yaml.YAMLError as yml_err:
                sys.exit(yml_err)
    except EnvironmentError as file_err:
        sys.exit('Error reading from ' + file + ': ' + file_err.strerror)
