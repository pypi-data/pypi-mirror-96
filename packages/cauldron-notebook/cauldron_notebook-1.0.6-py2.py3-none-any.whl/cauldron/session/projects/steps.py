import hashlib
import os
import time
import typing
from datetime import datetime

from cauldron import render
from cauldron import templating
from cauldron.session import definitions
from cauldron.session import naming
from cauldron.session import projects  # noqa
from cauldron.session.report import Report


class ProjectStep(object):
    """
    A computational step within the project, which contains data and
    functionality related specifically to that step as well as a reference to
    the project itself.
    """

    _reference_index = 0

    def __init__(
            self,
            project: 'projects.Project' = None,
            definition: definitions.FileDefinition = None
    ):
        """

        :param project:
        :param definition:
        """
        self.__class__._reference_index += 1
        self._reference_id = '{}'.format(self.__class__._reference_index)

        self.definition = definition if definition is not None else dict()
        self.project = project
        self.report = Report(self)

        self.last_modified = 0  # type: typing.Optional[float]
        self.code = None
        self.is_visible = True
        self._is_running = False
        self.is_selected = False
        self._is_dirty = True

        # Whether or not the step has ever been executed. Setting the
        # step.is_running property to True will cause this to become
        # True and will stay true for the remainder of the step's
        # lifetime.
        self._has_run = False

        self.error = None  # type: typing.Optional[str]
        self.is_muted = False
        self.dom = None  # type: typing.Optional[str]
        self.progress_message = None
        self.sub_progress_message = None
        self.progress = 0
        self.sub_progress = 0
        self.test_locals = None  # type: typing.Optional[dict]
        self.start_time = None  # type: typing.Optional[datetime]
        self.end_time = None  # type: typing.Optional[datetime]

    @property
    def is_running(self) -> bool:
        """Whether or not the step code is currently being executed."""
        return self._is_running

    @is_running.setter
    def is_running(self, value: bool):
        self._has_run = self._has_run or bool(value)
        self._is_running = bool(value)

    @property
    def remote_source_path(self) -> typing.Optional[str]:
        """
        Path to the step source file on the remote system or None
        if no remote connection exists.
        """
        unavailable = (
            not self.project
            or not self.project.remote_source_directory
            or not self.report
        )
        if unavailable:
            return None
        return os.path.join(
            self.project.remote_source_directory,
            self.filename
        )

    @property
    def name(self):
        return self.definition.name

    @property
    def reference_id(self):
        return self._reference_id

    @property
    def uuid(self):
        """Unique identifier based on the path of the step"""
        return hashlib.sha1(self.source_path.encode()).hexdigest()

    @property
    def filename(self) -> str:
        """Name of the step file"""
        return self.definition.slug

    @property
    def web_includes(self) -> list:
        if not self.project:
            return []

        folder = self.definition.get('folder', '')
        return [
            os.path.join(folder, fn.replace('/', os.sep))
            for fn in self.definition.get('web_includes', [])
        ]

    @property
    def index(self) -> int:
        if not self.project:
            return -1
        return self.project.steps.index(self)

    @property
    def source_path(self) -> typing.Union[None, str]:
        if not self.project or not self.report:
            return None
        return os.path.join(self.project.source_directory, self.filename)

    @property
    def elapsed_time(self) -> float:
        """
        The number of seconds that has elapsed since the step started running
        if the step is still running. Or, if the step has already finished
        running, the amount of time that elapsed during the last execution of
        the step.
        """
        current_time = datetime.utcnow()
        start = self.start_time or current_time
        end = self.end_time or current_time
        return (end - start).total_seconds()

    @property
    def file_last_modified(self) -> int:
        """When the source file was modified, or 0 if it does not exist."""
        return (
            os.path.getmtime(self.source_path)
            if self.source_path and os.path.exists(self.source_path)
            else 0
        )

    def get_elapsed_timestamp(self) -> str:
        """
        A human-readable version of the elapsed time for the last execution
        of the step. The value is derived from the `ProjectStep.elapsed_time`
        property.
        """
        t = self.elapsed_time
        minutes = int(t / 60)
        seconds = int(t - (60 * minutes))
        millis = int(100 * (t - int(t)))
        return '{:>02d}:{:>02d}.{:<02d}'.format(minutes, seconds, millis)

    def kernel_serialize(self):
        """..."""
        status = self.status()
        out = dict(
            slug=self.definition.slug,
            index=self.index,
            source_path=self.source_path,
            remote_source_path=self.remote_source_path,
            status=status,
            exploded_name=naming.explode_filename(
                self.definition.name,
                self.project.naming_scheme
            )
        )

        # Eventually this should be removed. It exists for legacy reasons.
        out.update(status)

        return out

    def status(self):
        """..."""
        is_dirty = self.is_dirty()
        return dict(
            uuid=self.uuid,
            reference_id=self.reference_id,
            name=self.definition.name,
            muted=self.is_muted,
            selected=self.is_selected,
            last_modified=self.last_modified,
            last_display_update=self.report.last_update_time,
            file_modified=self.file_last_modified,
            dirty=is_dirty,
            is_dirty=is_dirty,
            running=self.is_running,
            run=self._has_run,
            error=self.error is not None
        )

    def is_dirty(self):
        """
        Whether or not the step is in a state of needing to be rerun
        because a modification to the step or its source file has invalidated
        its last run state.
        """
        return (
            self._is_dirty
            or self.last_modified < 1
            or self.file_last_modified >= self.last_modified
        )

    def mark_dirty(self, value: bool, force: bool = False):
        """
        Steps that are forced to be dirty will be updated in the UI
        via step change dom responses. Not forcing will only update
        the settings dirty flag.
        """
        self._is_dirty = bool(value)
        time_adjust = 0 if value else time.time()
        self.last_modified = time_adjust if force else self.last_modified

    def get_dom(self) -> str:
        """ Retrieves the current value of the DOM for the step."""
        if self.is_running:
            return self.dumps()

        if self.dom is not None:
            return self.dom

        dom = self.dumps()
        self.dom = dom
        return dom

    def clear_dom(self) -> str:
        """
        Empties the current dom of all display body elements
        and returns the empty dom.
        """
        self.report.body = []
        self.dom = self.dumps()
        self.mark_dirty(True)
        return self.dom

    def dumps(self, running_override: bool = None) -> str:
        """Writes the step information to an HTML-formatted string"""
        is_running = (
            self.is_running
            if running_override is None
            else running_override
        )

        code_file_path = os.path.join(
            self.project.source_directory,
            self.filename
        )
        code = dict(
            filename=self.filename,
            path=code_file_path,
            code=render.code_file(code_file_path)
        )

        if not is_running:
            # If no longer running, make sure to flush the stdout buffer so
            # any print statements at the end of the step get included in
            # the body
            self.report.flush_stdout()

        # Create a copy of the body for dumping
        body = self.report.body[:]

        if is_running:
            # If still running add a temporary copy of anything not flushed
            # from the stdout buffer to the copy of the body for display. Do
            # not flush the buffer though until the step is done running or
            # it gets flushed by another display call.
            body.append(self.report.read_stdout())

        body = ''.join(body)

        has_body = len(body) > 0 and (
            body.find('<div') != -1 or
            body.find('<span') != -1 or
            body.find('<p') != -1 or
            body.find('<pre') != -1 or
            body.find('<h') != -1 or
            body.find('<ol') != -1 or
            body.find('<ul') != -1 or
            body.find('<li') != -1
        )

        std_err = (
            self.report.read_stderr()
            if is_running else
            self.report.flush_stderr()
        ).strip('\n').rstrip()

        # The step will be visible in the display if any of the following
        # conditions are true.
        is_visible = self.is_visible or is_running or self.error

        dom = templating.render_template(
            'step-body.html',
            last_display_update=self.report.last_update_time,
            elapsed_time=self.get_elapsed_timestamp(),
            code=code,
            body=body,
            has_body=has_body,
            id=self.definition.name,
            title=self.report.title,
            subtitle=self.report.subtitle,
            summary=self.report.summary,
            error=self.error,
            index=self.index,
            is_running=is_running,
            is_visible=is_visible,
            progress_message=self.progress_message,
            progress=int(round(max(0, min(100, 100 * self.progress)))),
            sub_progress_message=self.sub_progress_message,
            sub_progress=int(round(max(0, min(100, 100 * self.sub_progress)))),
            std_err=std_err
        )

        if not is_running:
            self.dom = dom
            self.last_modified = time.time()
        return dom
