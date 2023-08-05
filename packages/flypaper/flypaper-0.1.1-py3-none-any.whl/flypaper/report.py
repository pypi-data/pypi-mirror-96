"""
This module implements all Flypaper methods related to generating reports and publishing them to
Bugout knowledge bases.
"""
from dataclasses import dataclass, field
import textwrap
import traceback
from typing import List, Optional

from bugout.app import Bugout

from .consent import FlypaperConsent
from .system_information import (
    SystemInformation,
    generate as generate_system_information,
)


@dataclass
class Report:
    title: str
    content: str
    tags: List[str] = field(default_factory=list)


class Reporter:
    def __init__(
        self,
        name: str,
        consent: FlypaperConsent,
        client_id: Optional[str] = None,
        system_information: Optional[SystemInformation] = None,
        bugout_token: Optional[str] = None,
        bugout_journal_id: Optional[str] = None,
        timeout_seconds: int = 10,
    ):
        self.name = name
        self.consent = consent
        self.client_id = client_id
        if system_information is None:
            system_information = generate_system_information()
        self.system_information = system_information
        self.bugout = Bugout()
        self.bugout_token = bugout_token
        self.bugout_journal_id = bugout_journal_id
        self.timeout_seconds = timeout_seconds

    def system_tags(self) -> List[str]:
        tags = [
            "flypaper",
            "source:{}".format(self.name),
            "os:{}".format(self.system_information.os),
            "arch:{}".format(self.system_information.machine),
            "python:{}".format(self.system_information.python_version_major),
            "python:{}.{}".format(
                self.system_information.python_version_major,
                self.system_information.python_version_minor,
            ),
            "python:{}".format(self.system_information.python_version),
        ]
        if self.client_id is not None:
            tags.append("client:{}".format(self.client_id))

        return tags

    def publish(self, report: Report) -> None:
        if not self.consent.check():
            return
        if self.bugout_token is None or self.bugout_journal_id is None:
            return

        try:
            report.tags = list(set(report.tags))
            self.bugout.create_entry(
                self.bugout_token,
                self.bugout_journal_id,
                title=report.title,
                content=report.content,
                tags=report.tags,
                timeout=self.timeout_seconds,
            )
        except:
            pass

    def system_report(
        self, tags: Optional[List[str]] = None, publish: bool = True
    ) -> Report:
        title = "{}: System information".format(self.name)
        content = textwrap.dedent(
            """
            ### OS
            ```
            {os}
            ```

            Release: `{os_release}`

            ### Processor
            ```
            {machine}
            ```

            ### Python
            ```
            {python_version}
            ```
        """.format(
                os=self.system_information.os,
                os_release=self.system_information.os_release,
                machine=self.system_information.machine,
                python_version=self.system_information.python_version,
            )
        )
        report = Report(title=title, content=content, tags=self.system_tags())
        if tags is not None:
            report.tags.extend(tags)

        if publish:
            self.publish(report)

        return report

    def error_report(
        self, error: Exception, tags: Optional[List[str]] = None, publish: bool = True
    ) -> Report:
        title = "{} - {}".format(self.name, type(error).__name__)
        system_report = self.system_report(publish=False)
        error_content = textwrap.dedent(
            """
            ### Exception summary
            ```
            {error_summary}
            ```

            ### Traceback
            ```
            {error_traceback}
            ```
        """.format(
                error_summary=repr(error),
                error_traceback="".join(
                    traceback.format_exception(
                        etype=type(error),
                        value=error,
                        tb=error.__traceback__,
                    )
                ),
            )
        )
        content = "\n\n".join(
            [
                "## Error information",
                error_content,
                "- - -",
                "## System information",
                system_report.content,
            ]
        )
        if tags is None:
            tags = []
        tags.extend(system_report.tags)

        report = Report(title=title, content=content, tags=tags)

        if publish:
            self.publish(report)

        return report
