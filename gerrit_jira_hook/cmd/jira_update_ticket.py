#!/usr/bin/env python
# encoding: utf-8


import argparse
import ConfigParser
from jira import exceptions
from jira import JIRA
import logging
import re

from gerrit_jira_hook import common


FORMAT = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
logging.basicConfig(format=FORMAT, filename='/tmp/jira-hook.log', level=logging.DEBUG)


conf = ConfigParser.RawConfigParser()
conf.read('/etc/jira-hook.cfg')


def add_change_abandoned_message(jira, id, change_url, project,
                                 branch, abandoner, reason):
    content = common.change_abandoned_message(change_url, project, branch,
                                              abandoner, reason)

    jira.add_comment(id, content)


def add_change_proposed_message(jira, id, change_url, project, branch,
                                related=False, uploader=None):
    content = common.change_proposed_message(change_url, project,
                                             branch, related=related,
                                             uploader=uploader)

    jira.add_comment(id, content)


def add_change_merged_message(jira, id, change_url, project, commit,
                              submitter, branch, git_log, related=False):
    content = common.change_merged_message(change_url, project, commit,
                                           submitter, branch, git_log,
                                           conf.get('git', 'commit_url_template'),
                                           related=related)

    jira.add_comment(id, content)


def process_ticket(jira, ticket_id, git_log, args):
    try:
        issue = jira.issue(ticket_id)
    except exceptions.JIRAError as e:
        # issue not found
        if e.status_code == 404:
            logging.debug('Issue %s not found', ticket_id)
        else:
            logging.exception('Jira exception: %s', e.message)
        return
    if args.hook == "change-abandoned":
        add_change_abandoned_message(jira, ticket_id, args.change_url,
                                     args.project, args.branch,
                                     args.abandoner, args.reason)
    if args.hook == "change-merged":
        add_change_merged_message(jira, ticket_id, args.change_url, args.project,
                                  args.commit, args.submitter, args.branch,
                                  git_log)
        tester = conf.get('jira', 'default_tester')
        users = jira.search_users(tester)
        if not users:
            logging.warning("Default tester %s not found", tester)
        else:
            issue.update(assignee=tester)
    if args.patchset == '1' and args.hook == "patchset-created":
        # Transition status for the issue to in progress
        if issue.fields.status.id not in ['3']:
            jira.transition_issue(issue, transition='31')
        add_change_proposed_message(jira, ticket_id, args.change_url,
                                    args.project, args.branch,
                                    uploader=args.uploader)


def find_tickets(git_log):
    SPEC_RE = re.compile(r'\b(jira|jr)\b[ \t]*[#:]?[ \t]*(\S+)', re.I)
    tickets = set([m.group(2) for m in SPEC_RE.finditer(git_log)])
    return tickets


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('hook')
    # common
    parser.add_argument('--change', default=None)
    parser.add_argument('--change-url', default=None)
    parser.add_argument('--project', default=None, required=True)
    parser.add_argument('--branch', default=None)
    parser.add_argument('--commit', default=None, required=True)
    parser.add_argument('--topic', default=None)
    parser.add_argument('--change-owner', default=None)
    # change-abandoned
    parser.add_argument('--abandoner', default=None)
    parser.add_argument('--reason', default=None)
    # change-merged
    parser.add_argument('--submitter', default=None)
    parser.add_argument('--newrev', default=None)
    # patchset-created
    parser.add_argument('--uploader', default=None)
    parser.add_argument('--patchset', default=None)
    parser.add_argument('--is-draft', default=None)
    parser.add_argument('--kind', default=None)

    args = parser.parse_args()

    url = conf.get('jira', 'url')
    username = conf.get('jira', 'username')
    password = conf.get('jira', 'password')

    # Connect to Jira.
    jira = JIRA(url, basic_auth=(username, password))

    # Get git log.
    git_log = common.extract_git_log(args, conf.get('git', 'base_dir'))

    # Process tickets found in git log.
    for ticket in find_tickets(git_log):
        process_ticket(jira, ticket, git_log, args)


if __name__ == "__main__":
    main()
