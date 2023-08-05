# CircleCI CLI

[![CircleCI](https://circleci.com/gh/lightspeed-hospitality/circleci-cli.svg?style=svg&circle-token=639e11bbab82eb96b4cc285724c17de30fecf8ce)](https://app.circleci.com/pipelines/github/lightspeed-hospitality/circleci-cli)

<p align="center">
  <a href="#install">Install</a> •
  <a href="#commands">Commands</a> •
  <a href="#development">Development</a> •
  <a href="#how-to-contribute">Contribute</a> •
  <a href="#support--feedback">Support</a>
</p>

🛠 WIP
This is a small CircleCI CLI that allows you to interact with the [CircleCI API v2](https://circleci.com/docs/api/v2/).

---

## Install

1. If you're on macOS, it's recommended you install Python 3 via Homebrew first:
    ```sh
    brew install python3
    ```

2. Install `cci`:
    ```sh
    pip3 install --user cci-cli
    ```

3. Open a new shell and type `cci --help`. You should see help output.

    > ⚠️ No output? You might need to update your `PATH`. On macOS, try adding this to your `.zshrc`:
    > ```sh
    > export PATH="$PATH:$HOME/Library/Python/3.9/bin"
    > ```
    > (check which version of Python 3 you are using).

4. Generate a personal CircleCI API token [here](https://app.circleci.com/settings/user/tokens).

5. Give this token to `cci`:
    ```sh
    cci config setup --vcs gh --org lightspeed-hospitality --token <circle-ci-api-token>
    ```

### Install completions

For shell completion, run `cci --install-completion zsh` (or `bash`, if you use bash).

> ⚠️ If you use `zsh`, the configuration added to the bottom of your `.zshrc` [is wrong](https://github.com/tiangolo/typer/pull/237) and need to be adjusted. Replace:
> ```sh
> compinit
> zstyle ':completion:*' menu select
> fpath+=~/.zfunc
> ```
> With:
> ```sh
> fpath+=~/.zfunc
> compinit
> ```

### Docker

If you don't want to install `cci` locally, you can run it from Docker:

```sh
alias cci='docker pull lightspeedhq-ls-container-dev.jfrog.io/circleci-cli && docker run -it --rm --volume=$HOME/.config/circleci-cli:/root/.config/circleci-cli lightspeedhq-ls-container-dev.jfrog.io/circleci-cli'
```

## Commands

**Display your config**
```
cci config show
```


**List the last 20 pipelines for `<project-name>`**
```
cci pipelines list <project-name>
```

**Trigger a build for `<project-name>` using `<branch>`**
```
cci pipelines trigger <project-name> --branch <branch> [--wait-for-result] [--timeout <min>] [--params key=value,...]
```

## Development

### Setup

For development, best create a virtual environment and install all dependencies:
```console
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
```

### Build

You can create a docker image on your local machine by:
```console
docker build . -t circleci-cli
```

### Run

In order to run the build you created on your local machine, run:
```console
docker run -it --rm --volume=$HOME/.config/circleci-cli:/root/.config/circleci-cli circleci-cli
```

## How to Contribute

In order to contribute you just have to have Python installed on your machine. In case you do not have it installed get it from [python.org](https://www.python.org/downloads/).

#### Linting Tool

This project is using [pre-commit](https://pre-commit.com/) to enable linting and auto-formatting as a pre-commit hook.
The hooks are configured in [.pre-commit-config.yaml](./.pre-commit-config.yaml).

To install the hooks you have to run the following command (only once):
```bash
. venv/bin/activate
pre-commit install
```

Then you can trigger all the hooks manually by running:
```bash
. venv/bin/activate
pre-commit run --all-files
```

Additionally on every `git commit` the hooks will be triggered and have to pass.

#### How to run tests

You can run all the tests, by simply running:
```bash
. venv/bin/activate
python -m pytest
```

## Support & Feedback

Your contribution is very much appreciated. Feel free to create a PR or an Issue with your suggestions for improvements.
