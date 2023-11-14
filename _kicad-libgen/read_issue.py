
import os
from github import Github

def read_github_issue(repository, issue_number):
    # Get the GitHub token from the environment variable
    token = os.environ.get('GH_TOKEN')

    # Create a Github object using the token
    g = Github(token)

    # Access the repository
    repo = g.get_repo(repository)

    try:
        issue = repo.get_issue(issue_number)
        issue_body = issue.body
        # parse the issue body
        # split the issue body into lines
        issue_body = issue_body.splitlines()
        # remove empty lines
        issue_body = [line for line in issue_body if line != '']
        thing_dict = {}
        # first line is pid
        pid = issue_body[1]
        thing_dict['pid'] = pid
        # find the first line that contains "Overwrite"
        overwrite_line = [line for line in issue_body if "Overwrite" in line][0]
        # if overwrite_line contains [X] then overwrite is True
        if "[X]" in overwrite_line:
            overwrite = True
        else:
            overwrite = False
        thing_dict['overwrite'] = overwrite
        # find the first line that contains "without LCSC"
        without_lcsc_line = [line for line in issue_body if "without LCSC" in line][0]
        # if without_lcsc_line contains [X] then without_lcsc is True
        if "[X]" in without_lcsc_line:
            without_lcsc = True
        else:
            without_lcsc = False
        thing_dict['without_lcsc'] = without_lcsc
        # find the first line that contains "### Manufacturer Part Number"
        mpn_line = [line for line in issue_body if "### Manufacturer Part Number" in line][0]
        # the next line is the mpn
        mpn = issue_body[issue_body.index(mpn_line)+1]
        thing_dict['mpn'] = mpn
        # find the first line that contains "### Manufacturer"
        mfr_line = [line for line in issue_body if "### Manufacturer" in line][0]
        # the next line is the mfr
        mfr = issue_body[issue_body.index(mfr_line)+1]
        thing_dict['mfr'] = mfr
        # for each line that contains ":", split the line into key and value, strip spaces from value and add them to a dict called values_dict
        for line in issue_body:
            if ":" in line:
                key, value = line.split(":")
                # strip spaces from beginning and end of value
                value = value.strip()
                thing_dict[key] = value

        print("thing_dict:", thing_dict)
        return thing_dict

    except Exception as e:
        print(f"Error: {e}")
        return e