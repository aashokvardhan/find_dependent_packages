import os
import json
import argparse
import subprocess
from collections import defaultdict

import yaml

depend_package = defaultdict(dict)

def start_env():
    subprocess.Popen(["virtualenv", "venv"], stdout=subprocess.PIPE).communicate()
    subprocess.Popen(["venv/bin/activate"], stdout=subprocess.PIPE).communicate()

def end_env():
    subprocess.Popen(["deactivate"], stdout=subprocess.PIPE).communicate()


def install_package(package_name):
    pip_install = subprocess.Popen(["pip3", "install", '-U', package_name],
                                   stdout=subprocess.PIPE)

    _ = pip_install.communicate()

def get_pipdeptree():
    pip_pipdeptree = subprocess.Popen(["pipdeptree", "--json-tree"], stdout=subprocess.PIPE)

    return json.loads(pip_pipdeptree.communicate()[0])

def get_dependencies(input_data):
    child_package = input_data['package_name']
    child_required_version = input_data['required_version']

    if child_package not in depend_package:
        depend_package[child_package] = {child_required_version: []}

    dependencies = input_data['dependencies']

    for dependency in dependencies:
        parent_package = dependency['package_name']
        parent_required_version = dependency['required_version']
        if parent_package in depend_package:
            if parent_required_version in depend_package[parent_package]:
                if child_package not in depend_package[parent_package][parent_required_version]:
                    depend_package[parent_package][parent_required_version].append(child_package)
            else:
                depend_package[parent_package][parent_required_version] = [child_package]
        else:
            depend_package[parent_package] = {parent_required_version:[child_package]}
        
        get_dependencies(dependency)
    

if __name__ == '__main__':
    
    subprocess.Popen("virtualenv venv", shell=True)
    subprocess.Popen("source venv/bin/activate", shell=True)
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Find packages dependency for given package.')
    parser.add_argument('--package',
                        required=True,
                        help='Package whose dependency is required')
    parser.add_argument('--version',
                        required=True,
                        help='Package version dependency is required')
    parser.add_argument('--ymlfile',
                        required=True,
                        help='Location of yml file')

    args = parser.parse_args()

    if not os.path.isfile(args.ymlfile):
        print(args.ymlfile)
        raise ValueError('YML file not found')

    input_package_name = args.package + '==' + args.version

    install_package(input_package_name)

    output_lists = get_pipdeptree()

    found = False
    for i in output_lists:
        package = i['package_name']
        version = i['required_version']
        if package == args.package and version == args.version:
            found = True 
            desired_package = i
            break 

    if not found:
        raise ValueError("specified package not found")

    get_dependencies(desired_package)

    with open(args.ymlfile) as f:
        # use safe_load instead load
        dataMap = yaml.safe_load(f)

    if dataMap is not None and 'packages' in dataMap:

        for package in dataMap['packages'].keys():
            versions_to_delete = []
            if package in depend_package:
                for version in depend_package[package]:
                    if version in dataMap['packages'][package]['versions']:
                        versions_to_delete.append(version)

                for version in versions_to_delete:
                    del depend_package[package][version]

    print(depend_package)
    subprocess.Popen("exit", shell=True)






