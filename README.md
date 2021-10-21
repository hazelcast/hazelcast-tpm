# hazelcast-tpm
Repository of Hazelcast Technical Program Management Team for storing scripts and tools that helps gathering and processing information.

Usage of Composite Actions:
 
 Use the code snippet below to make your own composite action:
 
 - name: Test composite one
      uses: hazelcast/hazelcast-tpm/jira@v4
      with:
        JIRA_BASE_URL: ${{ secrets.JIRA_BASE_URL }}
        JIRA_USER_EMAIL: ${{ secrets.JIRA_USER_EMAIL }}
        JIRA_API_TOKEN: ${{ secrets.JIRA_API_TOKEN }}
        TARGET_JIRA_PROJECT: #Your JIRA Project Key
        JIRA_LABEL: #Your label
