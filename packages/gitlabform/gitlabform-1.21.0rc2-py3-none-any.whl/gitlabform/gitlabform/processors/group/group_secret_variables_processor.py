import logging

from gitlabform.gitlab import GitLab
from gitlabform.gitlab.core import NotFoundException
from gitlabform.gitlabform.processors.abstract_processor import AbstractProcessor


class GroupSecretVariablesProcessor(AbstractProcessor):
    def __init__(self, gitlab: GitLab):
        super().__init__("group_secret_variables")
        self.gitlab = gitlab

    def _process_configuration(
        self, group: str, configuration: dict, do_apply: bool = True
    ):
        logging.debug(
            "Group secret variables BEFORE: %s",
            self.gitlab.get_group_secret_variables(group),
        )

        for secret_variable in sorted(configuration["group_secret_variables"]):

            if "delete" in configuration["group_secret_variables"][secret_variable]:
                key = configuration["group_secret_variables"][secret_variable]["key"]
                if configuration["group_secret_variables"][secret_variable]["delete"]:
                    logging.info(f"Deleting {secret_variable}: {key} in group {group}")
                    try:
                        self.gitlab.delete_group_secret_variable(group, key)
                    except:
                        logging.warning(
                            f"Could not delete variable {key} in group {group}"
                        )
                    continue

            logging.info("Setting group secret variable: %s", secret_variable)
            try:
                self.gitlab.put_group_secret_variable(
                    group, configuration["group_secret_variables"][secret_variable]
                )
            except NotFoundException:
                self.gitlab.post_group_secret_variable(
                    group, configuration["group_secret_variables"][secret_variable]
                )

        logging.debug(
            "Groups secret variables AFTER: %s",
            self.gitlab.get_group_secret_variables(group),
        )
