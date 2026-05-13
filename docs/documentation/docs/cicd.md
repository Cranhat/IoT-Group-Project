## CI/CD

This project uses GitHub Actions for continuous integration. The workflow is triggered on every push and pull request, so code is tested before it is merged and after new changes are added to the repository.

The CI job runs tests on a matrix of operating systems and Python versions:

- Operating systems: Ubuntu and Windows
- Python versions: 3.10, 3.11, and 3.12

This means the same test suite is executed six times in total, covering each combination of operating system and Python version. The workflow has `fail-fast` disabled, so if one combination fails, the remaining combinations still continue. This makes it easier to see whether a problem affects only one environment or the whole project.

For each matrix entry, GitHub Actions performs the following steps:

1. Checks out the repository code.
2. Installs the selected Python version.
3. Upgrades `pip` and installs backend dependencies from requirements.
4. Runs the test suite with `pytest`.
