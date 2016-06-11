#!/usr/bin/env python
import argparse
import os
import sys

import git
import jenkins
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


def init_jenkins_conn():
    """
    Read the configuration file ~/.ci to get the server URL, username, and API token. Then, create a connection to the
    Jenkins server with those credentials.

    :return: A jenkins.Jenkins object describing the connection to the Jenkins server
    """
    config = {
        config_line.split('=')[0]: config_line.split('=')[1]
        for config_line in filter(lambda item: item, open(os.path.expanduser('~/') + '.ci').read().split('\n'))
    }
    assert {'server', 'username', 'api_token'}.issubset(set(config.keys())), 'Missing configuration parameters'
    return jenkins.Jenkins(url=config['server'], username=config['username'], password=config['api_token'])


def load_arguments():
    """
    Arguments to the program.

    :return: An object with argument name properties
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('action', help='Action to perform: one of {actions}'.format(actions=available_actions().keys()))
    return parser.parse_args()


def load_git_info():
    """
    Get all info for the git repository in the current working directory.

    :return: A dictionary of git parameters
    """
    try:
        repo = git.Repo()
        git_info = {
            'branch': repo.active_branch.name,
            'job_name': repo.git.working_dir.split('/')[-1],
        }
        print_info('Job/project ID is {job_name}.'.format(job_name=git_info['job_name']))
        print_info('Current branch is {branch}.'.format(branch=git_info['branch']))
        print ''
        return git_info
    except git.InvalidGitRepositoryError:
        print_error('Could not read the git repository in the current working directory!')
        sys.exit(1)


def build_job(conn, git_info):
    """
    Submit a job to the Jenkins server.

    :param conn: An instance of jenkins.Jenkins, as initialized by init_jenkins_conn()
    :param git_info: A dictionary of the working directory repository's git parameters, as returned by load_git_info()
    """
    conn.build_job(
        git_info['job_name'],
        parameters={
            'BRANCH': git_info['branch'],
        },
    )
    print_success('Submitted build job to the CI server.')


def job_queue(conn, git_info):
    """
    Print all jobs currently in the build queue.

    :param conn: An instance of jenkins.Jenkins, as initialized by init_jenkins_conn()
    :param git_info: A dictionary of the working directory repository's git parameters, as returned by load_git_info()
    """
    queue = conn.get_queue_info()
    if len(queue) == 0:
        print 'No jobs in queue.'
        return
    print 'Current jobs in queue:'
    for job in queue:
        print 'ID: {job_id}'.format(job_id=job['id'])
        print '    Name: {job_name}'.format(job_name=job['task']['name'])
        print '    Parameters: {params}'.format(params=job['params'].replace('\n', ''))
        print '    Status: {status}'.format(status=job['why'])


def cancel_job(conn, git_info):
    """
    Cancel all queued and running jobs, as applicable.

    :param conn: An instance of jenkins.Jenkins, as initialized by init_jenkins_conn()
    :param git_info: A dictionary of the working directory repository's git parameters, as returned by load_git_info()
    """
    queue = conn.get_queue_info()
    currently_running_jobs = conn.get_running_builds()

    if len(queue) == 0:
        print 'No jobs in queue to cancel.'
    for job in queue:
        print 'Canceling job {job_id}.'.format(job_id=job['id'])
        conn.cancel_queue(job['id'])

    if len(currently_running_jobs) == 0:
        print 'No currently running jobs in queue to cancel.'
    for job in currently_running_jobs:
        print 'Aborting build {build_num} (running on {node}).'.format(build_num=job['number'], node=job['node'])
        conn.stop_build(git_info['job_name'], job['number'])


def list_jobs(conn, git_info):
    """
    List all currently running/building jobs.

    :param conn: An instance of jenkins.Jenkins, as initialized by init_jenkins_conn()
    :param git_info: A dictionary of the working directory repository's git parameters, as returned by load_git_info()
    """
    currently_running_jobs = conn.get_running_builds()
    if len(currently_running_jobs) == 0:
        print 'No currently running builds.'
        return
    print 'Currently running builds:'
    for job in currently_running_jobs:
        print '{job_name} #{build_num} running on {node}'.format(
            job_name=job['name'],
            build_num=job['number'],
            node=job['node'],
        )


def console_output(conn, git_info):
    """
    Retrieve the console output of the most recently completed build.

    :param conn: An instance of jenkins.Jenkins, as initialized by init_jenkins_conn()
    :param git_info: A dictionary of the working directory repository's git parameters, as returned by load_git_info()
    """
    try:
        last_build_number = conn.get_job_info(git_info['job_name'])['lastCompletedBuild']['number']
    except jenkins.NotFoundException:
        print_error('No builds exist yet for this project.')
        return
    print_info('Most recent build number for project {job_name} is {build_number}.'.format(
        job_name=git_info['job_name'],
        build_number=last_build_number,
    ))
    print conn.get_build_console_output(git_info['job_name'], last_build_number)


def deploy_job(conn, git_info):
    """
    Deploy the specified job via the Jenkins server.

    :param conn: An instance of jenkins.Jenkins, as initialized by init_jenkins_conn()
    :param git_info: A dictionary of the working directory repository's git parameters, as returned by load_git_info()
    """
    conn.build_job(
        'deploy--{job_name}'.format(job_name=git_info['job_name']),
        parameters={
            'REPO_DIR': os.environ.get('REPO_DIR'),
            'BRANCH': os.environ.get('BRANCH'),
        },
    )
    print_success('Submitted deployment job to the CI server for branch {deploy_branch} to directory {deploy_dir}.'.format(
        deploy_branch=os.environ.get('BRANCH', 'master'),
        deploy_dir=os.environ.get('REPO_DIR', 'default'),
    ))


def invalid_input(conn, git_info):
    """
    Generic message if the input task was not recognized.

    :param conn: An instance of jenkins.Jenkins, as initialized by init_jenkins_conn()
    :param git_info: A dictionary of the working directory repository's git parameters, as returned by load_git_info()
    """
    print_error('Unknown action.')


def available_actions():
    """
    Retrieve a dictionary of all actions exposed to the client.

    :return: A dictionary mapping action names to functions.
    """
    return {
        'build': build_job,
        'queue': job_queue,
        'cancel': cancel_job,
        'list': list_jobs,
        'console': console_output,
        'deploy': deploy_job,
    }


def ci():
    """
    Main program. Load the git repository information, initialize a connection to the Jenkins server, and run the
    command requested by the user.
    """
    git_info = load_git_info()
    conn = init_jenkins_conn()
    available_actions().get(load_arguments().action, invalid_input)(conn, git_info)


if __name__ == '__main__':
    ci()
