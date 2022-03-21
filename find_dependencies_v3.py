import argparse
import os
import subprocess
from collections import defaultdict

import yaml


def install_package(package_name):
    pip_install = subprocess.Popen(["pip", "install", '-U', package_name],
                                   stdout=subprocess.PIPE)

    _ = pip_install.communicate()


def get_pipdeptree():
    pip_pipdeptree = subprocess.Popen(["pipdeptree"], stdout=subprocess.PIPE)

    return str(pip_pipdeptree.communicate()[0].decode('utf-8')).split('\r\n')


def get_level(input_data):
    input_split = input_data.split(' ')

    level = 0
    if '-' in input_split:
        level = input_split.index('-') // 2
    return level


def get_package_name_version(package_atri):

    input_split = package_atri.split(' ')
    version = 'Any'

    if '-' in input_split:
        package_name = input_split[input_split.index('-') + 1]
    else:
        package_name = input_split[0]

    if '[required:' in input_split:
        version = input_split[input_split.index('[required:') +
                              1].split(',')[0]

    return package_name, version


parents = []
package_dict = defaultdict(list)
dependencies = defaultdict(dict)


def get_packages(input_list, ind):

    level = get_level(input_list[ind])
    parent, parent_version = get_package_name_version(input_list[ind])
    parents.append(parent)

    while ind + 1 < len(input_list):
        new_level = get_level(input_list[ind + 1])

        if new_level == level + 2:
            ind = get_packages(input_list, ind)
        elif new_level == level:
            parents.pop()
            return ind - 1
        elif new_level == level + 1:
            package_name, version = get_package_name_version(input_list[ind +
                                                                        1])
            if parents[-1] not in package_dict[(package_name, version)]:
                package_dict[(package_name, version)].append(parents[-1])
        else:
            while len(parents) > new_level + 1:
                parents.pop()
            return ind - 1
            #raise ValueError('value error')

        ind += 1
    return ind + 1


if __name__ == '__main__':

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

    if not os.path.exits(args.ymlfile):
        raise ValueError('YML file not found')

    input_package_name = args.package + '==' + args.version

    install_package(input_package_name)

    output_lists = get_pipdeptree()

    found = False
    for i, value in enumerate(output_lists):

        if input_package_name in value:
            found = True
            start = i
            end = i

        if found:
            if get_level(value) == 0 and i != start:
                end = i
                break

    if not found:
        raise ValueError("specified package not found")

    filtered_list_dependencies = output_lists[start:end]

    get_packages(filtered_list_dependencies, 0)

    for i in [[i[0], [i[1], package_dict[i]]] for i in package_dict.keys()]:
        dependencies[i[0]][i[1][0]] = i[1][1]

    with open(args.ymlfile) as f:
        # use safe_load instead load
        dataMap = yaml.safe_load(f)

    for key in dataMap['packages'].keys():
        if key in dependencies:
            del dependencies[key]

    print()
