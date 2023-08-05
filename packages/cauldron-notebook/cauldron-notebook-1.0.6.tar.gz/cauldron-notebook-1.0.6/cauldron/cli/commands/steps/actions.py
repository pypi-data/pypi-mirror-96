import os
import time
import typing

from cauldron.cli.commands.steps import renaming as step_support
from cauldron.environ import Response
from cauldron.session import naming
from cauldron.session import writing
from cauldron.session.projects import Project
from cauldron.session.writing import file_io


def index_from_location(
        response: Response,
        project: Project,
        location: typing.Union[str, int] = None,
        default: int = None
) -> int:
    """..."""
    if location is None:
        return default

    if isinstance(location, (int, float)):
        return int(location)

    if isinstance(location, str):
        location = location.strip('"')

        try:
            location = int(location)
            return None if location < 0 else location
        except Exception:
            index = project.index_of_step(location)
            return default if index is None else (index + 1)

    return default


def clean_steps(response: Response, project: Project) -> Response:
    """Removes and dirty settings for all steps"""
    for step in project.steps:
        if step.is_dirty() and step.last_modified:
            step.mark_dirty(False, force=True)

    return (
        response
        .update(project=project.kernel_serialize())
        .notify(
            kind='CLEANED',
            code='MARKED_CLEAN',
            message='All steps have been marked as up-to-date'
        )
        .console(whitespace=1)
        .response
    )


def echo_steps(response: Response, project: Project):
    """..."""
    if len(project.steps) < 1:
        response.update(
            steps=[]
        ).notify(
            kind='SUCCESS',
            code='ECHO_STEPS',
            message='No steps in project'
        ).console(
            """
            [NONE]: This project does not have any steps yet. To add a new
                step use the command:

                steps add [YOUR_STEP_NAME]

                and a new step will be created in this project.
            """,
            whitespace=1
        )
        return

    response.update(
        steps=[ps.kernel_serialize() for ps in project.steps]
    ).notify(
        kind='SUCCESS',
        code='ECHO_STEPS'
    ).console_header(
        'Project Steps',
        level=3
    ).console(
        '\n'.join(['* {}'.format(ps.definition.name) for ps in project.steps]),
        indent_by=2,
        whitespace_bottom=1
    )


def create_step(
        response: Response,
        project: Project,
        name: str,
        position: typing.Union[str, int],
        title: str = None
) -> Response:
    """..."""
    name = name.strip('"')
    title = title.strip('"') if title else title
    index = index_from_location(response, project, position)
    if index is None:
        index = len(project.steps)

    name_parts = naming.explode_filename(name, project.naming_scheme)

    if not project.naming_scheme and not name_parts['name']:
        name_parts['name'] = naming.find_default_filename(
            [s.definition.name for s in project.steps]
        )

    name_parts['index'] = index
    name = naming.assemble_filename(
        scheme=project.naming_scheme,
        **name_parts
    )

    res = step_support.synchronize_step_names(project, index)
    response.consume(res)
    if response.failed:
        return response

    step_renames = res.returned
    step_data = {'name': name}

    if title:
        step_data['title'] = title

    result = project.add_step(step_data, index=index)

    if not os.path.exists(result.source_path):
        contents = (
            'import cauldron as cd\n\n'
            if result.source_path.endswith('.py')
            else ''
        )

        with open(result.source_path, 'w+') as f:
            f.write(contents)

    project.save()
    project.write()

    project.select_step(result)
    index = project.steps.index(result)

    step_changes = [dict(
        name=result.definition.name,
        filename=result.filename,
        action='added',
        timestamp=time.time(),
        step=writing.step_writer.serialize(result)._asdict(),
        after=None if index < 1 else project.steps[index - 1].definition.name
    )]

    return response.update(
        project=project.kernel_serialize(),
        step_name=result.definition.name,
        step_path=result.source_path,
        step_changes=step_changes,
        step_renames=step_renames
    ).notify(
        kind='CREATED',
        code='STEP_CREATED',
        message='"{}" step has been created'.format(result.definition.name)
    ).console(whitespace=1).response


