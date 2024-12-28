# YouTrack export

Export YouTrack issues Github issues.

## Usage

| Environment variable | Description                        |
| -------------------- | ---------------------------------- |
| YOUTRACK_URL         | URL of the YouTrack instance       |
| YOUTRACK_TOKEN       | Your YouTrack API token            |
| GITHUB_REPO          | Github repository name             |
| GITHUB_TOKEN         | Your Github API token _(optional)_ |
| GITHUB_APP_ID        | Github App ID _(optional)_         |

You can use Github token or Github App ID to authenticate. If you use Github App ID, you need to install the app to the repository and put the private key in the `key.pem` file.

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export YOUTRACK_URL=https://xxx.youtrack.cloud/
export YOUTRACK_TOKEN=...
export GITHUB_REPO=name/repo
export GITHUB_TOKEN=...
export GITHUB_APP_ID=123456
echo "private key" > key.pem

python export.py
```