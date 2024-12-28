# YouTrack export

Export YouTrack issues Github issues.

## Usage

| Environment variable | Description                  |
| -------------------- | ---------------------------- |
| YOUTRACK_URL         | URL of the YouTrack instance |
| YOUTRACK_TOKEN       | Your YouTrack API token      |
| GITHUB_REPO          | Github repository name       |
| GITHUB_TOKEN         | Your Github API token        |


```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export YOUTRACK_URL=https://xxx.youtrack.cloud/
export YOUTRACK_TOKEN=...
export GITHUB_REPO=name/repo
export GITHUB_TOKEN=...

python export.py
```