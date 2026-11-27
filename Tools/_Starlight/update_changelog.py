import os
import yaml
import re
from datetime import datetime
import time
from typing import Any
import requests
import sys
from github import Github

print("Environment Variables:")
changelog_path = os.getenv("CHANGELOG_FILE_PATH")
pr_number = os.getenv("PR_NUMBER")
repo_name = os.getenv("GITHUB_REPOSITORY")
github_token = os.getenv("GITHUB_TOKEN")
webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
print(f"CHANGELOG_FILE_PATH: {changelog_path}")
print(f"PR_NUMBER: {pr_number}")
print(f"GITHUB_REPOSITORY: {repo_name}")
print(f"GITHUB_TOKEN is set: {bool(github_token)}")
print(f"DISCORD_WEBHOOK_URL is set: {bool(webhook_url)}")

EMBED_DESCRIPTION_LIMIT = 4096
EMBED_TITLE_LIMIT = 256
EMBED_FIELD_NAME_LIMIT = 256
EMBED_FIELD_VALUE_LIMIT = 1024
TYPES_TO_EMOJI = {"Fix": "🐛", "Add": "🆕", "Remove": "❌", "Tweak": "⚒️"}

g = Github(github_token)
repo = g.get_repo(repo_name)
pr = repo.get_pull(int(pr_number))

def post_with_retries(payload: dict[str, Any]):
    attempt = 0
    while True:
        try:
            resp = requests.post(webhook_url, json=payload, timeout=10)
            if resp.status_code == 429:
                attempt += 1
                if attempt > 20:
                    print("Too many rate limit retries; giving up", file=sys.stderr)
                    sys.exit(1)
                retry_after = resp.json().get("retry_after", 5)
                print(f"Rate limited; sleeping {retry_after}s (attempt {attempt})")
                time.sleep(retry_after)
                continue
            resp.raise_for_status()
            return
        except requests.exceptions.RequestException as e:
            attempt += 1
            if attempt > 5:
                # Fail the job so the next run does not treat these entries as sent.
                print(f"Failed after retries: {e}", file=sys.stderr)
                sys.exit(1)
            backoff = 2 ** attempt
            print(f"Request failed ({e}), backing off {backoff}s and retrying")
            time.sleep(backoff)

def build_embed_for_pr(entries: list[dict[str,Any]], merge_time) -> dict[str, Any]:
    authors = set()
    description_lines: list[str] = []

    for entry in entries:
        if (type(entry) == str):
            continue
        authors.add(entry.get("author","unknown"))
        url = entry.get("url").strip() or None
        for change in entry.get("changes",[]):
            print(change)
            emoji = TYPES_TO_EMOJI.get(change.get("type",""), "❓")
            message = change.get("message","").strip()
            if len(message) > 300:
                message = message[:297].rstrip() + "..."
            line = f"{emoji} {message}"
            description_lines.append(line)

    description = "\n".join(description_lines)
    if len(description) > EMBED_DESCRIPTION_LIMIT:
        description = description[: EMBED_DESCRIPTION_LIMIT - 50].rstrip() + "\n*...truncated...*"

    sorted_authors = sorted(authors)
    authors_str = ", ".join(sorted_authors)
    title = authors_str
    if len(title) > EMBED_TITLE_LIMIT:
        # truncate authors part to fit
        overflow = len(title) - EMBED_TITLE_LIMIT + 3  # for "..."
        # remove overflow chars from authors_str
        truncated_authors = authors_str
        if overflow < len(authors_str):
            truncated_authors = authors_str[: -overflow].rstrip()
            # avoid cutting mid-comma: optionally rstrip to last comma-space
            if "," in truncated_authors:
                truncated_authors = truncated_authors.rsplit(",", 1)[0]
            truncated_authors = truncated_authors.rstrip() + "..."
        title = truncated_authors
        if len(title) > EMBED_TITLE_LIMIT:
            title = title[:EMBED_TITLE_LIMIT]

    author_field = ", ".join(sorted_authors)
    embed: dict[str, Any] = {
        "title": title,
        "description": description,
  #      "fields": [
  #          {"name": "Author(s)", "value": author_field[:EMBED_FIELD_VALUE_LIMIT], "inline": False}
  #      ],
        "footer": {"text": "Gear changelog"},
        "timestamp": merge_time.isoformat(timespec='microseconds'),
    }

    embed["url"] = entries[0].get("url","")
    return embed

