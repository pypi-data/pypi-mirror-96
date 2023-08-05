import os

from cauldron import environ
from cauldron.environ import Response
from cauldron.session.projects import specio


def get_known_root_paths():
    """..."""
    aliases = environ.configs.fetch('folder_aliases', {})
    root_paths = list(set(
        [os.path.dirname(p) for p in environ.configs.fetch('recent_paths', [])]
        + [a['path'] for a in aliases.values()]
    ))

    index = 0
    while index < len(root_paths):
        path = root_paths[index]
        children_paths = [
            p
            for i, p in enumerate(root_paths)
            if index != i and p.startswith(path)
        ]
        for p in children_paths:
            root_paths.remove(p)

        index += 1

    return list(sorted(root_paths))


def echo_known_projects(response: Response) -> Response:
    """..."""
    environ.configs.load()
    project_specs = specio.ProjectSpecsReader()

    for root in get_known_root_paths():
        project_specs.add_recursive(root, root_path=root)

    spec_groups = project_specs.group_by('root_path')

    results = '\n\n'.join([
        '{}\n{}'.format(root, specio.to_display_list(specs))
        for root, specs in spec_groups.items()
    ])

    return (
        response
        .update(
            specs=project_specs.specs,
            spec_groups=spec_groups
        )
        .notify(
            kind='FOUND',
            code='FOUND',
            message='The following projects:\n\n{}'.format(results)
        )
        .console(whitespace=1)
    ).response
