import logging
import os
import re
from pathlib import Path

from gitlabform.configuration import Configuration
from gitlabform.gitlab import GitLab
from gitlabform.gitlab.core import NotFoundException
from gitlabform.gitlabform.processors.abstract_processor import AbstractProcessor
from gitlabform.gitlabform.processors.util.branch_protector import BranchProtector


class FilesProcessor(AbstractProcessor):
    def __init__(self, gitlab: GitLab, config: Configuration, strict: bool):
        super().__init__("files")
        self.gitlab = gitlab
        self.config = config
        self.strict = strict
        self.branch_protector = BranchProtector(gitlab, strict)

    def _process_configuration(self, project_and_group: str, configuration: dict):
        for file in sorted(configuration["files"]):
            logging.debug("Processing file '%s'...", file)

            if configuration.get("files|" + file + "|skip"):
                logging.debug("Skipping file '%s'", file)
                continue

            all_branches = self.gitlab.get_branches(project_and_group)
            if configuration["files"][file]["branches"] == "all":
                branches = sorted(all_branches)
            elif configuration["files"][file]["branches"] == "protected":
                protected_branches = self.gitlab.get_protected_branches(
                    project_and_group
                )
                branches = sorted(protected_branches)
            else:
                branches = []
                for branch in configuration["files"][file]["branches"]:
                    if branch in all_branches:
                        branches.append(branch)
                    else:
                        logging.warning(
                            "! Branch '%s' not found, not processing file '%s' in it",
                            branch,
                            file,
                        )
                        if self.strict:
                            exit(3)

            for branch in branches:
                logging.info("Processing file '%s' in branch '%s'", file, branch)

                # unprotect protected branch temporarily for operations below
                if configuration.get("branches|" + branch + "|protected"):
                    logging.debug(
                        "> Temporarily unprotecting the branch for managing files in it..."
                    )
                    self.gitlab.unprotect_branch(project_and_group, branch)

                if configuration.get("files|" + file + "|delete"):
                    try:
                        self.gitlab.get_file(project_and_group, branch, file)
                        logging.debug("Deleting file '%s' in branch '%s'", file, branch)
                        self.gitlab.delete_file(
                            project_and_group,
                            branch,
                            file,
                            self.get_commit_message_for_file_change(
                                "delete",
                                configuration.get("files|" + file + "|skip_ci"),
                            ),
                        )
                    except NotFoundException:
                        logging.debug(
                            "Not deleting file '%s' in branch '%s' (already doesn't exist)",
                            file,
                            branch,
                        )
                else:
                    # change or create file

                    if configuration.get(
                        "files|" + file + "|content"
                    ) and configuration.get("files|" + file + "|file"):
                        logging.fatal(
                            "File '%s' in '%s' has both `content` and `file` set - "
                            "use only one of these keys.",
                            file,
                            project_and_group,
                        )
                        exit(4)
                    elif configuration.get("files|" + file + "|content"):
                        new_content = configuration.get("files|" + file + "|content")
                    else:
                        path_in_config = Path(
                            configuration.get("files|" + file + "|file")
                        )
                        if path_in_config.is_absolute():
                            path = path_in_config.read_text()
                        else:
                            # relative paths are relative to config file location
                            path = Path(
                                os.path.join(
                                    self.config.config_dir, str(path_in_config)
                                )
                            )
                        new_content = path.read_text()

                    if configuration.get("files|" + file + "|template", True):
                        new_content = self.get_file_content_as_template(
                            new_content,
                            project_and_group,
                            **configuration.get("files|" + file + "|jinja_env", dict()),
                        )

                    try:
                        current_content = self.gitlab.get_file(
                            project_and_group, branch, file
                        )
                        if current_content != new_content:
                            if configuration.get("files|" + file + "|overwrite"):
                                logging.debug(
                                    "Changing file '%s' in branch '%s'", file, branch
                                )
                                self.gitlab.set_file(
                                    project_and_group,
                                    branch,
                                    file,
                                    new_content,
                                    self.get_commit_message_for_file_change(
                                        "change",
                                        configuration.get("files|" + file + "|skip_ci"),
                                    ),
                                )
                            else:
                                logging.debug(
                                    "Not changing file '%s' in branch '%s' "
                                    "(overwrite flag not set)",
                                    file,
                                    branch,
                                )
                        else:
                            logging.debug(
                                "Not changing file '%s' in branch '%s' (it's content is already"
                                " as provided)",
                                file,
                                branch,
                            )
                    except NotFoundException:
                        logging.debug("Creating file '%s' in branch '%s'", file, branch)
                        self.gitlab.add_file(
                            project_and_group,
                            branch,
                            file,
                            new_content,
                            self.get_commit_message_for_file_change(
                                "add", configuration.get("files|" + file + "|skip_ci")
                            ),
                        )

                # protect branch back after above operations
                if configuration.get("branches|" + branch + "|protected"):
                    logging.debug("> Protecting the branch again.")
                    self.branch_protector.protect_branch(
                        project_and_group, configuration, branch
                    )
                if configuration.get("files|" + file + "|only_first_branch"):
                    logging.info(
                        "Skipping other branches for this file, as configured."
                    )
                    break

    def get_file_content_as_template(self, template, project_and_group, **kwargs):
        # Use jinja with variables project and group
        from jinja2 import Template

        return Template(template).render(
            project=self.get_project(project_and_group),
            group=self.get_group(project_and_group),
            **kwargs,
        )

    @staticmethod
    def get_commit_message_for_file_change(operation, skip_build):

        # add '[skip ci]' to commit message to skip CI job, as documented at
        # https://docs.gitlab.com/ee/ci/yaml/README.html#skipping-jobs
        skip_build_str = " [skip ci]" if skip_build else ""

        return "Automated %s made by gitlabform%s" % (operation, skip_build_str)

    @staticmethod
    def get_group(project_and_group):
        return re.match("(.*)/.*", project_and_group).group(1)

    @staticmethod
    def get_project(project_and_group):
        return re.match(".*/(.*)", project_and_group).group(1)
