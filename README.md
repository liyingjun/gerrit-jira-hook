# gerrit-jira-hook

This hook integrates Jira to Gerrit code review for auto creating patch related information when
a "patch set" is created, a "change" is merged or abandanded.

## Installation

Install this hook at Gerrit code review server.

```
python setup.py install
```

## Setup

Copy `etc/jira-hook.cfg` to `/etc/` and update:

- url: Jira api server base url
- username: jira user with comment permission
- password: password for jira user
- default_tester: auto assign the jira story or task to this user after the related "change" merged at Gerrit side.
- base_dir: base directory for git repository
- commit_url_template: URL template for merged git commit

Create the following files under directory `gerrit/hooks`:

- change-abandoned

    ```
    #!/bin/sh

    timeout -k 2m 10m /usr/bin/jira-update-ticket change-abandoned "$@"

- change-merged:

    ```
    #!/bin/sh

    timeout -k 2m 10m /usr/bin/jira-update-ticket change-merged "$@"
    ```

- patchset-created:

    ```
    #!/bin/sh

    timeout -k 2m 10m /usr/bin/jira-update-ticket patchset-created "$@"
    ```

Add commentlink "jira" to `gerrit/etc/gerrit.config`:

```
[commentlink "jira"]
        match = "(\\b[Jj]ira\\b)[ \\t#:]*([A-Za-z0-9\\-]+)"
        link = http://jiraserver/browse/$2
```

## Usage

Just add "Jira: Jira story or task ID" to commit message when pushing patch to Gerrit code review.
