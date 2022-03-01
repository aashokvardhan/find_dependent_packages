import os
import subprocess


def get_packages(package_name):
    """
        Find all the dependent packages for given package

        Input:
            package_name: name of pip packages
    """

    # run pip show to show all the required packages
    pip_show = subprocess.Popen(["pip", "show", package_name], stdout=subprocess.PIPE)
    output = str(pip_show.communicate()[0])

    requirements = []
    for i in output.replace('\\r', '').split('\\n'):
        if i.lower().startswith('requires'):
            requirements = [package.strip() for package in i[10:].split(',')]
    return requirements


def get_required_packages(package_name):
    """
        Find all the dependent packages and sub dependent packages for given package

        Input:
            package_name: name of pip packages
    """
    # find dependent packages for provided package
    requirements = get_packages(package_name)

    # Loop through the requirements and add additional dependencies for sub packages
    i = 0
    while i < len(requirements):
        new_requirements = get_packages(requirements[i])
        i += 1
        filtered = [j for j in new_requirements if j not in requirements and j.strip() != '']
        requirements += filtered

    return requirements


if __name__ == '__main__':
    import argparse

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Find packages dependency for given package.')
    parser.add_argument('--package', required=True, help='Package whose dependency is required')
    parser.add_argument('--filename', required=False, help='name of text file', default='readme')
    parser.add_argument('--location', required=False, help='folder location', default='.')

    args = parser.parse_args()

    output_folder = args.location
    if not os.path.exists(output_folder):
        print("Output folder doesn't exist. Saving in current folder.")
        output_folder = "."

    output_file_location = os.path.join(output_folder, args.filename + '.txt')
    packages = get_required_packages(args.package)

    with open(output_file_location, 'w') as f:
        for package in packages:
            f.write(package)
            f.write('\n')

    print("Requirements for {0} saved at {1}".format(args.package, output_file_location))
