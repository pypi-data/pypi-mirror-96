import os
import site

from unittest import mock
from unittest.mock import patch
from contextlib import ExitStack

from cauldron.environ import systems
from cauldron.test.support import scaffolds


class TestSystems(scaffolds.ResultsTest):
    """..."""

    def test_end_success(self):
        """Should end quietly with a success exit code."""

        with patch('sys.exit') as sys_exit:
            systems.end(0)
            sys_exit.assert_called_with(0)

    def test_end_fail(self):
        """Should end in error with non-success exit code."""

        with patch('sys.exit') as sys_exit:
            systems.end(1)
            sys_exit.assert_called_with(1)

    def test_remove_no_path(self):
        """Should abort removal if path is None."""

        self.assertFalse(systems.remove(None))

    def test_remove_file_fail(self):
        """Should fail to remove file when os.remove fails."""

        path = 'NOT-REAL-PATH'
        with ExitStack() as stack:
            exists = stack.enter_context(patch('os.path.exists'))
            exists.return_value = True

            is_file = stack.enter_context(patch('os.path.isfile'))
            is_file.return_value = True

            remove = stack.enter_context(patch('os.remove'))
            remove.side_effect = IOError('FAKE ERROR')

            self.assertFalse(systems.remove(path))
            exists.assert_called_with(path)
            self.assertEqual(remove.call_count, 3)

    def test_remove_file_success(self):
        """Should remove file when os.remove succeeds."""

        path = 'NOT-REAL-PATH'
        with ExitStack() as stack:
            exists = stack.enter_context(patch('os.path.exists'))
            exists.return_value = True

            is_file = stack.enter_context(patch('os.path.isfile'))
            is_file.return_value = True

            remove = stack.enter_context(patch('os.remove'))
            remove.return_value = True

            self.assertTrue(systems.remove(path))
            exists.assert_called_with(path)
            self.assertEqual(remove.call_count, 1)

    def test_remove_folder_fail(self):
        """Should fail to remove folder when os.remove fails."""

        path = 'NOT-REAL-PATH'
        with ExitStack() as stack:
            exists = stack.enter_context(patch('os.path.exists'))
            exists.return_value = True

            is_file = stack.enter_context(patch('os.path.isfile'))
            is_file.return_value = False

            remove_tree = stack.enter_context(patch('shutil.rmtree'))
            remove_tree.side_effect = IOError('FAKE ERROR')

            self.assertFalse(systems.remove(path))
            exists.assert_called_with(path)
            self.assertEqual(remove_tree.call_count, 3)

    def test_remove_folder_success(self):
        """Should remove file when os.remove succeeds."""

        path = 'NOT-REAL-PATH'
        with ExitStack() as stack:
            exists = stack.enter_context(patch('os.path.exists'))
            exists.return_value = True

            is_file = stack.enter_context(patch('os.path.isfile'))
            is_file.return_value = False

            remove_tree = stack.enter_context(patch('shutil.rmtree'))
            remove_tree.return_value = True

            self.assertTrue(systems.remove(path))
            exists.assert_called_with(path)
            self.assertEqual(remove_tree.call_count, 1)

    def test_simplify_path(self):
        """Should simplify the path """

        path = os.path.dirname(os.path.realpath(__file__))
        parent = os.path.dirname(path)
        result = systems.simplify_path(path, [('[ME]', parent)])
        self.assertTrue(result.startswith('[ME]'))

    def test_simplify_path_no_match(self):
        """Should not simplify the path if it doesn't match """

        path = 'NOT-A-REAL-PATH'
        result = systems.simplify_path(path, [])
        self.assertEqual(path, result)

    def test_module_to_package_data_core_package(self):
        """Should return None when module is part of the standard library."""

        result = systems.module_to_package_data('os', os)
        self.assertIsNone(result)

    def test_module_to_package_data_submodule(self):
        """Should return None if the module is a submodule."""

        result = systems.module_to_package_data('cauldron.environ', None)
        self.assertIsNone(result)

    def test_get_site_packages_success(self):
        """Should get site packages."""
        if not hasattr(site, 'getsitepackages'):  # pragma: no cover
            # Some versions of python on different systems lacked this
            # function. Here we enforce its existence for testing.
            setattr(site, 'getsitepackages', lambda *args, **kwargs: [])

        data = [1, 2, 3]
        with patch('site.getsitepackages') as get_site_packages:
            get_site_packages.return_value = data
            result = systems.get_site_packages()

        self.assertEqual(data, result)

    def test_get_site_packages_failed(self):
        """Should return an empty list if unable to get site packages."""
        if not hasattr(site, 'getsitepackages'):  # pragma: no cover
            # Some versions of python on different systems lacked this
            # function. Here we enforce its existence for testing.
            setattr(site, 'getsitepackages', lambda *args, **kwargs: [])

        with patch('site.getsitepackages') as get_site_packages:
            get_site_packages.side_effect = ValueError('FAKE ERROR')
            result = systems.get_site_packages()

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)
