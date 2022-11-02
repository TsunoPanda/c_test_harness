import sys
import json
import subprocess
import re
import dataclasses
from enum import Enum
from typing import List
from typing import Dict
from easy_html import *

class MisraCheckReporter:
    __MISRA_C_2012_RULE_FILE = 'misra_c_2012_rules.json'
    __CPPCHECK_COMMAND       = 'cppcheck --addon=misra.py'

    class __MISRA_LINE_TYPE(Enum):
        # Violation Type
        VIOLATION = 0
        # Violation Code or any string other than cppcheck result message.
        CODE      = 1
        # End
        END       = 2

    class __MISRA_REPORTER_COLOR(Enum):
        TABLE_TOP      = '#A1C3E7'
        TABLE_TOP_FONT = '#FFFFFF'
        ADVISORY       = '#CCDFEF'
        REQUIRED       = '#F8E9D1'
        MANDATORY      = '#F18D1D'

    @dataclasses.dataclass
    class __LineInfo:
        # MISRA_LINE_TYPE_VIOLATION or MISRA_LINE_TYPE_CODE or MISRA_LINE_TYPE_END
        lineType:        int             = None

        # Path to the file where the violation was found
        filePath:        str             = None

        # Line where the violation was found
        violationLine:   int             = None

        # Column where the violation was found
        violationColumn: int             = None

        # Description of the rule which was violated
        ruleMsg:         str             = None

        # Index of the rule
        ruleIdx:         str             = None

        # The code which violates the rule
        code:            str             = None

    def __init__(self, codePath:str):
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
        self.__dMisraRule: Dict[str, Dict[str, str]] = {}

        # A dictionary. key is the file path. and the value is
        # a list to the 'table_row' which contains violation
        # information
        # file_path : [
        #    table_row1,
        #    table_row2,
        #    ....
        # ]
        self.__dViolationTable: Dict[str, List[table_row]] = {}

        # Violation amount of type 'advisory'
        self.__advCnt:int = 0

        # Violation amount of type 'required'
        self.__reqCnt:int = 0

        # Violation amount of type 'mandatory'
        self.__manCnt:int = 0

        self.__product_code_path:str = codePath


    def __ExecuteCppcheckMisra(self):
        """Executes a command which checks product codes

        This method executes cppcheck command and return the result message
        as a line by line list.

        Returns:
             A list which contains lines of the result message of the cppcheck

         """

        # Make the Cppcheck command
        cmd = self.__CPPCHECK_COMMAND + ' ' + self.__product_code_path

        # Execute the command and get the output as binary
        wholeMsgByte = subprocess.check_output(cmd,
                                               stderr=subprocess.STDOUT,
                                               shell=False)

        # Convert the binary into string
        wholeMsg = wholeMsgByte.decode()

        # Split the string line by line into a list
        lWholeMsg = wholeMsg.splitlines()

        # Return the list
        return lWholeMsg

    def __AnalyzeMessageLine(self, lineStr:str):
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
        matchResult = re.match(pattern, lineStr)

        # If the match result is NOT None, it is violation message
        isViolationMessage = (matchResult is not None)

        # Remove all space to check if it is the type end
        lineWithoutSpace = lineStr.replace(' ', '')

        # If only '^' is remained, it is the type end
        isMsgEndLine = (lineWithoutSpace == '^')

        # Define the return dictionary
        cLineInfo = self.__LineInfo()

        # If it was the type violation
        if isViolationMessage is True:
            # Catch the violation information
            cLineInfo.lineType        = self.__MISRA_LINE_TYPE.VIOLATION
            cLineInfo.filePath        = matchResult.group(1)
            cLineInfo.violationLine   = matchResult.group(2)
            cLineInfo.violationColumn = matchResult.group(3)
            cLineInfo.ruleMsg         = matchResult.group(4)
            cLineInfo.ruleIdx         = matchResult.group(5)
            cLineInfo.code = None
        # If it was the type end,
        elif isMsgEndLine is True:
            # No information to return. just return the type end
            cLineInfo.lineType        = self.__MISRA_LINE_TYPE.END
            cLineInfo.filePath        = None
            cLineInfo.violationLine   = None
            cLineInfo.violationColumn = None
            cLineInfo.ruleMsg         = None
            cLineInfo.ruleIdx         = None
            cLineInfo.code            = None
        # If it was the type code.
        else:
            # Note: Any strings other than cppcheck result message
            #       will reach here.
            # Catch the code string
            cLineInfo.lineType        = self.__MISRA_LINE_TYPE.CODE
            cLineInfo.filePath        = None
            cLineInfo.violationLine   = None
            cLineInfo.violationColumn = None
            cLineInfo.ruleMsg         = None
            cLineInfo.ruleIdx         = None
            cLineInfo.code            = lineStr

        # Return the result
        return cLineInfo

    def __AppendTopRowOfSummaryTable(self, table:EasyHtml, type:str, count:str):
        """Appends the top row of the summary table
        """
        top_row = table_row(
            bgColor  = self.__MISRA_REPORTER_COLOR.TABLE_TOP.value,
            fontSize = 17,
            lCells   = [
                table_cell(text = type),
                table_cell(text = count),
            ],
        )
        table.CreateTableRow(top_row)

    def __AppendRowOfSummaryTable(self, table:EasyHtml, type:str, count:str, color:str):
        """Appends a row of the summary table
        """

        row = table_row(
            bgColor  = color,
            fontSize = 14,
            lCells   = [
                table_cell(text = type),
                table_cell(text = count),
            ],
        )
        row = table.CreateTableRow(row)

    def __MakeReportSummarySection(self, reportHtml:EasyHtml):
        """Makes a summary table on the html

        This method makes a summary table on the input html object
        as referring the counters of the violations in private data.

        """

        # Make Summary section
        reportHtml.SetBodyH2('Summary', 'center')

        # Create Summary table
        summary_table = reportHtml.CreateTable(5, 'center', '50%')

        # Append the top row to the table
        self.__AppendTopRowOfSummaryTable(summary_table,
                                          'Type',
                                          'Violation count')

        # Append the advisory violation count row to the table
        self.__AppendRowOfSummaryTable(summary_table,
                                       'Advisory',
                                       str(self.__advCnt),
                                       self.__MISRA_REPORTER_COLOR.ADVISORY.value)

        # Append the required violation row to the table
        self.__AppendRowOfSummaryTable(summary_table,
                                       'Required',
                                       str(self.__reqCnt),
                                       self.__MISRA_REPORTER_COLOR.REQUIRED.value)

        # Append the mandatory violation row to the table
        self.__AppendRowOfSummaryTable(summary_table,
                                       'Mandatory',
                                       str(self.__manCnt),
                                       self.__MISRA_REPORTER_COLOR.MANDATORY.value)

    def __MakeReportDetailedSection(self, reportHtml:EasyHtml):
        """Makes the detailed table on the html

        This method makes the detailed table on the input html object as
        referring the violation information captured from cppcheck

        """

        # List of the top row of the table
        color = self.__MISRA_REPORTER_COLOR.TABLE_TOP_FONT.value
        top_row = table_row(
            bgColor  = self.__MISRA_REPORTER_COLOR.TABLE_TOP.value,
            fontSize = 17,
            lCells   =
            [
                table_cell('Line',       color, '', '4%'),
                table_cell('Code',       color, '', '30%'),
                table_cell('Rule Index', color, '', '4%'),
                table_cell('Rule',       color, '', '50%'),
                table_cell('Type',       color, '', '6%'),
                table_cell('Decidable',  color, '', '6%'),
            ],)

        # Append all the detailed violation message to the table
        for filePath in sorted(self.__dViolationTable) :

            # Make detailed report table
            reportHtml.SetBodyH2('Violation Report: ' + filePath, 'center')
            # Make detailed report table
            detailed_table = reportHtml.CreateTable(5, 'center', '95%')
            detailed_table.CreateTableRow(top_row)

            # Add all rows of the violation information
            for row in self.__dViolationTable[filePath]:
                detailed_table.CreateTableRow(row)

    def __SortViolationTable(self):
        """Sorts the violation table by code line
        """
        def sort_key(table_row):
            return table_row.lCells[0].text.zfill(10)

        for key in self.__dViolationTable:
            self.__dViolationTable[key] = sorted(self.__dViolationTable[key],
                                                 key = sort_key)

    def GetMisraRuleDictionary(self):
        """Gets Misra rule dictionary

        This method reads the json file which contains MISRA C 2012 rule
        information. And saves the rule information as a dictionary type data
        into a instance variable __dMisraRule
         """

        # Open the json file which contains MISRA C 2012 rule information
        misraRuleRawJson = open(self.__MISRA_C_2012_RULE_FILE, 'r')

        # Load the json file and save it into a dictionary data
        self.__dMisraRule = json.load(misraRuleRawJson)

    def CppCheck(self):
        """Executes the cppcheck and analyze the result message

        This method executes the cppcheck. And receives
        the output message of the check and analyzes it.
        The analyze result will be stored into the private
        dictionary variable

        """

        # Counter of advisory violations
        advisoryViolationCount  = 0

        # Counter of required violations
        requiredViolationCount  = 0

        # Counter of mandatory violations
        mandatoryViolationCount = 0

        # Execute the cppcheck(misra.py) and get the result as a list of
        # message line
        lWholeMsg = self.__ExecuteCppcheckMisra()

        # Analyze the cppcheck result message line by line
        for line in lWholeMsg:

            # Analyze the line and get the information
            # cLineAnalyzeResult: _LineInfo
            cLineAnalyzeResult = self.__AnalyzeMessageLine(line)

            # If it was the violation message,
            if cLineAnalyzeResult.lineType == self.__MISRA_LINE_TYPE.VIOLATION:
                # Create a dictionary which contains the html detailed row
                # table data

                # Save the file path
                filePath = cLineAnalyzeResult.filePath

                # Get the violation information
                ruleIdx = cLineAnalyzeResult.ruleIdx
                rule = self.__dMisraRule[ruleIdx]['Rule']
                type = self.__dMisraRule[ruleIdx]['Type']
                decidable = self.__dMisraRule[ruleIdx]['Decidable']

                if filePath not in self.__dViolationTable:
                    self.__dViolationTable[filePath] = []

                cTableRow = table_row(
                    bgColor = '',  # will be assigned later
                    fontSize = 14,
                    lCells =
                    [
                        table_cell(cLineAnalyzeResult.violationLine),
                        # Cell for code. will be assigned later
                        table_cell(align = 'left'),
                        table_cell(cLineAnalyzeResult.ruleIdx),
                        table_cell(rule, align = 'left'),
                        table_cell(type),
                        table_cell(decidable),
                    ],)

            # If it was the code message,
            # (or any other string than cppcheck result message)
            elif cLineAnalyzeResult.lineType == self.__MISRA_LINE_TYPE.CODE:
                # Check if dHtmlRowInfo exists
                if 'cTableRow' not in locals():
                    # Not exists.
                    # This means it hasn't received violation message yet.
                    # Skip and check next line
                    continue

                # Save the code string to the dictionary
                cTableRow.lCells[1].text = cLineAnalyzeResult.code

            # If it was the end message,
            else :  # dLineAnalyzeResult['lineType'] == MISRA_LINE_TYPE_END
                # Check if dHtmlRowInfo exists
                if 'cTableRow' not in locals():
                    # Not exists.
                    # This means it hasn't received violation message yet.
                    # Skip and check next line
                    continue

                # Save rule index into the local variable
                ruleIdx = cTableRow.lCells[2].text

                # If it was the advisory violation,
                if self.__dMisraRule[ruleIdx]['Type'] == 'Advisory' :
                    # Increment the counter
                    advisoryViolationCount += 1
                    # Set the background color of the html table row as
                    # 'advisory color'
                    cTableRow.bgColor = self.__MISRA_REPORTER_COLOR.ADVISORY.value

                # If it was the required violation,
                elif self.__dMisraRule[ruleIdx]['Type'] == 'Required' :
                    # Increment the counter
                    requiredViolationCount += 1
                    # Set the background color of the html table row as
                    # 'required color'
                    cTableRow.bgColor = self.__MISRA_REPORTER_COLOR.REQUIRED.value

                # If it was the mandatory violation,
                else:  # self.__dMisraRule[ruleIdx]['Type'] == 'Mandatory'
                    # Increment the counter
                    mandatoryViolationCount += 1
                    # Set the background color of the html table row as
                    # 'mandatory color'
                    cTableRow.bgColor = self.__MISRA_REPORTER_COLOR.MANDATORY.value

                # Append a row of html detailed table according to the private
                # variable
                self.__dViolationTable[filePath].append(cTableRow)

                # Delete the dictionary
                del cTableRow

        # Save the counts in the private variables
        self.__advCnt        = advisoryViolationCount
        self.__reqCnt        = requiredViolationCount
        self.__manCnt        = mandatoryViolationCount

    def MakeHtmlReport(self, outFilePath:str):
        """Makes a html report

        This method makes a html report as referring the previous
        cppcheck result

        """
        # Sort the violation information by line
        self.__SortViolationTable()
        # Make reporting html file
        reportHtml = EasyHtml()

        # Set title
        reportHtml.SetTitle('Misra C 2012 Check Result')

        # Set body title
        reportHtml.SetBodyH1('Misra C 2012 Check Result', 'center')

        # Make summary section
        self.__MakeReportSummarySection(reportHtml)

        # Make detailed report section
        self.__MakeReportDetailedSection(reportHtml)

        # output the html
        reportHtml.OutputHtml(4, outFilePath)


if __name__ == '__main__':

    codePath    = sys.argv[1]
    outFilePath = sys.argv[2]

    reporter = MisraCheckReporter(codePath)

    # At first, load the Misra C rule information
    reporter.GetMisraRuleDictionary()

    # CppCheck starts. And save the results in the private variable
    reporter.CppCheck()

    # Output the report as html style
    reporter.MakeHtmlReport(outFilePath)