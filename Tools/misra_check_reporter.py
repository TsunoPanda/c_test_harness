'''
This module create html files which reports deviation of misra c in several files
'''
import os
import sys
import json
import subprocess
import re
import dataclasses
from enum import Enum
import tkinter
from tkinter import Tk, StringVar
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox
from py_module.easy_html import EasyHtml, TableRow, Cell

class _MisraLineType(Enum):
    # Violation Type
    VIOLATION = 0
    # Violation Code or any string other than cppcheck result message.
    CODE      = 1
    # End
    END       = 2

class _MisraReportColor(Enum):
    TABLE_TOP       = '#FFFABB'
    TABLE_TOP_FONT  = '#000000'
    NO_PROBLEM      = '#D3ECF3'
    WARNING         = '#FBE5E7'
    NO_PROBLEM_FONT = '#FF0000'
    WARNING_FONT    = '#0000FF'

class _FileListTableRow(TableRow):
    ''' This class represents row of the file list table in the html report.
    '''
    __CELL_IDX_FILE_PATH           = 0
    __CELL_IDX_ADV_CNT             = 1
    __CELL_IDX_REQ_CHECKED_CNT     = 2
    __CELL_IDX_REQ_NOT_CHECKED_CNT = 3
    __CELL_IDX_MAN_CNT             = 4

    def __init__(self):
        super().__init__(
            background_color = '#FFFFFF',
            font_size = 14,
            cells = [
                Cell(), # File path
                Cell(), # Advisory deviation count
                Cell(), # Required checked deviation count
                Cell(), # Required not checked deviation count
                Cell(), # Mandatory deviation count
            ]
        )

    def set_top_row_param(self):
        ''' This method set the top row parameter
        '''
        font_color = _MisraReportColor.TABLE_TOP_FONT.value
        self.background_color  = _MisraReportColor.TABLE_TOP.value
        self.font_size = 17
        self.cells   = [
            Cell(text = 'File path', font_color = font_color),
            Cell(text = 'Advisory count', font_color = font_color),
            Cell(text = 'Required count<br>Checked', font_color = font_color),
            Cell(text = 'Required count<br>Not checked', font_color = font_color),
            Cell(text = 'Mandatory count', font_color = font_color),
        ]

    def set_file_path(self, file_path:str, link:str):
        ''' This method set the "file path" and "link" of the file path cell of the row
        '''
        cell_idx = self.__CELL_IDX_FILE_PATH
        self.cells[cell_idx].text = file_path
        self.cells[cell_idx].link = link

    def set_advisory_count(self, count:int):
        ''' This method set the count of the "advisory count" cell of the row
        '''
        cell_idx = self.__CELL_IDX_ADV_CNT
        self.cells[cell_idx].text = str(count)
        self.cells[cell_idx].font_color = _MisraReportColor.NO_PROBLEM_FONT.value

    def set_required_checked_count(self, count:int):
        ''' This method set the count of the "required checked" cell of the row
        '''
        cell_idx = self.__CELL_IDX_REQ_CHECKED_CNT
        self.cells[cell_idx].text = str(count)
        self.cells[cell_idx].font_color = _MisraReportColor.NO_PROBLEM_FONT.value

    def set_required_not_checked_count(self, count:int):
        ''' This method set the count of the "required not checked" cell of the row
        '''
        cell_idx = self.__CELL_IDX_REQ_NOT_CHECKED_CNT
        self.cells[cell_idx].text = str(count)
        self.cells[cell_idx].font_color = _MisraReportColor.WARNING_FONT.value

    def set_mandatory_count(self, count:int):
        ''' This method set the count of the "mandatory" cell of the row
        '''
        cell_idx = self.__CELL_IDX_MAN_CNT
        self.cells[cell_idx].text = str(count)
        self.cells[cell_idx].font_color = _MisraReportColor.WARNING_FONT.value

