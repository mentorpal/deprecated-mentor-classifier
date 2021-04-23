# mentor-classifier

## TODO

- [ ] update to python 3.8
- [ ] fix nltk impl so that datasets autodownload (not in makefiles or docker)

A short answer classifier service focused on cold-start performance

This repo contains two subprojects:

- mentor-classifier: core implementation of training and inference
- mentor-classifier-api: a REST api for answer classification as a service in the app

## Requirements

- [recommended] [penv](https://github.com/pyenv/pyenv-installer) to simplify python version management. 
- python3.6 (must be in path as `python3.6` to build virtualenv)
- make

## Development

Generally you'll be working in the sub projects, so refer to README there within

## Licensing

All source code files must include a USC open license header.

To check if files have a license header:

```
make test-license
```

To add license headers:

```
make license
```

## Releases

Currently, this image is semantically versioned. When making changes that you want to test in another project, create a branch and PR and then you can release a test tag one of two ways:

To build/push a work-in-progress tag of `mentor-classifier` for the current commit in your branch

To build/push a pre-release semver tag of `mentor-classifier` for the current commit in your branch

- create a [github release](https://github.com/ICTLearningSciences/mentor-classifier/releases/new) **from your development branch** with tag format `/^\d+\.\d+\.\d+(-[a-z\d\-.]+)?$/` (e.g. `1.0.0-alpha.1`)
- this will create a tag like `uscictdocker/mentor-classifier:1.0.0-alpha.1`
- you can follow progress in [github actions](https://github.com/mentor/mentor-classifier/actions)


Once your changes are approved and merged to main, you should create a release tag in semver format as follows:

- create a [github release](https://github.com/ICTLearningSciences/mentor-classifier/releases/new) **from main** with tag format `/^\d+\.\d+\.\d$/` (e.g. `1.0.0`)
- this will create a tag like `uscictdocker/mentor-classifier:1.0.0`
- you can follow progress in [github actions](https://github.com/mentor/mentor-classifier/actions)

