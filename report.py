#!/usr/bin/env python3

import os
import datetime
import urllib.request
import json
import base64


url = 'https://api.github.com/repos/{0}/{1}/commits'
branches = 'https://api.github.com/repos/{0}/{1}/branches'


class Info():

    def __init__(self, *args, **kwargs):
        self.repo_name = kwargs.get('repo_name')
        self.repo_owner = kwargs.get('repo_owner')
        self.start_date = kwargs.get('start_date')
        self.last_date = kwargs.get('last_date')
        self.branch = kwargs.get('branch')
        self.author_name = kwargs.get('authore_name')
        self.username = kwargs.get('username')
        self.password = kwargs.get('password')

    def insert_params(self):
        return '?since={0}T00:00:0200&until={1}T23:59:0200&sha={2}'.format(
            self.start_date, self.last_date, self.branch
        )

    def getCommits(self):
        """
        Get raw Github commits data.
        """
        params = self.insert_params()
        # get specific user commits or all the commits if the author is None
        if self.author_name:
            full_url = url.format(
                self.repo_owner,
                self.repo_name
            ) + params + '&author={0}'.format(
                self.author_name
            )
        else:
            full_url = url.format(self.repo_owner, self.repo_name) + params

        req = urllib.request.Request(full_url)
        string = '%s:%s' % (self.username, self.password)
        bebo = string.encode('utf-8')

        req.add_header('Authorization', 'Basic ' + base64.urlsafe_b64encode(bebo).decode('utf-8'))
        req.add_header('Content-Type', 'application/json')
        req.add_header('Accept', 'application/json')
        resp = urllib.request.urlopen(req)

        parsed_data = json.loads(resp.read().decode('utf-8'))

        return parsed_data

    def createReport(self):
        """
        Parse and create string Report.
        """
        report = ''
        count = 1
        date = None
        commits = self.getCommits()
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

    def writeReport(self):
        """
        Write commits information to the file.
        """
        report = self.createReport()

        folder_path = os.path.join(os.getcwd(), 'reports')
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)
        file_name = os.path.join(folder_path, 'report({0}|{1}).txt'.format(
            self.start_date,
            self.last_date
        ))
        with open(file_name, 'w') as file:
            file.write(report)


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
    info = Info(
        repo_owner=repo_owner,
        repo_name=repo_name,
        start_date=start_date,
        last_date=last_date,
        branch=branch,
        author_name=author_name,
        username=username,
        password=password
    )
    info.writeReport()  # create file with commits


if __name__ == '__main__':
    print('Hello! Follow instructions to get a file with your commits history.')

    run_script()

    print('Report was created in script directory successfully!')
