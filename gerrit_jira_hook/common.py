#!/usr/bin/env python
# encoding: utf-8

import subprocess


def extract_git_log(args, base_dir):
    """Extract git log of all merged commits."""
    cmd = ['git',
           '--git-dir=' + base_dir + args.project + '.git',
           'log', '--no-merges', args.commit + '^1..' + args.commit]
    return subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()[0]


def fix_or_related_fix(related):
    if related:
        return "Related fix"
    else:
        return "Fix"


def change_abandoned_message(change_url, project,
                             branch, abandoner, reason):
    template = """
h3. {{color:red}}Change abandoned on {project} ({branch}){{color}}

Change abandoned by {abandoner} on branch: {branch}
Review: [{change_url}|{change_url}]
"""

    content = template.format(project=project, branch=branch,
                              abandoner=abandoner,
                              change_url=change_url)

    if reason:
        content += ('\nReason: %s' % (reason))

    return content


def change_proposed_message(change_url, project, branch,
                            related=False, uploader=None):
    template = """
h3. {{color:#4c9aff}}{fix} proposed to {project} ({branch}){{color}}

{fix} proposed to branch: {branch}
Review: [{change_url}|{change_url}]
Uploader: {uploader}
"""

    fix = fix_or_related_fix(related)
    content = template.format(fix=fix, project=project, branch=branch,
                              change_url=change_url, uploader=uploader)

    return content


def change_merged_message(change_url, project, commit,
                          submitter, branch, git_log, commit_template,
                          related=False):
    template = """
h3. {{color:#57d9a3}}{fix} merged to {project} ({branch}){{color}}

Reviewed: [{change_url}|{change_url}]
Committed: [{git_url}|{git_url}]
Submitter: {submitter}
Branch: {branch}

{git_log}
"""
    git_url = commit_template % (project, commit)
    content = template.format(fix=fix_or_related_fix(related), project=project,
                              branch=branch, change_url=change_url,
                              git_url=git_url, submitter=submitter,
                              git_log=git_log)

    return content
