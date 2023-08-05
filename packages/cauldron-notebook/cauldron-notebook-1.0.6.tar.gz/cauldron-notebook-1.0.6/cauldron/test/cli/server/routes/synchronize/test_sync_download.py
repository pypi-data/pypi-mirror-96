import os
from unittest.mock import patch

import cauldron
from cauldron.test import support
from cauldron.test.support.flask_scaffolds import FlaskResultsTest


class TestSyncDownload(FlaskResultsTest):
    """..."""

    def test_no_project(self):
        """Should return a 204 status when no project is open."""
        downloaded = self.get('/download/fake')
        self.assertEqual(downloaded.flask.status_code, 204)

    def test_no_such_file(self):
        """Should return a 204 status when no such file exists."""

        support.create_project(self, 'downloader')

        downloaded = self.get('/download/fake.filename.not_real')
        self.assertEqual(downloaded.flask.status_code, 204)

    def test_valid(self):
        """Should successfully download file."""
        support.create_project(self, 'downloader')
        project = cauldron.project.get_internal_project()

        support.run_remote_command(
            'open "{}" --forget'.format(project.source_directory)
        )

        my_path = os.path.realpath(__file__)
        with patch('os.path.realpath', return_value=my_path) as func:
            downloaded = self.get('/download/fake.filename.not_real')
            self.assertGreater(func.call_count, 0)

        self.assertEqual(downloaded.flask.status_code, 200)