class _SummaryTableRow(TableRow):
    ''' This class represents row of the summary table in the html report.
    '''
    __CELL_IDX_TYPE  = 0
    __CELL_IDX_COUNT = 1

    def __init__(self):
        super().__init__(
            background_color = '#FFFFFF',
            font_size = 14,
            cells = [
                Cell(), # Type
                Cell(), # Deviation count
            ]
        )

    def set_top_row_param(self):
        ''' This method setups the top row parameter
        '''
        font_color = _MisraReportColor.TABLE_TOP_FONT.value
        self.background_color  = _MisraReportColor.TABLE_TOP.value
        self.font_size = 17
        self.cells   = [
            Cell(text = 'Type', font_color = font_color),
            Cell(text = 'Deviation count', font_color = font_color),
        ]

    def set_advisory_row_param(self, count:int):
        ''' This method sets the advisory count row parameter
        '''
        self.background_color  = _MisraReportColor.NO_PROBLEM.value
        self.font_size = 14
        self.cells   = [
            Cell(text = 'Advisory'),
            Cell(text = str(count)),
        ]

    def set_required_checked_row_param(self, count:int):
        ''' This method sets the required checked count row parameter
        '''
        self.background_color  = _MisraReportColor.NO_PROBLEM.value
        self.font_size = 14
        self.cells   = [
            Cell(text = 'Required checked'),
            Cell(text = str(count)),
        ]

    def set_required_not_checked_row_param(self, count:int):
        ''' This method sets the required not-checked count row parameter
        '''
        self.background_color  = _MisraReportColor.WARNING.value
        self.font_size = 14
        self.cells   = [
            Cell(text = 'Required not checked'),
            Cell(text = str(count)),
        ]

    def set_mandatory_row_param(self, count:int):
        ''' This method sets the mandatory count row parameter
        '''
        self.background_color  = _MisraReportColor.WARNING.value
        self.font_size = 14
        self.cells   = [
            Cell(text = 'Mandatory'),
            Cell(text = str(count)),
        ]

class _DetailedTableRow(TableRow):
    ''' This class represents row of the detailed table in the html report.
    '''
    __CELL_IDX_LINE       = 0
    __CELL_IDX_CODE       = 1
    __CELL_IDX_RULE_INDEX = 2
    __CELL_IDX_RULE_DESC  = 3
    __CELL_IDX_TYPE       = 4
    __CELL_IDX_CHECKED    = 5

    __CHECKED_MARKER         = 'Yes'
    __NOT_CHECKED_MARKER     = 'No'
    __NO_NEED_CHECKED_MARKER = '-'

    def __init__(self):
        super().__init__(
            background_color = '#FFFFFF',
            font_size = 14,
            cells = [
                Cell(), # Deviation line
                Cell(), # Code
                Cell(), # Rule index
                Cell(), # Rule
                Cell(), # Type
                Cell(), # Checked
            ]
        )


    def set_top_row_param(self):
        ''' This method setups the top row parameter
        '''
        font_color = _MisraReportColor.TABLE_TOP_FONT.value
        self.background_color  = _MisraReportColor.TABLE_TOP.value
        self.font_size = 17
        self.cells   = [
            Cell('Line',       font_color, '', '4%'),
            Cell('Code',       font_color, '', '30%'),
            Cell('Rule Index', font_color, '', '4%'),
            Cell('Rule',       font_color, '', '50%'),
            Cell('Type',       font_color, '', '6%'),
            Cell('Checked',    font_color, '', '6%'),
            ]

    def set_line(self, line:int):
        ''' This method sets the line cell string
        '''
        self.cells[self.__CELL_IDX_LINE].text = str(line)

    def get_line(self):
        ''' This method gets the line cell string
        '''
        return self.cells[self.__CELL_IDX_LINE].text

    def set_code(self, code:str):
        ''' This method gets the code cell string
        '''
        self.cells[self.__CELL_IDX_CODE].text = code

    def set_code_align_left(self):
        ''' This method sets the code cell's align
        '''
        self.cells[self.__CELL_IDX_CODE].align = 'left'

    def set_rule_index(self, rule_idx:str):
        ''' This method sets the rule index cell's string
        '''
        self.cells[self.__CELL_IDX_RULE_INDEX].text = rule_idx

    def set_rule(self, rule:str):
        ''' This method sets the rule cell's string
        '''
        self.cells[self.__CELL_IDX_RULE_DESC].text = rule

    def set_rule_align_left(self):
        ''' This method sets the rule cell's align
        '''
        self.cells[self.__CELL_IDX_RULE_DESC].align = 'left'

    def set_type(self, misra_type:str):
        ''' This method sets the type cell's align
        '''
        self.cells[self.__CELL_IDX_TYPE].text = misra_type

    def get_type(self) -> str:
        ''' This method gets the type cell's align
        '''
        return self.cells[self.__CELL_IDX_TYPE].text

    def set_checked(self):
        ''' This method sets the checked cell as "checked"
        '''
        self.cells[self.__CELL_IDX_CHECKED].text = self.__CHECKED_MARKER

    def set_not_checked(self):
        ''' This method sets the checked cell as "not checked"
        '''
        self.cells[self.__CELL_IDX_CHECKED].text = self.__NOT_CHECKED_MARKER

    def set_no_need_to_be_checked(self):
        ''' This method sets the checked cell as "no need to be checked"
        '''
        self.cells[self.__CELL_IDX_CHECKED].text = self.__NO_NEED_CHECKED_MARKER

    def set_color(self, bg_color:str):
        ''' This method sets the background color of the row
        '''
        self.background_color = bg_color

    def set_font_size(self, font_size:int):
        ''' This method sets the fond size of the row "no need to be checked"
        '''
        self.font_size = font_size

    def is_checked(self):
        ''' This method returns "True" if the deviation has been marked as 'checked'.
        '''
        if self.cells[self.__CELL_IDX_CHECKED].text == self.__CHECKED_MARKER:
            return True
        return False


