import os
import time
import typing
from datetime import datetime

import cauldron
from cauldron import environ
from cauldron.environ import Response
from cauldron.runner import html_file
from cauldron.runner import markdown_file
from cauldron.runner import python_file
from cauldron.runner import redirection
from cauldron.session.projects import Project
from cauldron.session.projects import ProjectStep
from cauldron.session.projects import StopCondition

ERROR_STATUS = 'error'
OK_STATUS = 'ok'
SKIP_STATUS = 'skip'


def get_step(
        project: Project,
        step: typing.Union[ProjectStep, str]
) -> typing.Union[ProjectStep, None]:
    """

    :param project:
    :param step:
    :return:
    """
    if isinstance(step, ProjectStep):
        return step

    matches = [ps for ps in project.steps if ps.definition.name == step]
    return matches[0] if len(matches) > 0 else None


def has_extension(file_path: str, *args: str) -> bool:
    """
    Checks to see if the given file path ends with any of the specified file
    extensions. If a file extension does not begin with a '.' it will be added
    automatically

    :param file_path:
        The path on which the extensions will be tested for a match
    :param args:
        One or more extensions to test for a match with the file_path argument
    :return:
        Whether or not the file_path argument ended with one or more of the
        specified extensions
    """

    def add_dot(extension):
        return (
            extension
            if extension.startswith('.') else
            '.{}'.format(extension)
        )

    return any([
        file_path.endswith(add_dot(extension))
        for extension in args
    ])


def _execute_step(project: Project, step: ProjectStep) -> dict:
    if has_extension(step.source_path, 'md'):
        return markdown_file.run(project, step)

    if has_extension(step.source_path, 'html'):
        return html_file.run(project, step)

    # Mark the downstream steps as dirty because this one has run
    for s in project.steps[(step.index + 1):]:
        s.mark_dirty(True)

    if has_extension(step.source_path, 'py'):
        return python_file.run(project, step)

    return {'success': False}


def run_step(
        response: Response,
        project: Project,
        step: typing.Union[ProjectStep, str],
        force: bool = False
) -> bool:
    """

    :param response:
    :param project:
    :param step:
    :param force:
    :return:
    """
    step = get_step(project, step)
    if step is None:
        return False

    status = check_status(response, project, step, force)
    if status == ERROR_STATUS:
        return False

    step.error = None

    if status == SKIP_STATUS:
        return True

    os.chdir(os.path.dirname(step.source_path))
    project.current_step = step
    step.report.clear()
    step.dom = None
    step.is_visible = True
    step.is_running = True
    step.progress_message = None
    step.progress = 0
    step.sub_progress_message = None
    step.sub_progress = 0
    step.start_time = datetime.utcnow()
    step.end_time = None

    # Set the top-level display and cache values to the current project values
    # before running the step for availability within the step scripts
    cauldron.shared = cauldron.project.shared

    redirection.enable(step)

    try:
        result = _execute_step(project, step)
    except Exception as error:
        result = dict(
            success=False,
            message='{}'.format(error),
            html_message='<pre>{}</pre>'.format(error)
        )

    step.end_time = datetime.utcnow()
    os.chdir(environ.configs.fetch('directory', os.path.expanduser('~')))

    step.mark_dirty(not result['success'])
    step.error = result.get('html_message')
    step.progress = 0
    step.progress_message = None
    step.dumps(running_override=False)

    # Make sure this is called prior to printing response information to the
    # console or that will come along for the ride
    redirection.disable(step)

    step.project.stop_condition = result.get(
        'stop_condition',
        StopCondition(False, False)
    )

    if result['success']:
        environ.log('[{}]: Updated in {}'.format(
            step.definition.name,
            step.get_elapsed_timestamp()
        ))
    else:
        response.fail(
            message='Step execution error',
            code='EXECUTION_ERROR',
            project=project.kernel_serialize(),
            step_name=step.definition.name
        ).console_raw(result.get('message') or '')

    # Update the step timestamps so that the final dom changes
    # will be included in interactive display updates.
    step.report.update_last_modified()
    step.last_modified = time.time()

    # Wait until all of the step changes have been applied before
    # marking the step as no longer running to help prevent race
    # conditions with the dom output and running states when polled
    # by the UI or other external source in the main thread.
    step.is_running = False

    return result['success']


def _check_exists(path: str, retry_count: int = 3) -> bool:
    """
    Checks multiple times to see if a file exists, with a bit of
    a delay between calls to make sure that any race conditions
    will be avoided before making the call.
    """
    for index in range(retry_count):
        time.sleep(0.05 * min(4, index))
        if os.path.exists(path):
            return True

    return False


def check_status(
        response: Response,
        project: Project,
        step: ProjectStep,
        force: bool = False
) -> str:
    """..."""
    path = step.source_path

    if step.is_muted:
        environ.log('[{}]: Muted (skipped)'.format(step.definition.name))
        return SKIP_STATUS

    if not _check_exists(path):
        response.fail(
            code='MISSING_SOURCE_FILE',
            message='Source file not found "{}"'.format(path),
            id=step.definition.name,
            path=path
        ).console(
            '[{id}]: Not found "{path}"'.format(
                id=step.definition.name,
                path=path
            )
        )
        return ERROR_STATUS

    if not force and not step.is_dirty():
        environ.log('[{}]: Nothing to update'.format(step.definition.name))
        return SKIP_STATUS

    return OK_STATUS
