# actions-demo
Example repository for working with github actions

## Github Actions

## ...

Github Actions are software scripts triggered by Github events

## Github Events

- schedule
- workflow_dispatch
- repository_dispatch
- check_run
- create
- delete
- deployment
- fork
- issue_comment
- issues
- page_build
- project
- project_card
- public
- pull_request
- pull_request_review
- pull_request_review_comment
- pull_request_target
- push
- registry_package
- release
- status
- watch
- workflow_run
- etc

## Github Event - push

```
name: unittest
on:
  push:
    branches:
      - master
  pull_request:
    branches:
      - master

jobs:
  unittest:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version : '3.9'
      - name: Run unittests
        run:  python -m unittest discover -v
```

## Github Event - pull_request
```
name: release
on:
  release:
    types: [created]

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v2
      - name: Setup python
        uses: actions/setup-python@v2
        with:
          python-version : '3.9'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Build
        env:
          RELEASE_VERSION: ${{ github.event.release.tag_name }}
        run: python setup.py sdist bdist_wheel
      - name: Archive build
        uses: actions/upload-artifact@v2
        with:
          name: dist-${{ github.event.release.tag_name }}
          path: dist
      - name: Publish build
        env:
          TWINE_USERNAME: ${{ secrets.PYPI_USERNAME }}
          TWINE_PASSWORD: ${{ secrets.PYPI_PASSWORD }}
        run: |
          python -m twine upload --verbose dist/*
```

