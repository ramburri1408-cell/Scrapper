name: Company Discovery

on:
  workflow_dispatch:

jobs:
  discover-companies:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          pip install requests

      - name: Run company discovery
        run: |
          python agent/company_discovery.py

      - name: Upload companies artifact
        uses: actions/upload-artifact@v4
        with:
          name: companies-json
          path: data/companies.json