def send_embed(embed: dict[str, Any]):
    payload = {
        "embeds": [embed],
        "allowed_mentions": {"parse": []},  # no automatic pings
    }
    post_with_retries(payload)

def remove_comments(pr_body):
    """
    Removes all content inside HTML comments <!-- --> from the PR body.
    """
    pattern = r"<!--.*?-->"
    cleaned_body = re.sub(pattern, "", pr_body, flags=re.DOTALL)
    return cleaned_body

def parse_changelog(pr_body, pr_author):
    blocks = []
    lines = pr_body.splitlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if line.startswith(":cl:"):
            author_raw = line.replace(":cl:", "").strip()
            author = author_raw if author_raw else pr_author
            i += 1

            changes = []
            while i < len(lines) and not lines[i].strip().startswith(":cl:"):
                change_match = re.match(r"-\s+(add|remove|tweak|fix):\s+(.+)", lines[i].strip())
                if change_match:
                    changes.append({
                        "type": change_match.group(1).capitalize(),
                        "message": change_match.group(2).strip()
                    })
                i += 1

            if changes:
                blocks.append({
                    "author": author,
                    "changes": changes
                })
        else:
            i += 1

    return blocks

def get_last_id(changelog_data):
    if not changelog_data or "Entries" not in changelog_data or not changelog_data["Entries"]:
        return 0
    return max(entry["id"] for entry in changelog_data["Entries"])

def update_changelog():
    if not pr.body:
        print("PR body is empty.")
        return

    print("Original PR Body:", repr(pr.body))
    cleaned_body = remove_comments(pr.body)
    print("Cleaned PR Body:", repr(cleaned_body))

    if ":cl:" in cleaned_body:
        print("Found ':cl:' in PR body after removing comments.")
        merge_time = pr.merged_at
        blocks = parse_changelog(cleaned_body, pr.user.login)
        changes : list[dict[str,Any]] = []

        print("Parsed entries:", blocks)

        if not blocks:
            print("No changelog entries found after parsing.")
            return

        if os.path.exists(changelog_path):
            print(f"Changelog file exists at {changelog_path}")
            with open(changelog_path, "r", encoding='utf-8') as file:
                changelog_data = yaml.safe_load(file) or {"Entries": []}
        else:
            print(f"Changelog file does not exist and will be created at {changelog_path}")
            changelog_data = {"Entries": []}
        calculatedID = (int(pr_number) * 100)
        for i, block in enumerate(blocks, start=1):
            #shift PR number up two digits
            #add current ID to it
            # e.g., PR number 123 -> calculatedID = (123 * 100) = 12300
            changelog_entry = {
                "author": block["author"],
                "changes": block["changes"],
                "id": calculatedID + i,
                "time": merge_time.isoformat(timespec='microseconds'),
                "url": f"https://github.com/{repo_name}/pull/{pr_number}"
            }
            changes.append(changelog_entry)
            changelog_data["Entries"].append(changelog_entry)

        os.makedirs(os.path.dirname(changelog_path), exist_ok=True)

        with open(changelog_path, "w", encoding='utf-8') as file:
            yaml.dump(changelog_data, file, allow_unicode=True)
            file.write('\n')
        print(f"Changelog updated and written to {changelog_path}")

        if (bool(webhook_url)):
            send_embed(build_embed_for_pr(changes,merge_time))
    else:
        print("No ':cl:' tag found in PR body after removing comments.")
        return

if __name__ == "__main__":
    update_changelog()
