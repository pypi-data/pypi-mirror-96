## 3.1.1

- Fix bug where `assigner commit -S` would not commit staged changes
- Official support for Python 3.9!
- Minor changes to certain exception messages

## 3.1.0

- Add `-S` option to `commit` command to allow for GPG-signed commits
- Change `score` command defaults to be more generic
- Fix a bug in `score` that occurred when a student's repo did not exist

## 3.0.0

- Add auto-uploading functionality with `score` command to grab autograder results
  from repo CI artifacts and upload them to Canvas.  Also checks for student tampering
  with grading-related files.
- Tidy up some docs, clarifying new features and making things more informative

## 2.0.2

- Fix bugs with and severely de-cruft Gitlab timestamp parsing

## 2.0.1

- Fix issue where ASCII-only terminals cannot display progress bars

## 2.0.0

- Added 'commit' command to commit changes to student repos
- Added 'push' command to push commits to student repos
- Retry clones that fail with 'Connection reset by peer' using exponential backoff
- Offer to create GitLab group in `assigner init`
- Version configuration; automatically upgrade old configs to latest version
- Make GitLab backend configuration generic
- Tidy up progress bars with logging output
- Test all supported python versions (3.4-3.7) automatically
- Added `BackendBase`, `RepoBase`, `StudentRepoBase`, and `TemplateRepoBase`.
- Base Repos are now called Template Repos.
- Separated Gitlab backend from most of the code. Added Base implementations for Gitlab.
- Added `requires_backend_and_config` decorator with backend config option to load the desired backend.
- Renamed `config_context` decorator to `requires_config`.
- pyflakes 1.6.0 upgrade for type annotations fixes.
- Improved canvas error handling.

## 1.2.0

- Branch names are shown each on their own line in `assigner status` to make output more legible
- Send GitLab authentication token in HTTP header rather than request parameters
- Print informative message if `git` is not installed
- Use a shared HTTPS session for API calls to speed up operations
- Add `--version` flag to Assigner

## 1.1.1

- Fixed `get` failing to clone new repos with error `Remote branch ['master'] not found in upstream origin`

## 1.1.0

- Warn when an assignment is already open for a student when running `open`
- Calling `assign` with the `--open` flag assigns and opens an assignment in one step
- Removed remaining lint as specified by pylint.
- Removed old baserepo standalone code.
- Added Travis CI config for pylint and pyflakes.
- Added unittest scaffolding with nose
- Added `AssignerTestCase`, tests for `assigner`, `assigner get`, and all `--help` uses.

## 1.0.0

- Rename `token` to `gitlab-token` in the configuration file
- Display push time, rather than commit time, in `status` output
- Show push time in human-readable format in the current locale's timezone
- Display an informative error message when attempting to push an empty base repo
- Allow users to assign multiple branches in one call to `assign`
- Print help for the subcommand when `assigner help <command>` is run
- Fetch and pull branches when `get` is run if student repositories have already been cloned

## 0.1.0

This is the """"initial release""" that's been in use for a couple years now.
If you want to know what happened prior to this, sorry, you're going to have to read the commit log.
