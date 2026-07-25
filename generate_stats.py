name: Update GitHub Profile Assets
on:
  schedule:
    - cron: '0 0 * * *'
  workflow_dispatch:
  push:
    branches:
      - main
jobs:
  update-assets:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
      - name: Create assets directory
        run: mkdir -p assets
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Generate GitHub Stats SVG
        env:
          GITHUB_TOKEN: ${{ secrets.PAT_TOKEN }}
          GITHUB_USERNAME: suraj-yadav0
          OUTPUT_PATH: assets/stats.svg
        run: python generate_stats.py
      - name: Commit and Push Changes
        run: |
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git config user.name "github-actions[bot]"
          git add assets/
          if git diff --staged --quiet; then
            echo "No changes to commit"
          else
            git commit -m "📊 Update GitHub Profile Assets [$(date +'%Y-%m-%d')]"
            git push
          fi