def modify_step(
        response: Response,
        project: Project,
        name: str,
        new_name: str = None,
        position: typing.Union[str, int] = None,
        title: str = None
) -> Response:
    """..."""
    new_name = new_name if new_name else name
    old_index = project.index_of_step(name)
    new_index = index_from_location(response, project, position, old_index)

    if new_index > old_index:
        # If the current position of the step occurs before the new position
        # of the step, the new index has to be shifted by one to account for
        # the fact that this step will no longer be in this position when it
        # get placed in the position within the project
        new_index -= 1

    old_step = project.remove_step(name)
    if not old_step:
        return response.fail(
            code='NO_SUCH_STEP',
            message='Unable to modify unknown step "{}"'.format(name)
        ).console(whitespace=1).response

    source_path = old_step.source_path
    if os.path.exists(source_path):
        temp_path = '{}.cauldron_moving'.format(source_path)
        file_io.move(file_io.FILE_COPY_ENTRY(
            source=source_path,
            destination=temp_path
        ))
    else:
        temp_path = None

    res = step_support.synchronize_step_names(project, new_index)
    response.consume(res)
    step_renames = res.returned

    new_name_parts = naming.explode_filename(new_name, project.naming_scheme)
    new_name_parts['index'] = new_index

    if not project.naming_scheme and not new_name_parts['name']:
        new_name_parts['name'] = naming.find_default_filename(
            [s.definition.name for s in project.steps]
        )

    new_name = naming.assemble_filename(
        scheme=project.naming_scheme,
        **new_name_parts
    )

    step_data = {'name': new_name}
    if title is None:
        old_title = old_step.definition.title
        if old_title and old_title != old_step.definition.name:
            step_data['title'] = old_step.definition.title
    else:
        step_data['title'] = title.strip('"')

    new_step = project.add_step(step_data, new_index)
    project.select_step(new_step)
    project.save()

    if not os.path.exists(new_step.source_path):
        if temp_path and os.path.exists(temp_path):
            file_io.move(file_io.FILE_COPY_ENTRY(
                source=temp_path,
                destination=new_step.source_path
            ))
        else:
            # Create an empty file if no existing source file for the
            # step exists.
            with open(new_step.source_path, 'w+') as f:
                f.write('')

    if new_index > 0:
        before_step = project.steps[new_index - 1].definition.name
    else:
        before_step = None

    step_renames[old_step.definition.name] = {
        'name': new_step.definition.name,
        'title': new_step.definition.title
    }

    step_changes = [dict(
        name=new_step.definition.name,
        filename=new_step.filename,
        action='modified',
        timestamp=time.time(),
        after=before_step
    )]

    response.update(
        project=project.kernel_serialize(),
        step_name=new_step.definition.name,
        step_changes=step_changes,
        step_renames=step_renames
    ).notify(
        kind='SUCCESS',
        code='STEP_MODIFIED',
        message='Step modifications complete'
    ).console(whitespace=1)

    project.write()

    return response


def toggle_muting(
        response: Response,
        project: Project,
        step_name: str,
        value: bool = None
) -> Response:
    """..."""
    index = project.index_of_step(step_name)
    if index is None:
        return response.fail(
            code='NO_SUCH_STEP',
            message='No step found with name: "{}"'.format(step_name)
        ).kernel(
            name=step_name
        ).console().response

    step = project.steps[index]
    if value is None:
        value = not bool(step.is_muted)

    step.is_muted = value

    return response.notify(
        kind='SUCCESS',
        code='STEP_MUTE_ENABLED' if step.is_muted else 'STEP_MUTE_DISABLED',
        message='Muting has been {}'.format(
            'enabled' if step.is_muted else 'disabled'
        )
    ).kernel(
        project=project.kernel_serialize()
    ).console().response
