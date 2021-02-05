"""
Exports issues from a repository to csv files.
Uses basic authentication (Github username + password) to retrieve issues
from a repository that username has access to. Supports Github API v3.
Forked from: unbracketed/export_repo_issues_to_csv.py
"""
import csv
import requests
import datetime
import json


type_is = ' is:issue'
#milestone = '4.1'
repo = 'management-center'
#query_milestone = 'milestone:' + milestone
query_repo = 'repo:hazelcast/' + repo

# Search query with milestone filter
# search_query = ' ' + type_is + ' ' + query_milestone + ' ' + query_repo

# Search query without milestone filter
search_query = ' ' + type_is + ' ' + query_repo + ' is:open'

github_user = 'YOUR-GH-USERNAME'
github_token = 'YOUR-GH-TOKEN'
issue_count = 0

conversion_dict = {'emre-aydin': 'emre@hazelcast.com',
                   'jgardiner68': 'james.gardiner@hazelcast.com',
                   'puzpuzpuz': 'andrey@hazelcast.com',
                   'neilstevenson': 'neil@hazelcast.com',
                   'yuraku': 'iurii.kutelmakh@hazelcast.com',
                   'aigoncharov': 'andrey.goncharov@hazelcast.com',
                   'jbee': 'jan@hazelcast.com',
                   'vertex-github': 'vertex-github@ghuser.com',
                   'erosb': 'bence.eros@hazelcast.com',
                   'olukas': 'ondrej@hazelcast.com',
                   'alex-dukhno': 'alex.dukhno@hazelcast.com',
                   'jerrinot': 'jaromir@hazelcast.com',
                   'dbrimley': 'david@hazelcast.com',
                   'danad02': 'polansky@webscope.io',
                   'utkukaratas': 'utku.karatas@hazelcast.com',
                   'jankoritak': 'koritak@webscope.io',
                   'sertugkaya': 'sertug@hazelcast.com',
                   'alparslanavci': 'alparslan@hazelcast.com',
                   'tezc': 'ozan.tezcan@hazelcast.com',
                   'pjastrz': 'pjastrz@ghuser.com',
                   'jvorcak': 'vorcak@webscope.io',
                   'Holmistr': 'jiri@hazelcast.com',
                   'gurbuzali': 'ali@hazelcast.com',
                   'gokhanoner': 'gokhan@hazelcast.com',
                   'pawelklasa': 'pawel.klasa@hazelcast.com',
                   'ncherkas': 'nazarii@hazelcast.com',
                   'mesutcelik': 'mesut@hazelcast.com',
                   'viliam-durina': 'viliam@hazelcast.com',
                   'Serdaro': 'serdar@hazelcast.com',
                   'nfrankel': 'nicolas.frankel@hazelcast.com',
                   'mmedenjak': 'matko@hazelcast.com',
                   'mdumandag': 'metin@hazelcast.com',
                   'lazerion': 'baris@hazelcast.com',
                   'kairojya':'kairojya@ghuser.com',
                   'jahanzebbaber': 'jahanzeb@hazelcast.com',
                   'hasancelik': 'hasan@hazelcast.com',
                   'eminn': 'emin@hazelcast.com',
                   'burakcelebi': 'burak@hazelcast.com',
                   'bilalyasar': 'bilal@hazelcast.com',
                   'bbuyukormeci': 'berk@hazelcast.com',
                   '7erry': 'terry@hazelcast.com',
                   '': ''}


def get_issues():
    # Requests issues from GitHub API and writes to CSV file.
    result_json = requests.get('https://api.github.com/search/issues',
                               auth=(github_user, github_token),
                               params={'q': search_query, 'sort': 'updated', 'direction': 'desc'})

    print("Function starts:", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


    csvfilename = '/Users/ayberksorgun/Desktop/github-issues/{}-issues-{}.csv' \
        .format(repo, datetime.datetime.now().strftime("%Y-%m-%dt%H-%M-%S"))
    print('Filename: ', csvfilename)

    with open(csvfilename, 'w', newline='') as csvfile:
        csv_out = csv.writer(csvfile)

        csv_out.writerow(['Summary', 'Description', 'dateCreated', 'fixVersion', 'Creator', 'Assignee', 'Comments', 'Labels'])

        write_issues(result_json, csv_out)

        # Multiple requests are required if response is paged
        if 'link' in result_json.headers:
            pages = {rel[6:-1]: url[url.index('<') + 1:-1] for url, rel in
                     (link.split(';') for link in result_json.headers['link'].split(','))}
            while 'last' in pages and 'next' in pages:
                pages = {rel[6:-1]: url[url.index('<') + 1:-1]
                         for url, rel in (link.split(';')
                                          for link in result_json.headers['link'].split(','))}
                result_json = requests.get(pages['next'], auth=(github_user, github_token))
                write_issues(result_json, csv_out)
                if pages['next'] == pages['last']:
                    break

    print("Function ends : ", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print('Total number of issues imported:', issue_count)


def write_issues(result_json, csvout):
    # Parses JSON response and writes to CSV file
    if result_json.status_code != 200:
        raise Exception(result_json.status_code)

    for item in result_json.json()['items']:

        labels = [l['name'] for l in item['labels']]
        # Creation date of the issue
        create_date = item['created_at'].split('T')[0]
        # Close date of the issue
        close_date = item['closed_at']
        # If there is a close date then split the date and only include the date part but not time
        if close_date:
            close_date = close_date.split('T')[0]
        # Assignee information
        assignee_str = ''
        # If issue has assignee then get the login name of the assignee
        if item['assignee'] is not None:
            assignee = item['assignee']
            if assignee is not None:
                assignee_str = assignee['login']
        # User that opened the issue
        user_str = ''
        # Get the login name of the user who opened the issue
        if item['user'] is not None:
            user = item['user']
            if user is not None:
                user_str = user['login']

        milestone_str = ''
        # Get the milestone label of the issue
        if item['milestone'] is not None:
            milestone = item['milestone']
            if milestone is not None:
                milestone_str = milestone['title']

        # Getting comment information by using another GET request
        comment_json = requests.get('https://api.github.com/repos/hazelcast/management-center/issues/' +
                                    str(item['number']) + '/comments', auth=(github_user, github_token))

        # Creating a list of comments for every issue
        comments = [each['created_at'].split('T')[0] + ' ' + each['created_at'].split('T')[1][0:5] + '; ' +
                    conversion_dict[each['user']['login']] + '; ' + each['body'] for each in comment_json.json()]

        # Change the following line to write out additional fields
        csvout.writerow([item['title'], "GH Issue link: "+item['html_url'] + " \\"+"\\" + item['body'], create_date,
                         milestone_str, conversion_dict[user_str], conversion_dict[assignee_str], json.dumps(comments),
                         labels])
        # Counting the number of issues
        global issue_count
        issue_count += 1


get_issues()