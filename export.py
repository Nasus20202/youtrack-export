import requests
import os
import json
from github import Github, GithubIntegration, Auth as GithubAuth
from datetime import datetime
from jinja2 import Template
import random


def get_env(name: str, default: str = None) -> str:
    value = os.environ.get(name)
    if value is None and default is not None:
        return default
    if not value:
        raise ValueError(f"Environment variable {name} is not set")
    return value


def format_date(timestamp: int) -> str:
    return datetime.fromtimestamp(timestamp // 1000).strftime("%Y-%m-%d %H:%M")


YOUTRACK_URL = get_env("YOUTRACK_URL")
YOUTRACK_TOKEN = get_env("YOUTRACK_TOKEN")
GITHUB_REPO = get_env("GITHUB_REPO")
GITHUB_TOKEN = get_env("GITHUB_TOKEN", "")
GITHUB_APP_ID = get_env("GITHUB_APP_ID", "")

youtrack_session = requests.Session()
youtrack_session.headers.update({"Authorization": f"Bearer {YOUTRACK_TOKEN}"})

if GITHUB_TOKEN:
    print("Using GitHub token")
    github = Github(auth=GithubAuth.Token(GITHUB_TOKEN))
elif GITHUB_APP_ID:
    print(f"Using GitHub App {GITHUB_APP_ID}")

    with open("key.pem", "r") as f:
        auth = GithubAuth.AppAuth(GITHUB_APP_ID, f.read())

    github_integration = GithubIntegration(auth=auth)

    if not github_integration.get_installations():
        raise ValueError("No GitHub installations found")

    found = False
    for installation in github_integration.get_installations():
        github = installation.get_github_for_installation()
        try:
            github.get_repo(GITHUB_REPO)
            found = True
            break
        except:
            continue

    if not found:
        raise ValueError(
            f"Repository {GITHUB_REPO} not found for any of the installations"
        )

else:
    raise ValueError("Either GITHUB_TOKEN or GITHUB_APP_ID must be set")


# Fetch all issues from YouTrack

issues_list = youtrack_session.get(f"{YOUTRACK_URL}api/issues").json()
issue_ids = [issue["id"] for issue in issues_list]

print(f"Found {len(issue_ids)} issues on YouTrack")

issues = []
for issue_id in issue_ids:
    issue = youtrack_session.get(
        f"{YOUTRACK_URL}api/issues/{issue_id}?fields=id,idReadable,summary,description,created,updated,resolved,customFields(name,value(name,presentation,text)),comments(created,text,author(fullName)),tags(name)"
    ).json()

    issues.append(issue)

issues = sorted(issues, key=lambda issue: issue["created"])

with open("issues.json", "w") as f:
    json.dump(issues, f, indent=2)

print("Issues exported to issues.json")


# Create issues on GitHub

repo = github.get_repo(GITHUB_REPO)
print(f"Found GitHub repository {repo.full_name}")

current_issues = repo.get_issues(state="all")

with open("issue_template.jinja", "r") as f:
    template = Template(f.read())

for youtrack_issue in issues:
    title = f"[{youtrack_issue['idReadable']}] {youtrack_issue['summary']}"
    if any(current_issue.title == title for current_issue in current_issues):
        print(
            f"Skipping issue {youtrack_issue['idReadable']} as it already exists on GitHub"
        )
        continue

    print(f"Creating issue {youtrack_issue['idReadable']} on GitHub")

    body = template.render(
        issue=youtrack_issue,
        format_date=format_date,
        youtrack_url=YOUTRACK_URL,
    )

    labels = [tag["name"] for tag in youtrack_issue["tags"]] + [
        "imported-from-youtrack"
    ]

    for label in labels:
        try:
            repo.get_label(label)
        except:
            print(f"Creating label {label}")
            repo.create_label(
                name=label,
                color="".join([f"{random.randint(0, 255):02x}" for _ in range(3)]),
            )

    issue = repo.create_issue(title=title, body=body, labels=labels)

    # Create comments on GitHub
    comments = sorted(
        youtrack_issue["comments"], key=lambda comment: comment["created"]
    )
    for comment in comments:
        body = f"_{comment['author']['fullName']} commented on {format_date(comment['created'])}:_\n{comment['text']}"
        issue.create_comment(body)

    # Close issue if resolved
    if youtrack_issue["resolved"]:
        issue.edit(state="closed")
