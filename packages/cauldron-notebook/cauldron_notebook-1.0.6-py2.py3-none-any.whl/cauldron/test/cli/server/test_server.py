from unittest import mock

from cauldron import cli
from cauldron.cli.server import run as server_run
from cauldron.test import support
from cauldron.test.support.flask_scaffolds import FlaskResultsTest


class TestServer(FlaskResultsTest):
    """..."""

    def test_execute(self):
        """Should execute the command."""
        posted = self.post('/', {'command': 'open', 'args': ''})
        self.assertEqual(posted.flask.status_code, 200)

    def test_execute_invalid_command(self):
        """Should fail if command does not exist."""

        posted = self.post('/', {'command': 'fake-command', 'args': ''})
        self.assertEqual(posted.flask.status_code, 200)
        self.assert_has_error_code(posted.response, 'NO_SUCH_COMMAND')

    def test_execute_fail(self):
        """Should fail with improper arguments."""

        posted = self.post('/', {'command': 'open', 'args': [1234]})
        self.assertEqual(posted.flask.status_code, 200)
        self.assert_has_error_code(posted.response, 'INVALID_COMMAND')

    def test_ping(self):
        """Should successfully ping backend."""

        posted = self.post('/ping')
        self.assertEqual(posted.flask.status_code, 200)

    def test_status(self):
        """Should successfully check status of opened project."""

        opened = self.post('/', dict(
            command='open',
            args='@examples:hello_cauldron --forget'
        ))
        self.assertEqual(opened.flask.status_code, 200)
        self.assert_no_errors(opened.response)

        status = self.post('/status')
        self.assertEqual(status.flask.status_code, 200)
        self.assert_no_errors(status.response)

    def test_project(self):
        """

        :return:
        """

        opened = self.post('/', dict(
            command='open',
            args='@examples:hello_cauldron --forget'
        ))
        self.assert_no_errors(opened.response)

        project_status = self.post('/project')
        self.assert_no_errors(project_status.response)

    def test_run_status(self):
        """Should return unknown run status for invalid run uid."""

        run_status = self.get('/run-status/fake-uid')
        response = run_status.response
        self.assert_no_errors(response)
        self.assertEqual(response.data['run_status'], 'unknown')

    def test_abort_invalid(self):
        """Should cancel abort if nothing to abort."""

        aborted = self.get('/abort')
        self.assert_no_errors(aborted.response)

    def test_start_server_version(self):
        """Should return server version without starting the server."""

        with mock.patch('cauldron.cli.server.run.APPLICATION.run') as func:
            try:
                server_run.execute(version=True)
            except SystemExit:
                pass
            func.assert_not_called()

    def test_parse(self):
        """Should properly parse server args."""

        args = server_run.parse(['--port=9999', '--version', '--debug'])
        self.assertTrue(args.get('version'))
        self.assertTrue(args.get('debug'))
        self.assertEqual(args.get('port'), 9999)

    def test_abort_running(self):
        """Should abort long running step."""

        support.create_project(self, 'walter')
        support.add_step(self, contents=cli.reformat(
            """
            import time
            time.sleep(10)
            """
        ))

        running = self.post('/command-async', dict(
            command='run',
            args=''
        ))
        run_uid = running.response.data['run_uid']

        run_status = self.get('/run-status/{}'.format(run_uid))
        self.assert_no_errors(run_status.response)

        aborted = self.get('/abort')
        self.assert_no_errors(aborted.response)

    def test_long_running_print_buffering(self):
        support.create_project(self, 'walter2')
        support.add_step(self, contents=cli.reformat(
            """
            import time
            print('Printing to step print buffer...')
            for i in range(100):
                print(i)
                time.sleep(0.25)
            """
        ))

        running = self.post('/command-async', dict(
            command='run',
            args=''
        ))
        run_uid = running.response.data['run_uid']

        run_status = self.get('/run-status/{}'.format(run_uid))
        self.assert_no_errors(run_status.response)

        aborted = self.get('/abort')
        self.assert_no_errors(aborted.response)

    @mock.patch('cauldron.cli.server.run.APPLICATION.run')
    def test_start_server_basic(self, application_run: mock.MagicMock):
        """Should start server with specified settings."""
        kwargs = dict(
            port=9999,
            debug=True,
            host='TEST',
        )
        server_run.execute(basic=True, **kwargs)
        application_run.assert_called_once_with(**kwargs)

    @mock.patch('cauldron.cli.server.run.waitress.serve')
    def test_start_server(self, waitress_serve: mock.MagicMock):
        """Should start server with specified settings."""
        kwargs = dict(
            port=9999,
            host='TEST',
        )
        server_run.execute(**kwargs)
        assert waitress_serve.call_args[1] == kwargs
