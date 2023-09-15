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
    link:       str = ''

@dataclass
class TableRow:
    """
    This class is a data class which has parameters for the table row.
    """
    background_color: str        = '#000000'
    font_size:        int        = 1
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

    def __set_link(self, text:str, link:str) -> None: # pylint: disable=unused-private-member
        """
        This method adds link to other contents
        """
        link_obj = self.__create_child('a')       # pylint: disable=protected-access
        link_obj.__set_option('href = "' + link + '"') # pylint: disable=protected-access
        link_obj.__set_text(text)                 # pylint: disable=protected-access

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

    def set_title(self, text:str, link:str ='') -> None:
        """
        This method adds a title text to the EasyHtml instance
        """
        head = self.__create_child('head')
        title = head.__create_child('title') # pylint: disable=protected-access
        if link == '':
            title.__set_text(text) # pylint: disable=protected-access
        else:
            title.__set_link(text, link) # pylint: disable=protected-access

    def set_body_h1(self, text:str, align:str, link:str = '') -> None:
        """
        This method adds high light 1 text to the EasyHtml instance
        """
        body = self.__get_body()
        h1_title = body.__create_child('h1')      # pylint: disable=protected-access
        h1_title.__set_option('align = ' + align) # pylint: disable=protected-access
        if link == '':
            h1_title.__set_text(text) # pylint: disable=protected-access
        else:
            h1_title.__set_link(text, link) # pylint: disable=protected-access

    def set_body_h2(self, text:str, align:str, link = '') -> None:
        """
        This method adds high light 2 text to the EasyHtml instance
        """
        body = self.__get_body()
        h2_title = body.__create_child('h2')      # pylint: disable=protected-access
        h2_title.__set_option('align = ' + align) # pylint: disable=protected-access
        if link == '':
            h2_title.__set_text(text) # pylint: disable=protected-access
        else:
            h2_title.__set_link(text, link) # pylint: disable=protected-access

    def set_body_h3(self, text:str, align:str, link:str = '') -> None:
        """
        This method adds high light 3 text to the EasyHtml instance
        """
        body = self.__get_body()
        h3_title = body.__create_child('h3')      # pylint: disable=protected-access
        h3_title.__set_option('align = ' + align) # pylint: disable=protected-access
        if link == '':
            h3_title.__set_text(text) # pylint: disable=protected-access
        else:
            h3_title.__set_link(text, link) # pylint: disable=protected-access

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
            table_row.create_table_cell(cell) # pylint: disable=protected-access
        return table_row

    def create_table_cell(self, cell:Cell):
        """
        This method creates a table cell object in the table row instance and return the
        cell object.
        """
        cell_obj = self.__create_child('th')
        option_str = ''
        if cell.align != '':
            option_str += (' align = ' + cell.align)
        if cell.width != '':
            option_str += (' width = "' + cell.width + '"')
        cell_obj.__set_option(option_str) # pylint: disable=protected-access
        cell_font = cell_obj.__create_child('font') # pylint: disable=protected-access
        cell_font.__set_option('color =' + cell.font_color) # pylint: disable=protected-access
        if cell.link == '':
            cell_font.__set_text(cell.text) # pylint: disable=protected-access
        else:
            cell_font.__set_link(text=cell.text, link=cell.link) # pylint: disable=protected-access

    def output_html(self, indent:int, file_path:str):
        """
        This method saves the html file at the input file path.
        """
        with open(file_path, 'w', encoding = 'UTF-8') as file_handle:
            file_handle.write('<!DOCTYPE html>' + "\n")
            self.__dump_data_as_html(file_handle, indent)
