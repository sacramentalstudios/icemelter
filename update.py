name: Update Ice Melter
on:
  schedule:
    - cron: '*/15 * * * *'
  workflow_dispatch:
permissions:
  contents: write
jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install feedparser
      - run: python update.py
      - uses: stefanzweifel/git-auto-commit-action@v5
        with:
          commit_message: "Ice melted — feed updated"
          file_pattern: docs/feed.xml
