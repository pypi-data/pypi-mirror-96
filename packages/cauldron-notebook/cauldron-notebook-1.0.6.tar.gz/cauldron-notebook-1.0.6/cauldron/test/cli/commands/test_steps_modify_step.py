import os
from unittest.mock import patch
from unittest.mock import MagicMock

import cauldron
from cauldron.cli.commands.steps import actions as step_actions
from cauldron.environ import systems
from cauldron.environ.response import Response
from cauldron.test import support
from cauldron.test.support import scaffolds


class TestStepsCreateStep(scaffolds.ResultsTest):
    """..."""

    def test_move_step_later(self):
        """Should move step later in the project."""
        support.create_project(self, 'edina')
        support.add_step(self, 'first')
        support.add_step(self, 'second')
        support.add_step(self, 'third')

        project = cauldron.project.get_internal_project()

        r = step_actions.modify_step(
            response=Response(),
            project=project,
            name=project.steps[1].filename,
            position='3'
        )

        self.assertTrue(r.success)
        self.assertEqual(
            ['S01.py', 'S02-second.py', 'S03-first.py', 'S04-third.py'],
            [s.filename for s in project.steps]
        )

    def test_fail_remove_old_step(self):
        """Should fail if unable to remove the old step."""

        support.create_project(self, 'bloomington')
        support.add_step(self, 'first')

        project = cauldron.project.get_internal_project()
        step = project.steps[0]

        with patch.object(project, 'remove_step') as remove_step:
            remove_step.return_value = None
            r = step_actions.modify_step(Response(), project, step.filename)

        self.assertFalse(r.success)
        self.assert_has_error_code(r, 'NO_SUCH_STEP')

    def test_no_existing_source_file(self):
        """Should succeed even if the step has no source file."""
        support.create_project(self, 'richfield')
        support.add_step(self, 'first')

        project = cauldron.project.get_internal_project()
        step = project.steps[0]

        self.assertTrue(
            systems.remove(step.source_path),
            'should have removed source file'
        )

        r = step_actions.modify_step(
            response=Response(),
            project=project,
            name=step.filename,
            new_name='solo',
            title='Only Step'
        )

        new_step = project.steps[0]
        self.assertTrue(r.success)
        self.assertTrue(os.path.exists(new_step.source_path))

    def test_nameless_step(self):
        """Should rename properly a nameless step."""

        support.create_project(self, 'columbia-heights')
        project = cauldron.project.get_internal_project()
        project.naming_scheme = None

        support.add_step(self)
        support.add_step(self)

        with patch('cauldron.session.naming.explode_filename') as func:
            func.return_value = dict(
                extension='py',
                index=1,
                name=''
            )
            r = step_actions.modify_step(
                response=Response(),
                project=project,
                name=project.steps[0].filename,
                new_name='',
                position=2
            )

        self.assertFalse(r.failed)

    def test_change_title(self):
        """Should change title."""

        support.create_project(self, 'blaine')
        support.add_step(self)

        project = cauldron.project.get_internal_project()

        r = step_actions.modify_step(
            response=Response(),
            project=project,
            name=project.steps[0].filename,
            title='a'
        )
        self.assertFalse(r.failed)
        self.assertEqual(project.steps[0].definition.title, 'a')

        r = step_actions.modify_step(
            response=Response(),
            project=project,
            name=project.steps[0].filename,
            title='b'
        )
        self.assertFalse(r.failed)
        self.assertEqual(project.steps[0].definition.title, 'b')

        r = step_actions.modify_step(
            response=Response(),
            project=project,
            name=project.steps[0].filename,
            new_name='first'
        )
        self.assertFalse(r.failed)
        self.assertEqual(project.steps[0].definition.title, 'b')
