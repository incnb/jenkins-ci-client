# jenkins-ci-client

Command-line utility for triggering CI builds based on the current Git project.

## Installation

The following steps will generate a `ci` executable and place it in `/usr/local/bin`.

```bash
$ virtualenv env
$ source env/bin/activate
$ make bootstrap  # Installs dependencies
$ make  # Builds compiled executable
$ sudo make install  # Copies executable to `/usr/local/bin`
```

## Configuration

You must first create a text file `~/.ci` containing a URL to the CI server, your Jenkins username, and Jenkins API key. The expected format is as follows:

```
username=YOUR_JENKINS_USERNAME
server=https://ci.yourdomain.com
api_token=YOUR_JENKINS_API_KEY
```

## Usage

Trigger a test build:

```bash
$ ci build
```

Trigger a deployment build:

```bash
$ ci deploy
```

View currently running builds:

```bash
$ ci list
```

View builds in the queue:

```bash
$ ci queue
```

Cancel the most recent queued build:

```bash
$ ci cancel
```

View the console output for the most recently completed build:

```bash
$ ci console
```

## Opinions

`jenkins-ci-client` is deliberately highly opinionated about the structure of your project and CI jobs.

1. The project name is the name of the directory containing the `.git` directory. The *test* job name is `test--{project name}` and the *deploy* job name is `deploy--{project name}`.
2. `ci build` passes `BUILD` as an environment variable to the test job and `ci deploy` passes both `BUILD` and `REPO_DIR` as environment variables to the deploy job.
