"""
Generate a GitHub Stats SVG card using the GitHub GraphQL API.
Replicates the look of github-readme-stats with the highcontrast theme.
"""

import json
import os
import sys
import urllib.request
import urllib.error


def fetch_github_stats(username, token):
    """Fetch user stats from GitHub GraphQL API."""
    query = """
    query($login: String!) {
      user(login: $login) {
        name
        repositoriesContributedTo(contributionTypes: [COMMIT, ISSUE, PULL_REQUEST, REPOSITORY]) {
          totalCount
        }
        contributionsCollection {
          totalCommitContributions
          restrictedContributionsCount
          totalPullRequestContributions
          totalIssueContributions
          totalPullRequestReviewContributions
        }
        pullRequests(first: 1) {
          totalCount
        }
        issues(first: 1) {
          totalCount
        }
        followers {
          totalCount
        }
        repositories(first: 100, ownerAffiliations: OWNER, orderBy: {direction: DESC, field: STARGAZERS}) {
          totalCount
          nodes {
            stargazers {
              totalCount
            }
          }
        }
      }
    }
    """
    payload = json.dumps({"query": query, "variables": {"login": username}}).encode("utf-8")
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=payload,
        headers={
            "Authorization": f"bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "github-stats-generator",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"❌ GitHub API error: {e.code} {e.reason}")
        sys.exit(1)

    if "errors" in data:
        print(f"❌ GraphQL errors: {data['errors']}")
        sys.exit(1)

    user = data["data"]["user"]
    contrib = user["contributionsCollection"]
    total_stars = sum(r["stargazers"]["totalCount"] for r in user["repositories"]["nodes"])
    total_commits = contrib["totalCommitContributions"] + contrib["restrictedContributionsCount"]

    return {
        "name": user["name"] or username,
        "stars": total_stars,
        "commits": total_commits,
        "prs": user["pullRequests"]["totalCount"],
        "issues": user["issues"]["totalCount"],
        "contributed_to": user["repositoriesContributedTo"]["totalCount"],
        "reviews": contrib["totalPullRequestReviewContributions"],
    }


def format_number(n):
    """Format number with k/M suffix."""
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}k"
    return str(n)


def generate_svg(stats):
    """Generate an SVG card matching the highcontrast theme."""
    name = stats["name"]
    items = [
        ("⭐", "Total Stars Earned", stats["stars"]),
        ("📝", "Total Commits", stats["commits"]),
        ("🔀", "Total PRs", stats["prs"]),
        ("🔴", "Total Issues", stats["issues"]),
        ("📦", "Contributed to", stats["contributed_to"]),
    ]

    card_width = 495
    card_height = 195
    padding_x = 25
    title_y = 35

    # Build stat rows
    stat_rows = ""
    for i, (icon, label, value) in enumerate(items):
        y = 72 + i * 25
        stat_rows += f"""
    <g transform="translate({padding_x}, {y})">
      <text x="0" y="0" class="stat-icon">{icon}</text>
      <text x="25" y="0" class="stat-label">{label}:</text>
      <text x="{card_width - padding_x * 2 - 10}" y="0" class="stat-value" text-anchor="end">{format_number(value)}</text>
    </g>"""

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{card_width}" height="{card_height}" viewBox="0 0 {card_width} {card_height}">
  <defs>
    <style>
      .card-bg {{
        fill: #000000;
        stroke: #e4e2e2;
        stroke-width: 1;
        rx: 4.5;
      }}
      .card-title {{
        font: 600 18px 'Segoe UI', Ubuntu, 'Helvetica Neue', Sans-Serif;
        fill: #e4e2e2;
        animation: fadeInAnimation 0.8s ease-in-out forwards;
      }}
      .stat-label {{
        font: 400 14px 'Segoe UI', Ubuntu, 'Helvetica Neue', Sans-Serif;
        fill: #9f9f9f;
      }}
      .stat-value {{
        font: 700 14px 'Segoe UI', Ubuntu, 'Helvetica Neue', Sans-Serif;
        fill: #e4e2e2;
      }}
      .stat-icon {{
        font-size: 14px;
      }}
      @keyframes fadeInAnimation {{
        from {{ opacity: 0; }}
        to {{ opacity: 1; }}
      }}
    </style>
  </defs>

  <rect x="0.5" y="0.5" width="{card_width - 1}" height="{card_height - 1}" class="card-bg"/>

  <g transform="translate(0, 0)">
    <text x="{padding_x}" y="{title_y}" class="card-title">{name}'s GitHub Stats</text>
    {stat_rows}
  </g>
</svg>"""
    return svg


def main():
    username = os.environ.get("GITHUB_USERNAME", "suraj-yadav0")
    token = os.environ.get("GITHUB_TOKEN")
    output_path = os.environ.get("OUTPUT_PATH", "assets/stats.svg")

    if not token:
        print("❌ GITHUB_TOKEN environment variable is required")
        sys.exit(1)

    print(f"📊 Fetching stats for {username}...")
    stats = fetch_github_stats(username, token)

    print(f"  ⭐ Stars: {stats['stars']}")
    print(f"  📝 Commits: {stats['commits']}")
    print(f"  🔀 PRs: {stats['prs']}")
    print(f"  🔴 Issues: {stats['issues']}")
    print(f"  📦 Contributed to: {stats['contributed_to']}")

    svg = generate_svg(stats)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg)

    print(f"✅ Stats SVG saved to {output_path}")


if __name__ == "__main__":
    main()
