from typing import List
from dataclasses import dataclass, field

class EasyHtml:

    def __init__(self, tag = 'html'):
        self.tag      = tag
        self.opt      = None
        self.text     = None
        self.children = None

    def __SetOption(self, option):
        self.opt = option

    def __SetText(self, text):
        self.text = text

    def __CreateChild(self, tag):

        if self.children is None:
            self.children = []

        child = EasyHtml(tag)
        self.children.append(child)

        return (child)

    def __GetBody(self):
        for child in self.children:
            if child.tag == 'body':
                return child
        return self.__CreateChild('body')

    def __DumpDataAsHtml(self, fileHandle, indent, space = ""):
        if self.opt is None:
            fileHandle.write(space + '<' + self.tag + '>' + "\n")
        else:
            fileHandle.write(space + '<' + self.tag + ' ' + self.opt + '>' + "\n")

        nextSpace = space + (" " * indent)

        if self.text:
            fileHandle.write(nextSpace + self.text + "\n")

        if self.children is not None:
            for dChild in self.children:
                dChild.__DumpDataAsHtml(fileHandle, indent, nextSpace)

        fileHandle.write(space + '</' + self.tag + '>' + "\n")

    def SetTitle(self, text):
        head = self.__CreateChild('head')
        title = head.__CreateChild('title')
        title.__SetText(text)

    def SetBodyH1(self, text, align):
        body = self.__GetBody()
        h1_title = body.__CreateChild('h1')
        h1_title.__SetOption('align = ' + align)
        h1_title.__SetText(text)

    def SetBodyH2(self, text, align):
        body = self.__GetBody()
        h2_title = body.__CreateChild('h2')
        h2_title.__SetOption('align = ' + align)
        h2_title.__SetText(text)

    def SetBodyH3(self, text, align):
        body = self.__GetBody()
        h2_title = body.__CreateChild('h3')
        h2_title.__SetOption('align = ' + align)
        h2_title.__SetText(text)

    def CreateTable(self, border, align = '', width = ''):
        body = self.__GetBody()
        table = body.__CreateChild('table')
        optionStr = 'border = "' + str(border) + '"'
        if align != '':
            optionStr += (' align = ' + align)
        if width != '':
            optionStr += (' width = "' + width + '"')
        table.__SetOption(optionStr)
        return table

    def CreateBlankTableRow(self, bgColor, fontSize):
        tableRow = self.__CreateChild('tr')
        optionStr  = 'bgcolor = ' + bgColor
        optionStr += ' style="font-size: ' + str(fontSize) + 'pt"'
        tableRow.__SetOption(optionStr)
        return tableRow

    def CreateTableRow(self, c_table_row):
        tableRow = self.__CreateChild('tr')
        optionStr  = 'bgcolor = ' + c_table_row.bgColor
        optionStr += ' style="font-size: ' + str(c_table_row.fontSize) + 'pt"'
        tableRow.__SetOption(optionStr)

        for cell in c_table_row.lCells:
            tableRow.CreateTableCell(cell.text,
                                     cell.fontColor,
                                     cell.align,
                                     cell.width)
        return tableRow

    def CreateTableCell(self, text,
                        fontColor = '#000000', align = '', width = ''):
        cell = self.__CreateChild('th')
        optionStr = ''
        if align != '':
            optionStr += (' align = ' + align)
        if width != '':
            optionStr += (' width = "' + width + '"')
        cell.__SetOption(optionStr)
        cell_font = cell.__CreateChild('font')
        cell_font.__SetOption('color =' + fontColor)
        cell_font.__SetText(text)

    def OutputHtml(self, indent, filePath):
        fileHandle = open(filePath, 'w')
        fileHandle.write('<!DOCTYPE html>' + "\n")
        self.__DumpDataAsHtml(fileHandle, indent)

@dataclass
class table_cell:
    text:str      = ''
    fontColor:str = '#000000'
    align:str     = ''
    width:str     = ''

@dataclass
class table_row:
    bgColor:str  = '#000000'
    fontSize:str = '1'
    lCells:List[table_cell] = field(default_factory = list)


if __name__ == '__main__':
    testHtml = EasyHtml()
    testHtml.SetTitle('this is the title')
    testHtml.SetBodyH1('this is the body highlight 1', 'center')
    testHtml.SetBodyH2('this is the body highlight 2', 'center')
    testHtml.SetBodyH3('this is the body highlight 3', 'center')

    # Create a table
    table = testHtml.CreateTable(5, 'center', '50%')

    top_row = table_row(
        bgColor  = '#FFFFFF',
        fontSize = 17,
        lCells   =
        [
            table_cell(text = 'this is first cell'),
            table_cell(text = 'this is second cell'),
        ],)
    table.CreateTableRow(top_row)

    second_row = table_row(
        bgColor  = '#00AA00',
        fontSize = 17,
        lCells   =
        [
            table_cell(text = 'this is first cell of second row',
                       fontColor = '#FFFFFF'),
            table_cell(text = 'this is second cell of second row',
                       fontColor = '#FFFFFF'),
        ],)
    table.CreateTableRow(second_row)

    testHtml.OutputHtml(4, 'test.html')