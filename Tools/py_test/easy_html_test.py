import unittest
from py_module.easy_html import EasyHtml, TableRow, Cell

class BasicTest(unittest.TestCase):

    def test_basic_000_output_basic_html(self):
        test_html = EasyHtml()
        test_html.set_title('this is the title')
        test_html.set_body_h1('this is the body highlight 1', 'center', 'http://google.com')
        test_html.set_body_h2('this is the body highlight 2', 'center')
        test_html.set_body_h3('this is the body highlight 3', 'center')

        # Create a table
        test_table = test_html.create_table(5, 'center', '50%')

        # Create the first row of the table
        top_row = TableRow(
            background_color  = '#FFFFFF',
            font_size = 17,
            cells   =
            [
                Cell(text = 'this is first cell'),
                Cell(text = 'this is second cell'),
            ],)
        test_table.create_table_row(top_row)

        # Create the second row of the table
        second_row = TableRow(
            background_color  = '#00AA00',
            font_size = 17,
            cells   =
            [
                Cell(text = 'this is first cell of second row',
                        font_color = '#FFFFFF'),
                Cell(text = 'go to google', link = 'http://google.com',
                        font_color = '#FFFFFF'),
            ],)
        test_table.create_table_row(second_row)

        # Output the html file
        test_html.output_html(4, 'py_test/easy_html_test/basic.html')

        print('Please check output html')

    def test_basic_001_output_linking_html(self):
        test_html = EasyHtml()
        test_html.set_title('this is only a link')
        test_html.set_body_h1('Goto basic page', 'center', 'basic.html')
        test_html.output_html(4, 'py_test/easy_html_test/link.html')
