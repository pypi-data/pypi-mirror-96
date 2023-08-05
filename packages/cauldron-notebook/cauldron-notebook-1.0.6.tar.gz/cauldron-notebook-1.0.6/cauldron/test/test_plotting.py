from cauldron import plotting
from cauldron.test.support import scaffolds


class TestPlotting(scaffolds.ResultsTest):
    """Test suite for the plotting package"""

    def test_grey_color(self):
        """Should return gray colors based on arguments."""
        color = plotting.get_gray_color()
        self.assertEqual(color, 'rgba(128, 128, 128, 1.0)')

        color = plotting.get_gray_color(234, 0.34)
        self.assertEqual(color, 'rgba(234, 234, 234, 0.34)')

        color = plotting.get_gray_color(50, 0.1, False)
        self.assertEqual(len(color), 4)

    def test_get_color(self):
        """Should return colors with modifications"""
        color = plotting.get_color(0, 0.5, False)
        self.assertEqual(len(color), 4)

        color = plotting.get_color(4)
        self.assertTrue(color.startswith('rgba('))

        color = plotting.get_color(1235, 0.5)
        self.assertTrue(color.startswith('rgba('))

    def test_create_layout(self):
        """Should create layout using supplied arguments"""
        title = 'Some Title'
        x_label = 'X Label'
        y_label = 'Y Label'
        x_bounds = [3, 97]
        y_bounds = [-32, 48]

        layout = plotting.create_layout(
            layout={},
            title=title,
            x_label=x_label,
            y_label=y_label,
            x_bounds=x_bounds,
            y_bounds=y_bounds
        )

        self.assertIsInstance(layout, dict)
        self.assertIn('title', layout)

    def test_create_layout_defaults(self):
        """Should create a layout dictionary using default values."""
        layout = plotting.create_layout()
        self.assertIsInstance(layout, dict)
        self.assertIsNone(layout['title'])

    def test_make_line_data(self):
        """Should make line data according to arguments"""
        data = plotting.make_line_data(
            x=[1, 2, 3, 4],
            y=[1, 2, 3, 4],
            y_unc=[0.1, 0.1, 0.1, 0.1],
            name='TEST',
            color=plotting.get_color(4),
            fill_color=plotting.get_color(5, 0.2),
            line_properties={},
            marker_properties={}
        )
        self.assertIsInstance(data, dict)
        self.assertIn('data', data)
        self.assertIn('layout', data)

    def test_make_line_data_defaults(self):
        """Should make line data using default values"""
        data = plotting.make_line_data(
            x=[1, 2, 3, 4],
            y=[1, 2, 3, 4],
            y_unc=[0.1, 0.1, 0.1, 0.1]
        )
        self.assertIsInstance(data, dict)
        self.assertIn('data', data)
        self.assertIn('layout', data)

    def test_make_line_data_explicit_width(self):
        """Should make line using the line properties as the line width."""
        data = plotting.make_line_data(
            x=[1, 2, 3, 4],
            y=[1, 2, 3, 4],
            y_unc=[0.1, 0.1, 0.1, 0.1],
            line_properties=3
        )
        self.assertIsInstance(data, dict)
        self.assertIn('data', data)
        self.assertIn('layout', data)

    def test_make_line_data_explicit_size(self):
        """Should make markers invisible by setting the size to zero."""
        data = plotting.make_line_data(
            x=[1, 2, 3, 4],
            y=[1, 2, 3, 4],
            y_unc=[0.1, 0.1, 0.1, 0.1],
            marker_properties=0
        )
        self.assertIsInstance(data, dict)
        self.assertIn('data', data)
        self.assertIn('layout', data)
