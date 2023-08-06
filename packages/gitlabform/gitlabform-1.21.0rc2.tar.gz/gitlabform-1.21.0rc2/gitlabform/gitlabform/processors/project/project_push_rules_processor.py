import logging

from gitlabform.gitlab import GitLab
from gitlabform.gitlabform.processors.abstract_processor import AbstractProcessor
from gitlabform.gitlabform.processors.util.difference_logger import DifferenceLogger


class ProjectPushRulesProcessor(AbstractProcessor):
    def __init__(self, gitlab: GitLab):
        super().__init__("project_push_rules")
        self.gitlab = gitlab

    def _process_configuration(self, project_and_group: str, configuration: dict):
        push_rules = configuration["project_push_rules"]
        old_project_push_rules = self.gitlab.get_project_push_rules(project_and_group)
        logging.debug("Project push rules settings BEFORE: %s", old_project_push_rules)
        if old_project_push_rules:
            logging.info("Updating project push rules: %s", push_rules)
            self.gitlab.put_project_push_rules(project_and_group, push_rules)
        else:
            logging.info("Creating project push rules: %s", push_rules)
            self.gitlab.post_project_push_rules(project_and_group, push_rules)
        logging.debug(
            "Project push rules AFTER: %s",
            self.gitlab.get_project_push_rules(project_and_group),
        )

    def _log_changes(self, project_and_group: str, push_rules):
        current_push_rules = self.gitlab.get_project_push_rules(project_and_group)
        DifferenceLogger.log_diff(
            "Project %s push rules changes" % project_and_group,
            current_push_rules,
            push_rules,
        )
