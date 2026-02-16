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
        "followers": user["followers"]["totalCount"],
        "repos": user["repositories"]["totalCount"],
    }


def format_number(n):
    """Format number with k/M suffix."""
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}k"
    return str(n)


def calculate_rank(stats):
    """Calculate user rank based on stats, similar to github-readme-stats."""
    import math

    def log_norm(value, median, spread=1.0):
        """Log-normal CDF approximation."""
        if value <= 0:
            return 0
        log_val = math.log(value + 1)
        log_med = math.log(median + 1)
        z = (log_val - log_med) / spread
        # Approximate CDF using tanh
        return 0.5 * (1 + math.tanh(z * 0.7))

    # Weighted score based on typical GitHub user medians
    score = (
        log_norm(stats["commits"], 250, 1.5) * 0.30 +
        log_norm(stats["prs"], 50, 1.5) * 0.20 +
        log_norm(stats["issues"], 25, 1.5) * 0.10 +
        log_norm(stats["reviews"], 10, 1.5) * 0.10 +
        log_norm(stats["stars"], 50, 1.5) * 0.15 +
        log_norm(stats["followers"], 10, 1.5) * 0.05 +
        log_norm(stats["contributed_to"], 5, 1.0) * 0.10
    )

    # Map score to ranks
    ranks = [
        (0.95, "S+"),
        (0.85, "S"),
        (0.75, "A++"),
        (0.65, "A+"),
        (0.50, "A"),
        (0.35, "B+"),
        (0.20, "B"),
    ]
    rank_label = "C"
    for threshold, label in ranks:
        if score >= threshold:
            rank_label = label
            break

    return rank_label, min(score, 1.0)


def generate_svg(stats):
    """Generate an SVG card matching the highcontrast theme with rank badge."""
    name = stats["name"]
    rank_label, rank_score = calculate_rank(stats)

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
    stats_area_width = 310

    # Build stat rows
    stat_rows = ""
    for i, (icon, label, value) in enumerate(items):
        y = 72 + i * 25
        stat_rows += f"""
    <g transform="translate({padding_x}, {y})">
      <text x="0" y="0" class="stat-icon">{icon}</text>
      <text x="25" y="0" class="stat-label">{label}:</text>
      <text x="{stats_area_width}" y="0" class="stat-value" text-anchor="end">{format_number(value)}</text>
    </g>"""

    # Rank badge - circle with progress ring
    ring_cx = card_width - 70
    ring_cy = card_height // 2 + 8
    ring_r = 40
    ring_circumference = 2 * 3.14159 * ring_r
    progress_offset = ring_circumference * (1 - rank_score)

    # Rank color based on rank
    rank_colors = {
        "S+": "#FFD700", "S": "#FFD700",
        "A++": "#F5A623", "A+": "#F5A623", "A": "#F5A623",
        "B+": "#4CAF50", "B": "#4CAF50",
        "C": "#9f9f9f",
    }
    rank_color = rank_colors.get(rank_label, "#F5A623")

    # Font size for rank label
    rank_font_size = 28 if len(rank_label) <= 2 else 22

    rank_badge = f"""
    <g transform="translate(0, 0)">
      <!-- Background ring -->
      <circle cx="{ring_cx}" cy="{ring_cy}" r="{ring_r}"
              fill="none" stroke="#333333" stroke-width="5" opacity="0.4"/>
      <!-- Progress ring -->
      <circle cx="{ring_cx}" cy="{ring_cy}" r="{ring_r}"
              fill="none" stroke="{rank_color}" stroke-width="5"
              stroke-dasharray="{ring_circumference}"
              stroke-dashoffset="{progress_offset:.1f}"
              stroke-linecap="round"
              transform="rotate(-90 {ring_cx} {ring_cy})"
              class="rank-ring"/>
      <!-- Rank text -->
      <text x="{ring_cx}" y="{ring_cy}" class="rank-text"
            text-anchor="middle" dominant-baseline="central"
            style="font-size: {rank_font_size}px; fill: {rank_color};">{rank_label}</text>
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
      .rank-text {{
        font-family: 'Segoe UI', Ubuntu, 'Helvetica Neue', Sans-Serif;
        font-weight: 700;
      }}
      .rank-ring {{
        animation: rankAnimation 1s ease-in-out forwards;
      }}
      @keyframes fadeInAnimation {{
        from {{ opacity: 0; }}
        to {{ opacity: 1; }}
      }}
      @keyframes rankAnimation {{
        from {{ stroke-dashoffset: {ring_circumference}; }}
        to {{ stroke-dashoffset: {progress_offset:.1f}; }}
      }}
    </style>
  </defs>

  <rect x="0.5" y="0.5" width="{card_width - 1}" height="{card_height - 1}" class="card-bg"/>

  <g transform="translate(0, 0)">
    <text x="{padding_x}" y="{title_y}" class="card-title">{name}'s GitHub Stats</text>
    {stat_rows}
    {rank_badge}
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

    rank_label, rank_score = calculate_rank(stats)
    print(f"  🏅 Rank: {rank_label} (score: {rank_score:.2f})")

    svg = generate_svg(stats)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg)

    print(f"✅ Stats SVG saved to {output_path}")


if __name__ == "__main__":
    main()
