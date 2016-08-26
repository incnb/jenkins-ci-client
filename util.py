from termcolor import cprint


def print_info(info):
    """
    Print a color-coded informational message.

    :param info: Message to print
    """
    cprint('INFO: {info}'.format(info=info), 'yellow')


def print_success(success):
    """
    Print a color-coded success message.

    :param success: Message to print
    """
    cprint(success, 'green')


def print_error(error):
    """
    Print a color-coded error message.

    :param error: Message to print
    """
    cprint('ERROR: {error}'.format(error=error), 'red')


def test_job_name(project_name):
    """
    Get the name of the test job given the project name.

    :param project_name: Name of the project (generally, the directory name)
    :return: The name of the test job on Jenkins
    """
    return 'test--{project_name}'.format(project_name=project_name)


def deploy_job_name(project_name):
    """
    Get the name of the deploy job given the project name.

    :param project_name: Name of the project (generally, the directory name)
    :return: The name of the deploy job on Jenkins
    """
    return 'deploy--{project_name}'.format(project_name=project_name)
