## Introduction

This is an Open Source community project. Project contributors may be able to help, depending on their time and availability. Please be specific about what you're trying to do, your system, and steps to reproduce your scenario when opening a GitHub issue.

For bug reports, please [open an issue](https://github.com/trendmicro/cloudone-community/issues/new/choose)

For any other topic including but not limited to: ideas, feedback, questions, and many more... We have a discussion tab enabled, in this tab, you can ask questions and interact with all of our community. To get started, here's how you can [Open a Discussion](https://github.com/trendmicro/cloudone-community/discussions/new).

You are also welcome to [contribute](https://github.com/trendmicro/cloudone-community#for-contributors) to this project to improve our community.

> Note: Official support from Trend Micro is not available. Individual contributors may be Trend Micro employees but are not official support.

## For Contributors

We :heart: contributions from the community. To submit changes, please review the following information.

### Contributor Guidelines

Some tips before you start contributing to this project:

- The folder structure convention for this repo is '`/product-name/activity-name/{cloud-provider}-{language or framework}-your-script-foldername`'.

> For example, `/Workload-Security/Integration/aws-cdk-workload-iam-stack`

**Note:** The `{cloud-provider}` is mandatory for the cases that it's applied, such as `aws-cdk-workload-iam-stack`. For others cases is not necessary, but use your best judgement before submit the PR.

- Recommended to create a README for your folder to make it easier for the community to make use of your script.
- Writing separate test scripts in the `/tests` folder or having a built-in `dry-run` mode in the script to ensure everyone can test your script in their environment is much appreciated :)
- Images and other assets are a welcome addition to your scripts to help everyone run tests / look at examples. Ensure they are stored in relevant folders beside your script, like `/img`, `/assets`, `/examples`, `/tests`. :warning: Avoid including logs with your submission unless it is used as an example. In that case, examples can be included in an `/examples` folder.
- Using language-specific linters is super beneficial for easier code reviews.
- For Python scripts, please consider submitting a `requirements.txt` file within your script folder for easier deployment. You can generate a requirements.txt file using the following command

``` bash
# Install and run in current directory

#  For Python 3:
pip3 install pipreqs
python3 -m  pipreqs.pipreqs .

#  For Python 2:
pip install pipreqs
python -m  pipreqs.pipreqs .

# To check your python version:
python --version
```

### Contribute

1.  [Open a Discussion](https://github.com/trendmicro/cloudone-community/discussions/new) before you start contributing so we can discuss the changes and it's alignment with the scope of this project.
2.  Review the [Contributor Guidelines](https://github.com/trendmicro/cloudone-community#for-contributors)
3. If you are new to GitHub / Git, review the helpful documentation here in our [Wiki](https://github.com/trendmicro/cloudone-community/wiki) before proceeding.
4.  Fork this repository.
5.  Create a new feature branch, preferably from the `main` branch.
6.  Commit your code with a message that is structured according to the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification.
7.  Make your changes.
8.  Submit a pull request with an explanation for your changes or additions.

We will review and work with you to release the changes.
