#!/usr/bin/env python3

import datetime
import urllib.request
import json
import base64


url = 'https://api.github.com/repos/{0}/{1}/commits'
branches = 'https://api.github.com/repos/{0}/{1}/branches'


def insert_params(start_date, last_date, branch):
    return '?since={0}T00:00:0200&until={1}T23:59:0200&sha={2}'.format(
        start_date, last_date, branch
    )

def getCommits(params, username, password, author_name):
    """
    Get raw Github commits data.
    """
    # get specific user commits or all the commits if the author is None
    if author_name:
        author = '&author={0}'.format(author_name)
    req = urllib.request.Request(url.format(repo_owner, repo_name) + params + author)
    string = '%s:%s' % (username, password)
    bebo = string.encode('utf-8')

    req.add_header('Authorization', 'Basic ' + base64.urlsafe_b64encode(bebo).decode('utf-8'))
    req.add_header('Content-Type', 'application/json')
    req.add_header('Accept', 'application/json')
    resp = urllib.request.urlopen(req)

    parsed_data = json.loads(resp.read().decode('utf-8'))

    return parsed_data

def createReport(commits):
    """
    Parse and create string Report.
    """
    report = ''
    count = 1
    date = None
    for commit in commits:
        raw_date = commit.get('commit').get('author').get('date')
        converted_date = datetime.datetime.strptime(
            raw_date[:-1], "%Y-%m-%dT%H:%M:%S"
        )
        if not date:
            date = converted_date.strftime('%Y-%m-%d')
            report += '{0}\n'.format(date)
        if date != converted_date.strftime('%Y-%m-%d'):
            date = converted_date.strftime('%Y-%m-%d')
            report += '\n{0}\n'.format(date)
            count = 1
        report += '{0}) description: {1}\n'.format(
            count,
            commit.get('commit').get('message')
        )
        report += 'url: {0}\n'.format(commit.get('html_url'))
        count += 1
    return report

def writeReport(report, start_date, last_date):
    """
    Write commits information to the file.
    """
    f = open('report({0}|{1}).txt'.format(start_date, last_date), 'w')
    f.write(report)
    f.close()

def run_script():
    """
    Run script and populate data by the user
    """
    print('Please enter a repository owner:')
    repo_owner = input('->')
    if not repo_owner:
        raise Exception('You didn\'t enter a repo owner!')
    print('Please enter a repo name:')
    repo_name = input('->')
    print('Please enter start date (for instance, 2016-08-25):')
    start_date = input('->')
    if not start_date:
        raise Exception('You didn\'t enter start date!')
    print('Please enter last date (for instance, 2016-08-25):')
    last_date = input('->')
    if not last_date:
        raise Exception('You didn\'t enter last date!')
    print('Please enter the branch name which contains commits you need:')
    branch = input('->')
    if not branch:
        raise Exception('You didn\'t enter branch!')
    print('Please enter the author name which commits you need or tap enter if you prefer to get all users commits:')
    author_name = input('->')

    print('Time to authenticate...')
    print('Please enter your username:')
    username = input('->')
    if not username:
        raise Exception('You didn\'t enter username!')
    print('Please enter the username name which contains commits you need:')
    password = input('->')
    if not password:
        raise Exception('You didn\'t enter password!')

    # run report creating
    params = insert_params(start_date, last_date, branch)
    commits = getCommits(params, username, password, author_name)
    report = createReport(commits)
    writeReport(report, start_date, last_date)


if __name__ == '__main__':
    print('Hello! Follow instructions to get a file with your commits history.')

    run_script()

    print('Report was created in script directory successfully!')
