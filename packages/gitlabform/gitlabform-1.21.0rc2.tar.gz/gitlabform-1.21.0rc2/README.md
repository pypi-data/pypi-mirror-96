[![version](https://badge.fury.io/py/gitlabform.svg)](https://badge.fury.io/py/gitlabform)
![release date](https://img.shields.io/github/release-date/egnyte/gitlabform)
![PyPI downloads](https://img.shields.io/pypi/dm/gitlabform?label=PyPI%20Downloads)
![docker pulls](https://img.shields.io/docker/pulls/egnyte/gitlabform)
[![code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

<img src="https://raw.githubusercontent.com/egnyte/gitlabform/main/docs/gitlabform-logo.png" width="600px">

GitLabForm is a specialized "configuration as a code" tool for GitLab projects, groups and more
using hierarchical configuration written in YAML.

## Table of Contents

* What you get? - [Features](#features) (with [Comparison to similar apps](#comparison-to-similar-apps) and [Limitations](#limitations))
* Basic usage - [Requirements](#requirements), [Installation](#installation), [Quick start](#quick-start)
* Advanced usage - [Full configuration syntax](#full-configuration-syntax),
  [More cli usage examples](#more-cli-usage-examples),
  [Running in an automated pipeline](#running-in-an-automated-pipeline),
  [Running automatically for new projects](#running-automatically-for-new-projects),
* Join us! - [Contributing](#contributing), [History](#history), [Legal](#legal)

## Features

GitLabForm enables you to manage:

* Group settings,
* Project settings,
* Archive/unarchive project,
* Project members (users and groups) {add/change access level, NO removal yet},
* Group members (users) {add/remove user, change access level},
* Deployment keys,
* Secret variables (on project and group/subgroup level),
* Branches (protect/unprotect),
* Tags (protect/unprotect),
* Services,
* (Project) Hooks,
* (Project) Push Rules (**GitLab EE only**),
* (Add/edit or delete) Files, with templating based on Jinja2 (now supports custom variables!),
* Merge Requests approvals settings and approvers (**GitLab EE only**),
* Pipeline schedules,

...for:

* all projects in your GitLab instance/that you have access to,
* a group/subgroup of projects,
* a single project,

...and a combination of them.

GitLabForm uses [hierarchical configuration with inheritance, merging/overwriting and addivity](https://github.com/egnyte/gitlabform/blob/main/docs/FEATURES_DESIGN.md#hierarchical-merged-and-overridable-configuration).
GitLabForm is also using [passing the parameters as-is to GitLab APIs with PUT/POST requests](https://github.com/egnyte/gitlabform/blob/main/docs/FEATURES_DESIGN.md#raw-parameters-passing).

### Comparison to similar apps

GitLabForm has roughly the same purpose as [GitLab provider](https://www.terraform.io/docs/providers/gitlab/index.html)
for [Terraform](https://www.terraform.io/) (which is a tool that we love and which has inspired us to write this app),
but it has a different set of features and uses a different configuration format.

Please read more about [GitLab provider for Terraform vs GitLabForm](https://github.com/egnyte/gitlabform/blob/main/docs/GT_VS_GLF.md). This article includes a link to the feature matrix / comparison sheet between these two tools.

To configure your GitLab instance itself (appearance, application settings, features, license) please check out
the [GitLab Configuration as Code (GCasC)](https://github.com/Roche/gitlab-configuration-as-code) project!

### Limitations

Some of the app features are limited because of the GitLab API issues. [Here is the list of them](https://github.com/egnyte/gitlabform/issues?q=is%3Aissue+is%3Aopen+label%3A%22gitlab+issue%22). Please check the links to the GitLab issue(s) in their comments and please upvote them if they are affecting you. Note that these issues/bugs affect all the apps using GitLab API, not just GitLabForm.

## Requirements

* Python 3.6-3.8 **or** Docker
  * (Python 3.9 should be fine too, but it's not "officially" supported yet)
* GitLab 11+, GitLab EE for Merge Requests & Push Rules management

## Installation

A. Pip: `pip3 install gitlabform`

B. Docker: run GitLabForm in a Docker container with this oneliner:
`docker run -it -v $(pwd):/config egnyte/gitlabform:latest gitlabform`.
Instead of "latest" you can also use a specific version and choose from Alpine and Debian-based images.
See the [GitLabForm's DockerHub page](https://hub.docker.com/r/egnyte/gitlabform/tags) for a list of available tags.

## Quick start

Let's assume that you want to add a deployment key to all projects in a group "My Group" (with path "my-group").
If so then:

1. Create example `config.yml`:

```yaml
gitlab:
  # You can also set in your environment GITLAB_URL
  url: https://gitlab.yourcompany.com
  # You can also set in your environment GITLAB_TOKEN
  token: "<private token of an admin user>"
  api_version: 4

group_settings:
  my-group:
    deploy_keys:
      a_friendly_deploy_key_name:  # this name is only used in GitLabForm config
        key: ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC3WiHAsm2UTz2dU1vKFYUGfHI1p5fIv84BbtV/9jAKvZhVHDqMa07PgVtkttjvDC8bA1kezhOBKcO0KNzVoDp0ENq7WLxFyLFMQ9USf8LmOY70uV/l8Gpcn1ZT7zRBdEzUUgF/PjZukqVtuHqf9TCO8Ekvjag9XRfVNadKs25rbL60oqpIpEUqAbmQ4j6GFcfBBBPuVlKfidI6O039dAnDUsmeafwCOhEvQmF+N5Diauw3Mk+9TMKNlOWM+pO2DKxX9LLLWGVA9Dqr6dWY0eHjWKUmk2B1h1HYW+aUyoWX2TGsVX9DlNY7CKiQGsL5MRH9IXKMQ8cfMweKoEcwSSXJ
        title: ssh_key_name_that_is_shown_in_gitlab
        can_push: false
```

2. Run `gitlabform my-group`

3. Watch GitLabForm add this deploy key to all projects in "My Group" group in your GitLab!

## Full configuration syntax

See [config.yml](https://github.com/egnyte/gitlabform/blob/main/config.yml) in this repo as a well documented example
of all the features, including configuring all projects in all groups, projects in "my-group" group and specifically
project "my-group/my-project1".

## More cli usage examples

To apply settings for a single project, run:

```gitlabform my-group/my-project1```

To apply settings for a group of projects, run:

```gitlabform my-group```

To apply settings for all groups of projects and projects explicitly defined in the config, run:

```gitlabform ALL_DEFINED```

To apply settings for all projects, run:

```gitlabform ALL```


Run:

```gitlabform -h```

...to see the current set of supported command line parameters.

## Running in an automated pipeline

You can use GitLabForm as a part of your [CCA (Continuous Configuration Automation)](https://en.wikipedia.org/wiki/Continuous_configuration_automation) pipeline.

You can run it with a schedule on `ALL_DEFINED` or `ALL` projects to unify your GitLab configuration, after it may have drifted
from the configuration. For example you may allow the users to reconfigure projects during their working hours
but automate cleaning up the drift each night.

An example for running GitLabForm using GitLab CI is provided in the [.gitlab-ci.example.yml](https://github.com/egnyte/gitlabform/docs/.gitlab-ci.example.yml)
file.

Note that as a standard best practice you should not put your GitLab access token in your `config.yml` (unless it is
encrypted) for security reasons - please set it in the `GITLAB_TOKEN` environment variable instead.

For GitLab CI a secure place to set it would be a [Secret/Protected Variable in the project configuration](https://docs.gitlab.com/ee/ci/variables/#via-the-ui).

## Running automatically for new projects

We have documented some methods of automating running GitLabForm for newly created GitLab projects
[here](https://github.com/egnyte/gitlabform/blob/main/docs/AUTOMATE_FOR_NEW_PROJECTS.md).

## Contributing

Please see the [contribution guide](https://github.com/egnyte/gitlabform/CONTRIBUTING.md) for info about all kinds of contributions, like:
* questions, feature requests,
* documentation and code contributions,
* other.

[Contribution guide](https://github.com/egnyte/gitlabform/CONTRIBUTING.md) is also the place to look for info how to develop the app locally,
build it, run the tests and learn about the code guidelines.


For detailed info about how the app code has been organized, where is what and where and how to fix bugs and/or
add new features, please see the [implementation design](https://github.com/egnyte/gitlabform/blob/main/docs/IMPLEMENTATION_DESIGN.md) article.

## History

This tool has been originally created as a workaround for missing GitLab features such as [assigning deploy keys per project groups](https://gitlab.com/gitlab-org/gitlab-ce/issues/3890)
but as of now we prefer to use it ever if there are appropriate web UI features, such as [secret variables per project groups](https://gitlab.com/gitlab-org/gitlab-ce/issues/12729)
(released in GitLab 9.4) to keep the configuration as code.

Later on we added features that allowed us to use GitLabForm to improve a group containing around 100 similar projects
to move to a unified development flow (by managing branches protection and the Pull Requests configuration),
basic tests and deployment process (by managing secret variables, deployment keys and files, such as `.gitlab-ci.yml`),
integrations (such as JIRA or Slack) and more.

## Legal

The app code is licensed under the [MIT](https://github.com/egnyte/gitlabform/blob/main/LICENSE) license.


GitLab is a registered trademark of GitLab, Inc. This application is not endorsed by GitLab and is not affiliated with GitLab in any way.

The GitLabForm logo is based on the GitLab logos available [here](https://about.gitlab.com/press/),
and like the original art is licensed under the
[Creative Commons Attribution Non-Commercial ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-nc-sa/4.0/).
