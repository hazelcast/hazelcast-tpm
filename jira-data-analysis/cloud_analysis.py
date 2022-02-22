#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from jira import JIRA
import pandas as pd
import os

#setting up user-specific parameters
desktop_path = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop') 
jiraOptions = {'server': "https://hazelcast.atlassian.net"}
jira = JIRA(options=jiraOptions, basic_auth=("YOUR_COMPANY_EMAIL", "YOUR_TOKEN"))

#insert your query written in JQL
jira_query = 'project = HZC AND type in (Bug, Story, Task) AND status = Done and originalEstimate > 0 and timespent > 0 ORDER BY created DESC'


#run query to get result lenght
results = jira.search_issues(jql_str=jira_query,maxResults=100000)
issue_count = results.total
print("Total issue count: " + str(issue_count))
iter_count = int(((issue_count - issue_count % 100) / 100) + 1)
issues_deviation = []


#iterate over query to store records in a python list
while iter_count > 0:
    print("Starting the query from: " + str(((iter_count -1) * 100)))
    for each in jira.search_issues(jql_str= jira_query,startAt=((iter_count -1) * 100),maxResults=100):
       
        issues_deviation.append([
            each.key, 
            each.fields.issuetype.name, 
            #int(each.fields.aggregatetimeestimate), 
            int(each.fields.aggregatetimeoriginalestimate),
            #int(each.fields.aggregatetimespent), 
            #int(each.fields.timeestimate), 
            #int(each.fields.timeoriginalestimate),
            int(each.fields.timespent),
            each.fields.status.name, 
            each.fields.assignee.displayName])
    iter_count -=1

#filter out the data from some specific users
for index, line in enumerate(issues_deviation):
    if line[5] == 'Ozge Avcioglu' or line[5] == 'Former user' or line[5] == 'Alexander Galibey' or line[5] == 'Grzegorz Piwowarek' or line[5] == 'Andrii Borovenskyi' or line[5] == 'Eugene Abramchuk':
        issues_deviation[index] = None

issues_deviation = list(filter(lambda v: v is not None, issues_deviation))

#convert list to pandas dataframe for easier data manipulation    
df_issues = pd.DataFrame(issues_deviation, columns=["KEY",
                                          "ISSUE_TYPE",
                                          #"aggregatetimeestimate",
                                          "aggregatetimeoriginalestimate",
                                          #"aggregatetimespent",
                                          #"timeestimate",
                                          #"timeoriginalestimate",
                                          "timespent",
                                          "STATUS",
                                          "ASSIGNEE"])

df_issues["aggregatetimeoriginalestimate"] = df_issues["aggregatetimeoriginalestimate"].apply(lambda sec: sec/3600)
df_issues["timespent"] = df_issues["timespent"].apply(lambda sec: sec/3600)
df_deviation = pd.pivot_table(df_issues,index=['ASSIGNEE'], aggfunc={'aggregatetimeoriginalestimate': 'sum','timespent': 'sum','KEY':'count'})
df_deviation.loc["Total"] = df_deviation.sum()
df_deviation["avg_estimation"]= df_deviation.apply(lambda row: round(row.aggregatetimeoriginalestimate/row.KEY,2), axis=1)
df_deviation["avg_timespent"]= df_deviation.apply(lambda row: round(row.timespent/row.KEY,2), axis=1)
df_deviation["deviation_pct"]= df_deviation.apply(lambda row: round((100 * row.timespent/row.aggregatetimeoriginalestimate)-100,2), axis=1)

#export data to csv file
df_issues.to_csv(desktop_path + '/deviation_raw_data.csv', sep=',', encoding='utf-8')
df_deviation.to_csv(desktop_path + '/deviation_table.csv', sep=',', encoding='utf-8')


jira_query = 'project = HZC AND type in (Bug) AND status = Done and timespent > 0 ORDER BY created DESC'


#run query to get result lenght
results = jira.search_issues(jql_str=jira_query,maxResults=100000)
issue_count = results.total
print("Total issue count: " + str(issue_count))
iter_count = int(((issue_count - issue_count % 100) / 100) + 1)
issues_bugs = []


#iterate over query to store records in a python list
while iter_count > 0:
    print("Starting the query from: " + str(((iter_count -1) * 100)))
    for each in jira.search_issues(jql_str= jira_query,startAt=((iter_count -1) * 100),maxResults=100):
       
        issues_bugs.append([
            each.key, 
            each.fields.issuetype.name, 
            #int(each.fields.aggregatetimeestimate), 
            #int(each.fields.aggregatetimeoriginalestimate),
            #int(each.fields.aggregatetimespent), 
            #int(each.fields.timeestimate), 
            #int(each.fields.timeoriginalestimate),
            int(each.fields.timespent),
            each.fields.status.name, 
            each.fields.assignee.displayName])
    iter_count -=1
    
#convert list to pandas dataframe for easier data manipulation    
df_bugs = pd.DataFrame(issues_bugs, columns=["KEY",
                                          "ISSUE_TYPE",
                                          #"aggregatetimeestimate",
                                          #"aggregatetimeoriginalestimate",
                                          #"aggregatetimespent",
                                          #"timeestimate",
                                          #"timeoriginalestimate",
                                          "timespent",
                                          "STATUS",
                                          "ASSIGNEE"])

df_bugs["timespent"] = df_bugs["timespent"].apply(lambda sec: sec/3600)

bugfix_list = []
bugfix_list.append([issue_count, round(df_bugs['timespent'].sum(),2), round(df_bugs['timespent'].sum()/issue_count,2)])
df_bugfix_time = pd.DataFrame(bugfix_list,columns = ['Number of Issues','Total Time Spent','Average Time Spent'])

df_bugs.to_csv(desktop_path + '/bugs_raw_data.csv', sep=',', encoding='utf-8')
df_bugfix_time.to_csv(desktop_path + '/bugs_table.csv', sep=',', encoding='utf-8')