class MisraCheckReporter:
    # pylint: disable=too-many-instance-attributes
    '''
    This class
    '''

    __MISRA_C_2012_RULE_FILE = 'misra_c_2012_rules.json'
    __CPPCHECK_COMMAND       = 'cppcheck --addon=misra.py'

    # Note: These string has to match with the string in .json file.
    __TYPE_ADVISORY_JSON_STR = 'Advisory'
    __TYPE_REQUIRED_JSON_STR = 'Required'
    __TYPE_MANDATORY_JSON_STR = 'Mandatory'

    @dataclasses.dataclass
    class _MessageAnalyzeResult:
        # pylint: disable=too-many-instance-attributes
        # MISRA_LINE_TYPE_VIOLATION or MISRA_LINE_TYPE_CODE or MISRA_LINE_TYPE_END
        line_type:        _MisraLineType  = _MisraLineType.VIOLATION

        # Path to the file where the violation was found
        file_path:        str             = ''

        # Line where the violation was found
        violation_line:   int             = 0

        # Column where the violation was found
        violation_column: int             = 0

        # Description of the rule which was violated
        rule_messag:      str             = ''

        # Index of the rule
        rule_idx:         str             = ''

        # The code which violates the rule
        code:             str             = ''

        # The justification comment
        comment:          str             = ''

    def __init__(self, code_folder_path:str, report_path:str):
        #pylint: disable=unsubscriptable-object

        # A dictionary which contains MISRA C 2012 rule information.
        # The data structure is shown in below
        # 'rule index 1' :
        # {
        #   'Type'     : Required or Advisory or Mandatory
        #   'Decidable' : Decidable or Undecidable
        #   'Rule'     : Description of the rule
        # }
        # 'rule index 2' :
        # {
        # ....... (same as above)
        # }
        self.__misra_rule: dict[str, dict[str, str]] = {}



        # A dictionary. key is the file path. and the value is
        # a list to the 'table_row' which contains violation
        # information
        # file_path : [
        #    table_row1,
        #    table_row2,
        #    ....
        # ]
        self.__deviation_table: dict[str, list[_DetailedTableRow]] = {}

        # Violation amount of type 'advisory'
        self.__advisory_deviation_count:int = 0

        # Violation amount of type 'required'
        self.__required_checked_deviation_count:int = 0

        # Violation amount of type 'required'
        self.__required_not_checked_deviation_count:int = 0

        # Violation amount of type 'mandatory'
        self.__mandatory_deviation_count:int = 0

        self.__product_code_path:str = code_folder_path
        self.__report_path:str       = report_path


    def __execute_cppcheck_misra(self):
        """Executes a command which checks product codes

        This method executes cppcheck command and return the result message
        as a line by line list.

        Returns:
             A list which contains lines of the result message of the cppcheck

         """

        # Make the Cppcheck command
        cmd = self.__CPPCHECK_COMMAND + ' ' + self.__product_code_path

        # Execute the command and get the output as binary
        whole_msg_byte = subprocess.check_output(cmd,
                                               stderr=subprocess.STDOUT,
                                               shell=False)

        # Convert the binary into string
        whole_msg = whole_msg_byte.decode()

        # Split the string line by line into a list
        whole_msg_lines = whole_msg.splitlines()

        # Return the list
        return whole_msg_lines

    def __analyze_message_line(self, line_str:str) -> _MessageAnalyzeResult:
        """Analyzes a line of the the cppcheck result massage

        This method checks the cppcheck output message line.
        And classify it into three types, they are 'violation', 'code', 'end'.
        Then returns the informations accordingly

        The message from the checker is a stream of like below example three
        line. First line is violation information. This function classifies
        this line as type 'violation'. Second line is violation code.
        This function classifies this line as type 'code'.
        Third line is suggesting column where the violation occurred.
        This function classifies this line as type 'end'
        ---------------- Example start from here -----------------
        ..\\..\\code.c:269:11: style: 'misra rule' [misra-c2012-17.7]
            memcpy(pOutData, &self->pBuffer[self->tail], size);
                  ^
        ---------------- End of the Example ----------------------

        Returns:
            see LineInfo
         """

        checked_comment_pattern = r'\/\* *MISRA CHECKED:(.+)\*\/'

        # regular expression to catch the misra-c-2012 violation message
        deviation_pattern = (r'(.+)\:(\d+)\:(\d+)\: style\:'
                   r' (.+)\[misra-c2012-(\d+\.\d+)\]')

        # Get the match result.
        deviation_match_result = re.match(deviation_pattern, line_str)

        # If the match result is NOT None, it is violation message
        is_deviation_message = (deviation_match_result is not None)

        # Remove all space to check if it is the type end
        line_without_space = line_str.replace(' ', '')

        # If only '^' is remained, it is the type end
        is_message_end_line = (line_without_space == '^')

        # Define the return dictionary
        c_line_info = self._MessageAnalyzeResult()

        # If it was the type violation
        if is_deviation_message is True:
            # Catch the violation information
            c_line_info.line_type        = _MisraLineType.VIOLATION
            c_line_info.file_path        = deviation_match_result.group(1)
            c_line_info.violation_line   = int(deviation_match_result.group(2))
            c_line_info.violation_column = int( deviation_match_result.group(3))
            c_line_info.rule_messag      = deviation_match_result.group(4)
            c_line_info.rule_idx         = deviation_match_result.group(5)
        # If it was the type end,
        elif is_message_end_line is True:
            # No information to return. just return the type end
            c_line_info.line_type        = _MisraLineType.END
        # If it was the type code.
        else:
            # Note: Any strings other than cppcheck result message
            #       will reach here.
            # Catch the code string
            c_line_info.line_type        = _MisraLineType.CODE
            c_line_info.code             = line_str
            checked_comment_match_result = re.search(checked_comment_pattern, line_str)
            if checked_comment_match_result is not None:
                c_line_info.comment      = checked_comment_match_result.group(1)


        # Return the result
        return c_line_info

    def __make_report_summary_section(self, report_html:EasyHtml):
        """Makes a summary table on the html

        This method makes a summary table on the input html object
        as referring the counters of the violations in private data.

        """

        # Make Summary section
        report_html.set_body_h2('Summary', 'center')

        # Create Summary table
        summary_table = report_html.create_table(5, 'center', '50%')

        # Append the top row to the table
        top_row = _SummaryTableRow()
        top_row.set_top_row_param()
        summary_table.create_table_row(top_row)

        # Append the advisory violation count row to the table
        row = _SummaryTableRow()
        row.set_advisory_row_param(self.__advisory_deviation_count)
        summary_table.create_table_row(row)

        # Append the required violation row to the table
        row = _SummaryTableRow()
        row.set_required_checked_row_param(self.__required_checked_deviation_count)
        summary_table.create_table_row(row)

        # Append the required violation row to the table
        row = _SummaryTableRow()
        row.set_required_not_checked_row_param(self.__required_not_checked_deviation_count)
        summary_table.create_table_row(row)

        # Append the mandatory violation row to the table
        row = _SummaryTableRow()
        row.set_mandatory_row_param(self.__mandatory_deviation_count)
        summary_table.create_table_row(row)

    def __make_detailed_section(self, report_html:EasyHtml):
        """Makes the detailed table on the html

        This method makes the detailed table on the input html object as
        referring the violation information captured from cppcheck

        """

        #pylint: disable=unsubscriptable-object
        def count_deviation(html_table:list[_DetailedTableRow]):

            advisory_count = 0
            required_not_checked_count = 0
            required_checked_count = 0
            mandatory_count = 0
            for row in html_table:
                if row.get_type() == self.__TYPE_ADVISORY_JSON_STR:
                    advisory_count += 1
                elif row.get_type() == self.__TYPE_REQUIRED_JSON_STR:
                    if row.is_checked():
                        required_checked_count += 1
                    else:
                        required_not_checked_count += 1
                elif row.get_type() == self.__TYPE_MANDATORY_JSON_STR:
                    mandatory_count += 1
                else:
                    print('Unknow type detected.')
                    sys.exit(1)
            return (advisory_count, required_checked_count,
                    required_not_checked_count, mandatory_count)

        def append_file_table_row(file_table, file_path, link):
            detailed_table = self.__deviation_table[file_path]
            [advisory_count,
             required_checked_count,
             required_not_checked_count,
             mandatory_count] = count_deviation(detailed_table)
            row = _FileListTableRow()
            row.set_file_path(file_path,link)
            row.set_advisory_count(advisory_count)
            row.set_required_checked_count(required_checked_count)
            row.set_required_not_checked_count(required_not_checked_count)
            row.set_mandatory_count(mandatory_count)
            file_table.create_table_row(row)

        def create_sub_html_file(file_path, out_file_name):
            file_name = os.path.basename(file_path)
            # List of the top row of the table
            top_row = _DetailedTableRow()
            top_row.set_top_row_param()

            # Create a sub html object
            report_per_file = EasyHtml(tag = file_name)

            # Add back link to the index.html
            report_per_file.set_body_h3('back', 'left', link = '000_index.html')

            # Make detailed report table title
            report_per_file.set_body_h2('Deviation Report: ' + file_path, 'center')

            # Make detailed report table
            detailed_table = report_per_file.create_table(5, 'center', '95%')

            # Add top row of the table
            detailed_table.create_table_row(top_row)

            # Add all rows of the violation information
            for row in self.__deviation_table[file_path]:
                detailed_table.create_table_row(row)

            file_name = self.__report_path + '/' + out_file_name
            report_per_file.output_html(4, file_name)

        # Make deviation per files section
        report_html.set_body_h2('Deviation files', 'center')

        # Create deviation files table
        file_table = report_html.create_table(5, 'center', '90%')

        # Append the top row to the table
        top_row = _FileListTableRow()
        top_row.set_top_row_param()
        file_table.create_table_row(top_row)


        # Initialize the file counter to be used for naming the sub html files.
        file_count = 0

        # Append all the detailed violation message to the table
        for file_path in sorted(self.__deviation_table) :
            file_count += 1

            code_file_name = os.path.basename(file_path)

            out_file_name = self.__sub_html_name(file_count, code_file_name)

            # Add row of the deviation file table
            append_file_table_row(file_table, file_path, out_file_name)

            # Create sub html file
            create_sub_html_file(file_path, out_file_name)

    @staticmethod
    def __sub_html_name(file_count, file_name):
        return str(file_count).zfill(3) + '_' + file_name + '.html'

    def __sort_deviation_table(self):
        """Sorts the violation table by code line
        """
        def sort_key(table_row:_DetailedTableRow):
            return table_row.get_line().zfill(10)

        for key in self.__deviation_table:
            self.__deviation_table[key] = sorted(self.__deviation_table[key],
                                                 key = sort_key)

    def get_misra_rule_dictionary(self):
        """Gets Misra rule dictionary

        This method reads the json file which contains MISRA C 2012 rule
        information. And saves the rule information as a dictionary type data
        into a instance variable __dMisraRule
         """

        # Open the json file which contains MISRA C 2012 rule information
        with  open(self.__MISRA_C_2012_RULE_FILE, 'r',
                   encoding = 'UTF-8') as misra_rule_raw_json_file:
            # Load the json file and save it into a dictionary data
            self.__misra_rule = json.load(misra_rule_raw_json_file)

    def __create_detailed_table(self,
                                analyze_result:_MessageAnalyzeResult) -> _DetailedTableRow:
        rule_idx  = analyze_result.rule_idx
        c_table_row = _DetailedTableRow()
        c_table_row.set_code_align_left()
        c_table_row.set_rule_align_left()
        c_table_row.set_line(analyze_result.violation_line)
        c_table_row.set_rule_index(rule_idx)
        c_table_row.set_rule(self.__misra_rule[rule_idx]['Rule'])
        c_table_row.set_type(self.__misra_rule[rule_idx]['Type'])
        return c_table_row

    def __add_detailed_table_code_info(self, c_table_row: _DetailedTableRow,
                                       analyze_result:_MessageAnalyzeResult):

        is_required_deviation_checked = (analyze_result.comment != '')

        c_table_row.set_code(analyze_result.code)

        if c_table_row.get_type() == self.__TYPE_ADVISORY_JSON_STR:
            self.__advisory_deviation_count += 1
            c_table_row.set_no_need_to_be_checked()
            c_table_row.set_color(_MisraReportColor.NO_PROBLEM.value)
        elif c_table_row.get_type() == self.__TYPE_REQUIRED_JSON_STR:
            if is_required_deviation_checked:
                self.__required_checked_deviation_count += 1
                c_table_row.set_checked()
                c_table_row.set_color(_MisraReportColor.NO_PROBLEM.value)
            else:
                self.__required_not_checked_deviation_count += 1
                c_table_row.set_not_checked()
                c_table_row.set_color(_MisraReportColor.WARNING.value)
        else: # if c_table_row.get_type() == self. __TYPE_MANDATORY_JSON_STR
            self.__mandatory_deviation_count += 1
            c_table_row.set_no_need_to_be_checked()
            c_table_row.set_color(_MisraReportColor.WARNING.value)

    def cpp_check(self):
        """Executes the cppcheck and analyze the result message

        This method executes the cppcheck. And receives
        the output message of the check and analyzes it.
        The analyze result will be stored into the private
        dictionary variable

        """

        # Execute the cppcheck(misra.py) and get the result as a list of
        # message line
        whole_message = self.__execute_cppcheck_misra()

        # Analyze the cppcheck result message line by line
        for line in whole_message:

            # Analyze the line and get the information
            # cLineAnalyzeResult: _LineInfo
            c_line_analyzation_result = self.__analyze_message_line(line)

            # If it was the violation message,
            if c_line_analyzation_result.line_type == _MisraLineType.VIOLATION:
                # Create a dictionary which contains the html detailed row table data

                # Create new deviation table
                file_path = c_line_analyzation_result.file_path
                if file_path not in self.__deviation_table:
                    self.__deviation_table[file_path] = []

                # Create new c table row
                c_table_row = self.__create_detailed_table(c_line_analyzation_result)

            # If it was the code message,
            # (or any other string than cppcheck result message)
            elif c_line_analyzation_result.line_type == _MisraLineType.CODE:
                # Check if dHtmlRowInfo exists
                if 'c_table_row' not in locals():
                    # Not exists.
                    # This means it hasn't received violation message yet.
                    # Skip and check next line
                    continue

                # Save the code string to the table
                self.__add_detailed_table_code_info(c_table_row, c_line_analyzation_result)


            # If it was the end message,
            else :  # dLineAnalyzeResult['lineType'] == MISRA_LINE_TYPE_END
                # Check if dHtmlRowInfo exists
                if 'c_table_row' not in locals():
                    # Not exists.
                    # This means it hasn't received violation message yet.
                    # Skip and check next line
                    continue

                # Append a row of html detailed table according to the private
                # variable
                self.__deviation_table[file_path].append(c_table_row)

                # Delete the dictionary
                del c_table_row

    def make_html_report(self, out_html:str):
        """Makes a html report

        This method makes a html report as referring the previous
        cppcheck result

        """
        # Sort the violation information by line
        self.__sort_deviation_table()

        # Make reporting html file
        report_html = EasyHtml()

        # Set title
        report_html.set_title('Misra C 2012 Check Result')

        # Set body title
        report_html.set_body_h1('Misra C 2012 Check Result', 'center')

        # Make summary section
        self.__make_report_summary_section(report_html)

        # Make detailed report section
        self.__make_detailed_section(report_html)

        # output the html
        report_html.output_html(4, self.__report_path +'/'+ out_html)

