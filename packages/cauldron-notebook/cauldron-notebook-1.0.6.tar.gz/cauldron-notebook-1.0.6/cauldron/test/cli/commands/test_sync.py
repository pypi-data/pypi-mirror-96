import os
import time

import cauldron
from cauldron import environ
from cauldron.environ.response import Response
from cauldron.test import support
from cauldron.test.support import scaffolds


class TestSync(scaffolds.ResultsTest):
    """..."""

    def test_sync_project(self):
        """Should synchronize local files to remote location."""
        support.run_remote_command('open @examples:hello_cauldron --forget')
        response = support.run_remote_command('sync')
        self.assertTrue(response.success)

        project = cauldron.project.get_internal_project()
        remote_files = sorted(os.listdir(project.remote_source_directory))
        local_files = sorted(os.listdir(project.source_directory))

        self.assertEqual(remote_files, local_files)

    def test_sync_project_again(self):
        """Should synchronize files only when needed."""
        support.run_remote_command('open @examples:hello_cauldron --forget')
        response = support.run_remote_command('sync')
        self.assertTrue(response.success)

        self.assertGreater(response.data['synchronized_count'], 0)

        # Create a mock remote connection that has a future timestamp
        # so that no files will be synchronized.
        remote_connection = environ.RemoteConnection(
            url='fake-run-remote.command',
            active=True
        )
        remote_connection._sync_timestamp = time.time() + 10

        response = support.run_remote_command(
            'sync',
            remote_connection=remote_connection,
        )
        self.assertEqual(response.data['synchronized_count'], 0)

    def test_sync_no_connection(self):
        """Should fail if no remote connection is active."""
        response = support.run_command('sync')
        self.assert_has_error_code(response, 'NO_REMOTE_CONNECTION')

    def test_failed_status(self):
        """Should fail if unable to get remote sync status."""
        def mock_send_request(*args, **kwargs):
            return Response().fail(code='FAKE-ERROR').response

        response = support.run_remote_command(
            command='sync',
            mock_send_request=mock_send_request
        )
        self.assertTrue(response.failed)
        self.assert_has_error_code(response, 'FAKE-ERROR')

    def test_no_such_project(self):
        """Should fail if unable to get remote sync status."""
        def mock_send_request(*args, **kwargs):
            return Response().update(
                remote_source_directory=directory
            ).response

        directory = os.path.dirname(os.path.realpath(__file__))
        response = support.run_remote_command(
            command='sync',
            mock_send_request=mock_send_request
        )
        self.assert_has_error_code(response, 'NO_PROJECT')
