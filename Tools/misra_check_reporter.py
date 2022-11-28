'''
This module ...
'''
import sys
import json
import subprocess
import re
import dataclasses
from enum import Enum
from typing import List
from typing import Dict
from py_module.easy_html import EasyHtml, TableRow, Cell

class _MisraLineType(Enum):
    # Violation Type
    VIOLATION = 0
    # Violation Code or any string other than cppcheck result message.
    CODE      = 1
    # End
    END       = 2

class MisraCheckReporter:
    '''
    This class
    '''

    __MISRA_C_2012_RULE_FILE = 'misra_c_2012_rules.json'
    __CPPCHECK_COMMAND       = 'cppcheck --addon=misra.py'

    class _MisraReportColor(Enum):
        TABLE_TOP      = '#A1C3E7'
        TABLE_TOP_FONT = '#FFFFFF'
        ADVISORY       = '#CCDFEF'
        REQUIRED       = '#F8E9D1'
        MANDATORY      = '#F18D1D'

    @dataclasses.dataclass
    class _LineInfo:
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

    def __init__(self, code_folder_path:str):
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
        self.__misra_rule: Dict[str, Dict[str, str]] = {}
        # A dictionary. key is the file path. and the value is
        # a list to the 'table_row' which contains violation
        # information
        # file_path : [
        #    table_row1,
        #    table_row2,
        #    ....
        # ]
        self.__deviation_table: Dict[str, List[TableRow]] = {}

        # Violation amount of type 'advisory'
        self.__advisory_deviation_count:int = 0

        # Violation amount of type 'required'
        self.__required_deviation_count:int = 0

        # Violation amount of type 'mandatory'
        self.__mandatory_deviation_count:int = 0

        self.__product_code_path:str = code_folder_path


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

    def __analyze_message_line(self, line_str:str) -> _LineInfo:
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

        # regular expression to catch the misra-c-2012 violation message
        pattern = (r'(.+)\:(\d+)\:(\d+)\: style\:'
                   r' (.+)\[misra-c2012-(\d+\.\d+)\]')

        # Get the match result.
        match_result = re.match(pattern, line_str)

        # If the match result is NOT None, it is violation message
        is_deviation_message = (match_result is not None)

        # Remove all space to check if it is the type end
        line_without_space = line_str.replace(' ', '')

        # If only '^' is remained, it is the type end
        is_message_end_line = (line_without_space == '^')

        # Define the return dictionary
        c_line_info = self._LineInfo()

        # If it was the type violation
        if is_deviation_message is True:
            # Catch the violation information
            c_line_info.line_type        = _MisraLineType.VIOLATION
            c_line_info.file_path        = match_result.group(1)
            c_line_info.violation_line   = int(match_result.group(2))
            c_line_info.violation_column = int( match_result.group(3))
            c_line_info.rule_messag      = match_result.group(4)
            c_line_info.rule_idx         = match_result.group(5)
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

        # Return the result
        return c_line_info

    def __append_top_row_of_summary_table(self, table:EasyHtml, deviation_type:str, count:str):
        """Appends the top row of the summary table
        """
        top_row = TableRow(
            background_color  = self._MisraReportColor.TABLE_TOP.value,
            font_size = 17,
            cells   = [
                Cell(text = deviation_type),
                Cell(text = count),
            ],
        )
        table.create_table_row(top_row)

    @staticmethod
    def __append_row_of_summary_table(table:EasyHtml, deviation_type:str, count:str, color:str):
        """Appends a row of the summary table
        """

        row = TableRow(
            background_color  = color,
            font_size = 14,
            cells   = [
                Cell(text = deviation_type),
                Cell(text = count),
            ],
        )
        row = table.create_table_row(row)

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
        self.__append_top_row_of_summary_table(summary_table,
                                          'Type',
                                          'Violation count')

        # Append the advisory violation count row to the table
        self.__append_row_of_summary_table(summary_table,
                                       'Advisory',
                                       str(self.__advisory_deviation_count),
                                       self._MisraReportColor.ADVISORY.value)

        # Append the required violation row to the table
        self.__append_row_of_summary_table(summary_table,
                                       'Required',
                                       str(self.__required_deviation_count),
                                       self._MisraReportColor.REQUIRED.value)

        # Append the mandatory violation row to the table
        self.__append_row_of_summary_table(summary_table,
                                       'Mandatory',
                                       str(self.__mandatory_deviation_count),
                                       self._MisraReportColor.MANDATORY.value)

    def __make_detailed_section(self, report_html:EasyHtml):
        """Makes the detailed table on the html

        This method makes the detailed table on the input html object as
        referring the violation information captured from cppcheck

        """

        # List of the top row of the table
        color = self._MisraReportColor.TABLE_TOP_FONT.value
        top_row = TableRow(
            background_color  = self._MisraReportColor.TABLE_TOP.value,
            font_size = 17,
            cells   =
            [
                Cell('Line',       color, '', '4%'),
                Cell('Code',       color, '', '30%'),
                Cell('Rule Index', color, '', '4%'),
                Cell('Rule',       color, '', '50%'),
                Cell('Type',       color, '', '6%'),
                Cell('Decidable',  color, '', '6%'),
            ],)

        # Append all the detailed violation message to the table
        for file_path in sorted(self.__deviation_table) :

            # Make detailed report table
            report_html.set_body_h2('Violation Report: ' + file_path, 'center')
            # Make detailed report table
            detailed_table = report_html.create_table(5, 'center', '95%')
            detailed_table.create_table_row(top_row)

            # Add all rows of the violation information
            for row in self.__deviation_table[file_path]:
                detailed_table.create_table_row(row)

    def __sort_deviation_table(self):
        """Sorts the violation table by code line
        """
        def sort_key(table_row:TableRow):
            return table_row.cells[0].text.zfill(10)

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

    def cpp_check(self):
        """Executes the cppcheck and analyze the result message

        This method executes the cppcheck. And receives
        the output message of the check and analyzes it.
        The analyze result will be stored into the private
        dictionary variable

        """

        # Counter of advisory violations
        advisory_deviation_count  = 0

        # Counter of required violations
        required_deviation_count  = 0

        # Counter of mandatory violations
        mandatory_deviation_count = 0

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
                # Create a dictionary which contains the html detailed row
                # table data

                # Save the file path
                file_path = c_line_analyzation_result.file_path

                # Get the violation information
                rule_idx = c_line_analyzation_result.rule_idx
                rule = self.__misra_rule[rule_idx]['Rule']
                rule_type = self.__misra_rule[rule_idx]['Type']
                decidable = self.__misra_rule[rule_idx]['Decidable']

                if file_path not in self.__deviation_table:
                    self.__deviation_table[file_path] = []

                c_table_row = TableRow(
                    background_color = '',  # will be assigned later
                    font_size = 14,
                    cells =
                    [
                        Cell(str(c_line_analyzation_result.violation_line)),
                        # Cell for code. will be assigned later
                        Cell(align = 'left'),
                        Cell(c_line_analyzation_result.rule_idx),
                        Cell(rule, align = 'left'),
                        Cell(rule_type),
                        Cell(decidable),
                    ],)

            # If it was the code message,
            # (or any other string than cppcheck result message)
            elif c_line_analyzation_result.line_type == _MisraLineType.CODE:
                # Check if dHtmlRowInfo exists
                if 'c_table_row' not in locals():
                    # Not exists.
                    # This means it hasn't received violation message yet.
                    # Skip and check next line
                    continue

                # Save the code string to the dictionary
                c_table_row.cells[1].text = c_line_analyzation_result.code

            # If it was the end message,
            else :  # dLineAnalyzeResult['lineType'] == MISRA_LINE_TYPE_END
                # Check if dHtmlRowInfo exists
                if 'c_table_row' not in locals():
                    # Not exists.
                    # This means it hasn't received violation message yet.
                    # Skip and check next line
                    continue

                # Save rule index into the local variable
                rule_idx = c_table_row.cells[2].text

                # If it was the advisory violation,
                if self.__misra_rule[rule_idx]['Type'] == 'Advisory' :
                    # Increment the counter
                    advisory_deviation_count += 1
                    # Set the background color of the html table row as
                    # 'advisory color'
                    c_table_row.background_color = self._MisraReportColor.ADVISORY.value

                # If it was the required violation,
                elif self.__misra_rule[rule_idx]['Type'] == 'Required' :
                    # Increment the counter
                    required_deviation_count += 1
                    # Set the background color of the html table row as
                    # 'required color'
                    c_table_row.background_color = self._MisraReportColor.REQUIRED.value

                # If it was the mandatory violation,
                else:  # self.__dMisraRule[ruleIdx]['Type'] == 'Mandatory'
                    # Increment the counter
                    mandatory_deviation_count += 1
                    # Set the background color of the html table row as
                    # 'mandatory color'
                    c_table_row.background_color = self._MisraReportColor.MANDATORY.value

                # Append a row of html detailed table according to the private
                # variable
                self.__deviation_table[file_path].append(c_table_row)

                # Delete the dictionary
                del c_table_row

        # Save the counts in the private variables
        self.__advisory_deviation_count  = advisory_deviation_count
        self.__required_deviation_count  = required_deviation_count
        self.__mandatory_deviation_count = mandatory_deviation_count

    def make_html_report(self, out_html_path:str):
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
        report_html.output_html(4, out_html_path)


if __name__ == '__main__':

    code_path    = sys.argv[1]
    out_file_path = sys.argv[2]

    reporter = MisraCheckReporter(code_path)

    # At first, load the Misra C rule information
    reporter.get_misra_rule_dictionary()

    # CppCheck starts. And save the results in the private variable
    reporter.cpp_check()

    # Output the report as html style
    reporter.make_html_report(out_file_path)