class DirectorySelector:
    #pylint: disable=too-few-public-methods
    ''' This class represent directory selector UI like below.
        description: [ -selected directory- ] [browsing button]
    '''
    def __init__(self, frame, name:str):
        self.__label = ttk.Label(frame, text=name+': ')

        self.__directory_var = StringVar()
        self.__directory_entry = ttk.Entry(frame, width = 100, textvariable=self.__directory_var)
        self.__select_button = ttk.Button(
            frame,
            width = 5,
            text='...',
            command= lambda: self.__get_dir_dialog() #pylint: disable=unnecessary-lambda
            )

        self.dir_name:str = ''

    def __get_dir_dialog(self):
        this_dir = os.getcwd()
        open_dir = filedialog.askdirectory(initialdir=this_dir)
        if open_dir != "":
            self.__directory_var.set(open_dir)
            self.dir_name = open_dir

    def grid(self, row_in:int):
        ''' This method put the selector UI.
        Args:
             row_in: the row where this UI places.
        '''
        self.__label.grid(row = row_in, column = 0, pady = (0, 8))
        self.__directory_entry.grid(row = row_in, column = 1, pady = (0, 8), sticky=tkinter.EW)
        self.__select_button.grid(row = row_in, pady = (0, 8), column = 2)


def create_misra_report(code_path:str, out_dir_path:str):
    ''' This function creates html misra report.
        This is called when the 'create' button was clicked
    Args:
         code_path: The path to the directory where code to be analyzed locates
         out_dir_path: The path to the directory where the html report will be created
    '''
    if os.path.exists(code_path) and os.path.exists(out_dir_path):

        reporter = MisraCheckReporter(code_path, out_dir_path)

        # At first, load the Misra C rule information
        reporter.get_misra_rule_dictionary()

        # CppCheck starts. And save the results in the private variable
        reporter.cpp_check()

        # Output the report as html style
        reporter.make_html_report('000_index.html')

        messagebox.showinfo('Misra Reporter', 'Report files generated.')
    else:
        messagebox.showerror('Misra Reporter', 'Could not found input directory')

if __name__ == '__main__':

    root = Tk()
    root.title('Misra Reporter')
    root.grid_columnconfigure(0, weight=1)

    directory_select_frame = ttk.Frame(root)
    target_directory = DirectorySelector(directory_select_frame, 'Target code directory')
    result_directory = DirectorySelector(directory_select_frame, 'Result output directory')

    target_directory.grid(0)
    result_directory.grid(1)
    directory_select_frame.grid_columnconfigure(1, weight=1)
    directory_select_frame.grid(sticky=tkinter.EW, padx = 8, pady = (8, 0))

    create_button_frame = ttk.Frame(root)
    create_button_frame.grid(sticky=tkinter.E)

    create_button = ttk.Button(
        create_button_frame, text='Create',
        command = lambda: create_misra_report(target_directory.dir_name, result_directory.dir_name))
    create_button.grid(padx=8, pady= (0,8))

    root.mainloop()
