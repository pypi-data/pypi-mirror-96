import os
import time

import cauldron as cd
from cauldron import cli
from cauldron.test import support
from cauldron.test.support import scaffolds


class TestRunner(scaffolds.ResultsTest):
    """..."""

    def test_syntax_error(self):
        """Should render a syntax error."""
        support.create_project(self, 'seattle')
        support.add_step(self, contents='// Not Python')
        response = support.run_command('run -f')
        self.assertTrue(response.failed, 'should have failed')

        project = cd.project.get_internal_project()
        step = project.steps[1]

        self.assertTrue(step.dom.find('cd-CodeError') > 0)
        self.assertTrue(step.dom.find('SyntaxError') > 0)

    def test_exception(self):
        """Should fail on the third step."""
        support.create_project(self, 'brad')
        support.add_step(
            self, 'brad_one.py', cli.reformat(
                """
                import cauldron as cd

                a = dict(
                    one=1,
                    two=['1', '2'],
                    three={'a': True, 'b': False, 'c': True}
                )

                cd.display.inspect(a)
                cd.shared.a = a
                cd.display.workspace()

                """
            )
        )
        support.add_step(self, 'brad_two.py', "1 + 's'")

        r = support.run_command('run ..')
        self.assertFalse(r.failed, 'should not have failed')

        r = support.run_command('run .')
        self.assertTrue(r.failed, 'should have failed')

    def test_library(self):
        """Should refresh the local project library with the updated value."""
        support.create_project(self, 'jack')
        project = cd.project.get_internal_project()

        lib_directory = os.path.join(project.source_directory, 'libs', '_jack')
        os.makedirs(lib_directory)

        path = os.path.join(lib_directory, '__init__.py')
        with open(path, 'w') as fp:
            fp.write('TEST_VALUE = 1\n')

        # TODO: Fix these forced pauses
        time.sleep(1)

        self.assertTrue(os.path.exists(path), 'Library does not exist')

        support.add_step(self, contents='\n'.join([
            'import cauldron as cd',
            'import _jack',
            'cd.shared.TEST_VALUE = _jack.TEST_VALUE'
        ]))

        response = support.run_command('run --force')
        self.assertFalse(response.failed, support.Message(
            'RUN-STEP',
            'should be able to run the step that imports the local library',
            'without failing',
            response=response
        ))
        self.assertEqual(cd.shared.TEST_VALUE, 1)

        # Pause execution to deal with race conditions in modified
        # times that cause this test to fail on certain systems
        time.sleep(1)

        with open(os.path.join(lib_directory, '__init__.py'), 'w') as fp:
            fp.write('TEST_VALUE = 2\n')

        # TODO: Fix these forced pauses
        time.sleep(1)

        support.run_command('run --force')
        self.assertEqual(cd.shared.TEST_VALUE, 2)
