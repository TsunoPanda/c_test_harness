"""
This module provides utilities to make the html which contains only title and simple table.
"""
from typing import List
from dataclasses import dataclass, field

@dataclass
class Cell:
    """
    This class is a data class which has parameters for the table cell.
    """
    text:       str = ''
    font_color: str = '#000000'
    align:      str = ''
    width:      str = ''

@dataclass
class TableRow():
    """
    This class is a data class which has parameters for the table row.
    """
    background_color: str        = '#000000'
    font_size:        str        = '1'
    cells:            List[Cell] = field(default_factory = list)  # type: ignore

class EasyHtml:
    """
    This class expresses html file which contains only title and simple table
    """

    def __init__(self, tag:str = 'html') -> None:
        self.tag:str                 = tag
        self.opt:str                 = ''
        self.text:str                = ''
        self.children:List[EasyHtml] = []

    def __set_option(self, option:str) -> None: # pylint: disable=unused-private-member
        self.opt = option

    def __set_text(self, text:str) -> None: # pylint: disable=unused-private-member
        self.text = text

    def __create_child(self, tag:str) -> 'EasyHtml':

        if self.children is None:
            self.children = []

        child = EasyHtml(tag)
        self.children.append(child)

        return child

    def __get_body(self) -> 'EasyHtml':
        for child in self.children:
            if child.tag == 'body':
                return child
        return self.__create_child('body')

    def __dump_data_as_html(self, file_handle, indent:int, space:str = "") -> None:
        if self.opt is None:
            file_handle.write(space + '<' + self.tag + '>' + "\n")
        else:
            file_handle.write(space + '<' + self.tag + ' ' + self.opt + '>' + "\n")

        next_space = space + (" " * indent)

        if self.text:
            file_handle.write(next_space + self.text + "\n")

        if self.children is not None:
            for child in self.children:
                child.__dump_data_as_html(file_handle,  # pylint: disable=protected-access
                                          indent,
                                          next_space)

        file_handle.write(space + '</' + self.tag + '>' + "\n")

    def set_title(self, text:str) -> None:
        """
        This method adds a title text to the EasyHtml instance
        """
        head = self.__create_child('head')
        title = head.__create_child('title') # pylint: disable=protected-access
        title.__set_text(text)               # pylint: disable=protected-access

    def set_body_h1(self, text:str, align:str) -> None:
        """
        This method adds high light 1 text to the EasyHtml instance
        """
        body = self.__get_body()
        h1_title = body.__create_child('h1')      # pylint: disable=protected-access
        h1_title.__set_option('align = ' + align) # pylint: disable=protected-access
        h1_title.__set_text(text)                 # pylint: disable=protected-access

    def set_body_h2(self, text:str, align:str) -> None:
        """
        This method adds high light 2 text to the EasyHtml instance
        """
        body = self.__get_body()
        h2_title = body.__create_child('h2')      # pylint: disable=protected-access
        h2_title.__set_option('align = ' + align) # pylint: disable=protected-access
        h2_title.__set_text(text)                 # pylint: disable=protected-access

    def set_body_h3(self, text:str, align:str) -> None:
        """
        This method adds high light 3 text to the EasyHtml instance
        """
        body = self.__get_body()
        h2_title = body.__create_child('h3')      # pylint: disable=protected-access
        h2_title.__set_option('align = ' + align) # pylint: disable=protected-access
        h2_title.__set_text(text)                 # pylint: disable=protected-access

    def create_table(self, border:int, align:str = '', width:str = '') -> 'EasyHtml':
        """
        This method creates a table object in the EasyHtml instance and return the
        table object.
        """
        body = self.__get_body()
        table = body.__create_child('table') # pylint: disable=protected-access
        option_str = 'border = "' + str(border) + '"'
        if align != '':
            option_str += (' align = ' + align)
        if width != '':
            option_str += (' width = "' + width + '"')
        table.__set_option(option_str) # pylint: disable=protected-access
        return table

    def create_blank_table_row(self, background_color:str, font_size:int):
        """
        This method creates a table row object in the table instance and return the
        row object.
        """
        table_row = self.__create_child('tr')
        option_str  = 'bgcolor = ' + background_color
        option_str += ' style="font-size: ' + str(font_size) + 'pt"'
        table_row.__set_option(option_str) # pylint: disable=protected-access
        return table_row

    def create_table_row(self, table_row_param:TableRow) -> 'EasyHtml':
        """
        This method creates a table row object according to input TableRow instance
        in the table instance and return the row object.
        """
        table_row = self.__create_child('tr')
        option_str  = 'bgcolor = ' + table_row_param.background_color
        option_str += ' style="font-size: ' + str(table_row_param.font_size) + 'pt"'
        table_row.__set_option(option_str) # pylint: disable=protected-access

        for cell in table_row_param.cells:
            table_row.create_table_cell(cell.text, # pylint: disable=protected-access
                                       cell.font_color,
                                       cell.align,
                                       cell.width)
        return table_row

    def create_table_cell(self, text:str,
                        font_color:str = '#000000', align:str = '', width:str = ''):
        """
        This method creates a table cell object in the table row instance and return the
        cell object.
        """
        cell = self.__create_child('th')
        option_str = ''
        if align != '':
            option_str += (' align = ' + align)
        if width != '':
            option_str += (' width = "' + width + '"')
        cell.__set_option(option_str) # pylint: disable=protected-access
        cell_font = cell.__create_child('font') # pylint: disable=protected-access
        cell_font.__set_option('color =' + font_color) # pylint: disable=protected-access
        cell_font.__set_text(text) # pylint: disable=protected-access

    def output_html(self, indent:int, file_path:str):
        """
        This method saves the html file at the input file path.
        """
        with  open(file_path, 'w', encoding = 'UTF-8') as file_handle:
            file_handle.write('<!DOCTYPE html>' + "\n")
            self.__dump_data_as_html(file_handle, indent)

if __name__ == '__main__':
    test_html = EasyHtml()
    test_html.set_title('this is the title')
    test_html.set_body_h1('this is the body highlight 1', 'center')
    test_html.set_body_h2('this is the body highlight 2', 'center')
    test_html.set_body_h3('this is the body highlight 3', 'center')

    # Create a table
    test_table = test_html.create_table(5, 'center', '50%')

    # Create the first row of the table
    top_row = TableRow(
        background_color  = '#FFFFFF',
        font_size = '17',
        cells   =
        [
            Cell(text = 'this is first cell'),
            Cell(text = 'this is second cell'),
        ],)
    test_table.create_table_row(top_row)

    # Create the second row of the table
    second_row = TableRow(
        background_color  = '#00AA00',
        font_size = '17',
        cells   =
        [
            Cell(text = 'this is first cell of second row',
                       font_color = '#FFFFFF'),
            Cell(text = 'this is second cell of second row',
                       font_color = '#FFFFFF'),
        ],)
    test_table.create_table_row(second_row)

    # Output the html file
    test_html.output_html(4, 'test.html')
