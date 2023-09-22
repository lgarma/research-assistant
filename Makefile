########################################################################################
###################### MAKEFILE FOR research-research-assistant MODEL #######################
########################################################################################

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
	@[ -f ./quality.yml ] && mkdir .github && mkdir .github/workflows && mv quality.yml .github/workflows/ || true
	@echo "Running shell..."
	@poetry shell
	@echo ""
else
init:
	@read -p "Your profile (.bashrc, .zshrc, .bash_profile, etc)?: " PROFILE; \
	echo "export SHELL_PROFILE_PATH='${HOME}/$$PROFILE'" >> ~/$$PROFILE; \
	echo "\033[0;33mSource your profile\033[0m";
endif

##########
## Aliases
##########
aliases:
	@echo "alias research-assistant='make -C ${PROJECT_PATH}'" >> ${SHELL_PROFILE}

#################
## Change version
#################
change-version:
ifdef version
	@echo ""
	@old_version=$(shell cat pyproject.toml | awk '/^version =/{print $$3}' | xargs); \
	echo "Changing from version v$$old_version to v${version}..."; \
	sed "s/tree\/v$$old_version/tree\/v${version}/g" mkdocs.yml > temp && mv temp mkdocs.yml; \
	sed "s/@v$$old_version/@v${version}/g" mkdocs.yml > temp && mv temp mkdocs.yml; \
	sed "s/\/v$$old_version/\/v${version}/g" README.md > temp && mv temp README.md
	@cat pyproject.toml | awk '/^version =/{gsub($$3,"\"${version}\"")};{print}' > temp && mv temp pyproject.toml
	@cat docs/design_doc.md | awk '/- Versión:/{gsub($$3,"${version}")};{print}' > temp && mv temp docs/design_doc.md
	@cat researchResearch-assistant/__init__.py | awk '/^__version__ =/{gsub($$3,"\"${version}\"")};{print}' > temp && mv temp researchResearch-assistant/__init__.py
	@cat tests/test_researchResearch-assistant.py | awk '/__version__ ==/{gsub($$4,"\"${version}\"")};{print}' > temp && mv temp tests/test_researchResearch-assistant.py
	@echo ""
	@echo "Deploying documentation for version ${version}"
	@poetry run mike deploy v${version} -b gh-pages --push
	@poetry run mike set-default v${version}
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

################
## Documentation
################
doc-deploy:
ifdef version
	@echo ""
	@echo "Deploying documentation for version ${version}"
	@poetry run mike deploy v${version} -b gh-pages --push
	@poetry run mike set-default v${version}
	@echo ""
else
	@echo ""
	@version=$(shell cat pyproject.toml | awk '/^version =/{print $$3}' | xargs); \
	echo "Deploying documentation for version $$version"; \
	poetry run mike deploy v$$version -b gh-pages --push; \
	poetry run mike set-default v$$version
	@echo ""
endif

doc-serve:
	@echo ""
	@poetry run mkdocs serve
	@echo ""

###################
## Jupyter Notebook
###################
jupyter:
	@echo ""
	@poetry run jupyter-lab
	@echo ""

######################
## Jupyter to Markdown
######################
jup2md:
ifdef jupfile
	@poetry run jupyter nbconvert ${jupfile} --to markdown
else
	@poetry run jupyter nbconvert ${PROJECT_PATH}/notebooks/examples.ipynb --to markdown
endif

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
	@echo "Installing kernel..."
	@poetry run python -m ipykernel install --user --name researchResearch-assistant
	@echo "\033[0;32mresearchResearch-assistant kernel installed.\033[0m"
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

pre-commit-all:
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

##################
## Memory-profiler
##################
profile:
ifdef version
	@echo ""
	@echo "Running memory-profiler for version v${version}..."
	@poetry run python ${PROJECT_PATH}/profiling/researchResearch-assistant_profiling.py > docs/img/memory_profiler_v${version}.log
	@echo "Profiling log saved in docs/img/memory_profiler_v${version}.log"
	@mv plot.png docs/img/memory_profiler_plot_v${version}.png
	@echo "Memory and CPU usage reported in docs/img/memory_profiler_plot_v${version}.png"
	@echo ""
else
	@echo ""
	echo "Running memory-profiler..."; \
	poetry run python ${PROJECT_PATH}/profiling/researchResearch-assistant_profiling.py > profiling/memory_profiler.log; \
	echo "Profiling log saved in profiling/memory_profiler.log"; \
	mv plot.png profiling/memory_profiler_plot.png; \
	echo "Memory and CPU usage reported in profiling/memory_profiler_plot.png"
	@echo ""
endif

############
## Streamlit
############
stream:
ifdef ip
	@cd ${PROJECT_PATH}/app;\
	poetry run streamlit run 01_✨_Research_Assistant.py --server.port=8601 --server.enableCORS=false --server.enableXsrfProtection=false --theme.base=dark --theme.primaryColor=#9333ea --theme.font=monospace --theme.textColor=#f1f5f9 --server.fileWatcherType=none --browser.serverAddress=${ip}
else
	@cd ${PROJECT_PATH}/app;\
	poetry run streamlit run 01_✨_Research_Assistant.py --server.port=8601 --server.enableCORS=false --server.enableXsrfProtection=false --theme.base=dark --theme.primaryColor=#9333ea --theme.font=monospace --theme.textColor=#f1f5f9 --server.fileWatcherType=none
endif

#########
## Pytest
#########
test:
	@echo ""
	@pytest ${PROJECT_PATH}/tests/
	@echo ""

#######
## Help
#######
help:
	@echo "#############################################################"
	@echo "##           MAKEFILE FOR research-research-assistant                 ##"
	@echo "#############################################################"
	@echo ""
	@echo "   Targets:   "
	@echo ""
	@echo "   - init: Initialize repository:"
	@echo "     - Install poetry"
	@echo "     - Install pre-commit"
	@echo "     - Install ipykernel"
	@echo "     - Check necessary paths and external dependencies"
	@echo "       Usage: % make init"
	@echo ""
	@echo "   - aliases: Create alias"
	@echo "       Usage: % make aliases"
	@echo ""
	@echo "   - change-version: Change version"
	@echo "       Usage: % make change-version version=<version_number>"
	@echo ""
	@echo "   - doc: Deploy documentation"
	@echo "       Usage: % make doc-deploy → GitHub Page"
	@echo "       Usage: % make doc-deploy version=<version_number> → GitHub Page"
	@echo "       Usage: % make doc-serve  → Local"
	@echo ""
	@echo "   - jup2md: Convert Jupyter notebook to Markdown"
	@echo "       Usage: % make jup2md → Convert notebooks/examples.md"
	@echo "       Usage: % make jup2md jupfile=</path/to/jupfile>"
	@echo "                            ↳ Convert notebooks/examples.md"
	@echo ""
	@echo "   - poetry-remove: Remove poetry environment."
	@echo "       Usage: % make poetry-remove"
	@echo ""
	@echo "   - pre-commit: Run pre-commits"
	@echo "       Usage: % make pre-commit"
	@echo ""
	@echo "   - profile: Run memory-profiler"
	@echo "       Usage: % make profile"
	@echo "       Usage: % make profile version=<version_number>"
	@echo ""
	@echo "   - test: Run pytests"
	@echo "       Usage: % make test"
	@echo ""
	@echo "   - stream: Run streamlit app"
	@echo "       Usage: % make stream"
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
