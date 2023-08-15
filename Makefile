#################################################################################
#################### MAKEFILE FOR ANALYSIS MODEL TEMPLATE #######################
#################################################################################

#####################################
## Set PROJECT_PATH AND SHELL_PROFILE
#####################################
PROJECT_PATH=${PWD}
SHELL_PROFILE=${SHELL_PROFILE_PATH}

#######
## Init
#######
ifdef SHELL_PROFILE_PATH
init: poetry paths docker
	@[ -f ./jenkins_pr.yml ] && mkdir .github && mkdir .github/workflows && mv jenkins_pr.yml .github/workflows/ || true
	@echo "Running shell..."
	@poetry shell
	@echo ""
else
init:
	@read -p "Your profile (.bashrc, .zshrc, .bash_profile, etc)?: " PROFILE; \
	echo "export SHELL_PROFILE_PATH='${HOME}/$$PROFILE'" >> ~/$$PROFILE; \
	echo "\033[0;33mSource your profile\033[0m";
endif

#################
## Change version
#################
change-version:
ifdef version
	@echo ""
	@old_version=$(shell cat pyproject.toml | awk '/^version =/{print $$3}' | xargs); \
	echo "Changing from version v$$old_version to v${version}..."; \
	sed "s/v$$old_version/v${version}/g" README.md > temp && mv temp README.md
	@cat pyproject.toml | awk '/^version =/{gsub($$3,"\"${version}\"")};{print}' > temp && mv temp pyproject.toml
	@echo ""
else
	@echo ""
	@echo "Please set the version number: version=<version number>"
	@echo ""
endif

#########
## Docker
#########
docker:
	@echo ""
	@echo "No docker services needed."
	@echo ""

#################################
## Exported environment variables
#################################
paths:
	@echo ""
	@echo "No exported paths needed."
	@echo ""

############################
## Poetry and ipykernel init
############################
poetry:
	@echo ""
	@echo "Installing dependencies in poetry environment..."
	@poetry install
	@echo ""
	@echo "Installing pre-commit..."
	@poetry run pre-commit install
	@echo ""

poetry-remove:
	@echo ""
	@echo "Removing poetry environment $(shell poetry env list | awk '{print $$1}')..."
	@poetry env remove $(shell poetry env list | awk '{print $$1}')
	@echo "Poetry environment removed."
	@echo ""
	@echo "Removing poetry.lock..."
	@rm poetry.lock
	@echo "Poetry lock removed."
	@echo ""

#############
## Pre-commit
#############
pre-commit:
	@cd ${PROJECT_PATH}/
	@git add .
	@pre-commit run

pre-commit-jenkins:
	@cd ${PROJECT_PATH}/
	@git add .
	@pre-commit run
	@poetry run pre-commit run --all-files trailing-whitespace
	@poetry run pre-commit run --all-files check-executables-have-shebangs
	@poetry run pre-commit run --all-files debug-statements
	@poetry run pre-commit run --all-files check-merge-conflict
	@poetry run pre-commit run --all-files name-tests-test
	@poetry run pre-commit run --all-files flake8
	@poetry run pre-commit run --all-files black
	@poetry run pre-commit run --all-files bandit
	@poetry run pre-commit run --all-files isort

#######
## Help
#######
help:
	@echo "#############################################################"
	@echo "##           MAKEFILE FOR ANALYSIS TEMPALTE MODEL          ##"
	@echo "#############################################################"
	@echo ""
	@echo "   Targets:   "
	@echo ""
	@echo "   - init: Initialize repository:"
	@echo "     - Install poetry"
	@echo "     - Install pre-commit"
	@echo "     - Check necessary paths and external dependencies"
	@echo "       Usage: % make init"
	@echo ""
	@echo "   - poetry-remove: Remove poetry environment."
	@echo "       Usage: % make poetry-remove"
	@echo ""
	@echo "   - pre-commit: Run pre-commits"
	@echo "       Usage: % make pre-commit"
	@echo ""
	@echo "   - help: Display this menu"
	@echo "       Usage: % make help"
	@echo ""
	@echo "   - default: init"
	@echo ""
	@echo "   Hidden targets:"
	@echo "   "
	@echo "   - poetry"
	@echo "   "
	@echo "#############################################################"
