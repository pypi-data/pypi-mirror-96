import os

import cauldron
from cauldron import environ
from cauldron import runner
from cauldron import session
from cauldron.environ import Response
from cauldron.session import projects


def project_exists(response: 'environ.Response', path: str) -> bool:
    """
    Determines whether or not a project exists at the specified path

    :param response:
    :param path:
    :return:
    """

    if os.path.exists(path):
        return True

    response.fail(
        code='PROJECT_NOT_FOUND',
        message='The project path does not exist',
        path=path
    ).console(
        """
        [ERROR]: Unable to open project. The specified path does not exist:

          {path}
        """.format(path=path)
    )
    return False


def load_project(response, path):
    try:
        runner.initialize(path)
        return True
    except FileNotFoundError:
        response.fail(
            code='PROJECT_NOT_FOUND',
            message='Project not found'
        ).console(whitespace=1)
    except Exception as err:
        response.fail(
            code='PROJECT_INIT_FAILURE',
            message='Unable to load the project',
            error=err
        ).console(whitespace=1)

    return False


def update_recent_paths(response: 'environ.Response', path: str):
    """..."""
    try:
        recent_paths = environ.configs.fetch('recent_paths', [])

        if path in recent_paths:
            recent_paths.remove(path)

        recent_paths.insert(0, path)
        environ.configs.put(recent_paths=recent_paths[:40], persists=True)
        environ.configs.save()
    except Exception as error:  # pragma: no cover
        response.warn(
            code='FAILED_RECENT_UPDATE',
            message='Unable to update recently opened projects',
            error=str(error)
        ).console(whitespace=1)


def initialize_results(response: environ.Response, project):
    if not project.results_path:
        return True

    try:
        session.initialize_results_path(project.results_path)
        return True
    except Exception as err:
        response.fail(
            code='RESULTS_INIT_FAILED',
            message='Unable to updated project results data',
            error=err
        )

    return False


def write_results(response: environ.Response, project: 'projects.Project'):
    try:
        path = project.output_path
        if not path or not os.path.exists(path):
            project.write()
        return True
    except Exception as error:
        import traceback
        traceback.print_exc()
        response.fail(
            code='WRITE_FAILED',
            message='Unable to write project output data',
            error=error
        )
        return False


def open_project(
        path: str,
        forget: bool = False,
        results_path: str = None
) -> Response:
    """..."""
    response = Response()

    try:
        # Try to close any open projects before opening a new one.
        runner.close()
    except Exception:  # pragma: no cover
        pass

    path = environ.paths.clean(path)

    if not project_exists(response, path):
        return response.fail(
            code='PROJECT_NOT_FOUND',
            message='No project found at: "{}"'.format(path)
        ).console(whitespace=1).response

    if not load_project(response, path):
        return response.fail(
            code='PROJECT_NOT_LOADED',
            message='Unable to load project data'
        ).console(whitespace=1).response

    if not forget:  # pragma: no cover
        update_recent_paths(response, path)

    project = cauldron.project.get_internal_project()
    if project.steps:
        # Always select the first step when a project is opened.
        project.select_step(0)

    if results_path:
        project.results_path = results_path

    # Set the top-level display and cache values to the current project values
    # before running the step for availability within the step scripts
    cauldron.shared = cauldron.project.shared

    if not initialize_results(response, project):
        return response.fail(
            code='PROJECT_INIT_FAILURE',
            message='Unable to initialize loaded project'
        ).console(whitespace=1).response

    if not write_results(response, project):
        return response.fail(
            code='PROJECT_WRITE_FAILURE',
            message='Unable to write project notebook data'
        ).console(whitespace=1).response

    # Should no longer be needed because the source directory is included
    # in the library directories as of v0.4.7
    # runner.add_library_path(project.source_directory)
    runner.reload_libraries(project.library_directories)

    return response.update(
        project=project.kernel_serialize()
    ).notify(
        kind='SUCCESS',
        code='PROJECT_OPENED',
        message='Opened project: {}'.format(path)
    ).console_header(
        project.title,
        level=2
    ).console(
        """
        PATH: {path}
         URL: {url}
        """.format(path=path, url=project.baked_url),
        whitespace=1
    ).response
