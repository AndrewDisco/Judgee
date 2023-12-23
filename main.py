import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox, QTextEdit, QTableWidget, QTableWidgetItem, QHeaderView, QHBoxLayout, QPlainTextEdit
from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QTextCursor, QTextBlockUserData, QColor, QFont, QPainter, QTextFormat
from PyQt5.QtCore import Qt, pyqtSlot, QRegularExpression, QRect
from PyQt5 import QtGui
import subprocess
import time
import os
import qdarktheme
 
class QCodeEditor(QPlainTextEdit):
    class NumberBar(QWidget):
        def __init__(self, editor):
            QWidget.__init__(self, editor)
            
            self.editor = editor
            self.editor.blockCountChanged.connect(self.updateWidth)
            self.editor.updateRequest.connect(self.updateContents)
            self.font = QFont()
            self.numberBarColor = QColor("#49494A")
                     
        def paintEvent(self, event):
            
            painter = QPainter(self)
            painter.fillRect(event.rect(), self.numberBarColor)
             
            block = self.editor.firstVisibleBlock()
 
            # Iterate over all visible text blocks in the document.
            while block.isValid():
                blockNumber = block.blockNumber()
                block_top = int(self.editor.blockBoundingGeometry(block).translated(self.editor.contentOffset()).top())
 
                # Check if the position of the block is out side of the visible area.
                if not block.isVisible() or block_top >= event.rect().bottom():
                    break
 
                # We want the line number for the selected line to be bold.
                if blockNumber == self.editor.textCursor().blockNumber():
                    self.font.setBold(True)
                    painter.setPen(QColor("#2D74E6"))
                else:
                    self.font.setBold(False)
                    painter.setPen(QColor("#8ab4f7"))
                painter.setFont(self.font)
                
                # Draw the line number right justified at the position of the line.
                paint_rect = QRect(0, block_top, self.width(), self.editor.fontMetrics().height())
                painter.drawText(paint_rect, Qt.AlignRight, str(blockNumber+1))
 
                block = block.next()
 
            painter.end()
            
            QWidget.paintEvent(self, event)
 
        def getWidth(self):
            count = self.editor.blockCount()
            width = self.fontMetrics().width(str(count)) + 8
            return width      
        
        def updateWidth(self):
            width = self.getWidth()
            if self.width() != width:
                self.setFixedWidth(width)
                self.editor.setViewportMargins(width, 0, 0, 0);
 
        def updateContents(self, rect, scroll):
            if scroll:
                self.scroll(0, scroll)
            else:
                self.update(0, rect.y(), self.width(), rect.height())
            
            if rect.contains(self.editor.viewport().rect()):   
                fontSize = self.editor.currentCharFormat().font().pointSize()
                self.font.setPointSize(fontSize)
                self.font.setStyle(QFont.StyleNormal)
                self.updateWidth()
                
        
    def __init__(self, DISPLAY_LINE_NUMBERS=True, HIGHLIGHT_CURRENT_LINE=True,
                 SyntaxHighlighter=None, *args):        
        '''
        Parameters
        ----------
        DISPLAY_LINE_NUMBERS : bool 
            switch on/off the presence of the lines number bar
        HIGHLIGHT_CURRENT_LINE : bool
            switch on/off the current line highliting
        SyntaxHighlighter : QSyntaxHighlighter
            should be inherited from QSyntaxHighlighter
        
        '''                  
        super(QCodeEditor, self).__init__()
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
                               
        self.DISPLAY_LINE_NUMBERS = DISPLAY_LINE_NUMBERS

        if DISPLAY_LINE_NUMBERS:
            self.number_bar = self.NumberBar(self)
            self.setViewportMargins(self.number_bar.getWidth(), 0, 0, 0)
            
        if HIGHLIGHT_CURRENT_LINE:
            self.currentLineNumber = None
            self.currentLineColor = QColor("#333539")
            self.cursorPositionChanged.connect(self.highligtCurrentLine)
        
        if SyntaxHighlighter is not None: # add highlighter to textdocument
           self.highlighter = SyntaxHighlighter(self.document())         
                 
    def resizeEvent(self, *e):
        '''overload resizeEvent handler'''
                
        if self.DISPLAY_LINE_NUMBERS:   # resize number_bar widget
            cr = self.contentsRect()
            rec = QRect(cr.left(), cr.top(), self.number_bar.getWidth(), cr.height())
            self.number_bar.setGeometry(rec)
        
        QPlainTextEdit.resizeEvent(self, *e)

    def highligtCurrentLine(self):
        newCurrentLineNumber = self.textCursor().blockNumber()
        if newCurrentLineNumber != self.currentLineNumber:                
            self.currentLineNumber = newCurrentLineNumber
            hi_selection = QTextEdit.ExtraSelection() 
            hi_selection.format.setBackground(self.currentLineColor)
            hi_selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            hi_selection.cursor = self.textCursor()
            hi_selection.cursor.clearSelection() 
            self.setExtraSelections([hi_selection])        


class CppSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(CppSyntaxHighlighter, self).__init__(parent)

        self.keywordFormat = QTextCharFormat()
        self.keywordFormat.setForeground(QColor("#569CD6"))
        self.keywordFormat.setFontWeight(QFont.Bold)

        self.operatorFormat = QTextCharFormat()
        self.operatorFormat.setForeground(QColor("#e8e2b7"))

        self.numberFormat = QTextCharFormat()
        self.numberFormat.setForeground(QColor("#B5CEA8"))

        self.stringFormat = QTextCharFormat()
        self.stringFormat.setForeground(QColor("#CE9178"))

        self.directiveFormat = QTextCharFormat()
        self.directiveFormat.setForeground(QColor("#D4D4D4"))

        keywords = [
            "alignas", "alignof", "and", "and_eq", "asm", "auto", "bitand", "bitor",
            "bool", "break", "case", "catch", "char", "class", "compl", "const",
            "constexpr", "const_cast", "continue", "decltype", "default", "delete",
            "do", "double", "dynamic_cast", "else", "enum", "explicit", "export",
            "extern", "false", "float", "for", "friend", "goto", "if", "inline",
            "int", "long", "mutable", "namespace", "new", "noexcept", "not", "not_eq",
            "nullptr", "operator", "or", "or_eq", "private", "protected", "public",
            "register", "reinterpret_cast", "return", "short", "signed", "sizeof",
            "static", "static_assert", "static_cast", "struct", "switch", "template",
            "this", "thread_local", "throw", "true", "try", "typedef", "typeid",
            "typename", "union", "unsigned", "using", "virtual", "void", "volatile",
            "wchar_t", "while", "xor", "xor_eq"
        ]
        
        self.rules = [
            (r'\b%s\b' % keyword, 0, self.keywordFormat) for keyword in keywords
        ] + [
            (r'(\+|\-|\*|\/|\%|==|!=|<|>|<=|>=|&&|\|\||\!|\?|\:|\=|\+=|\-=|\*=|\/=|\%=|\&=|\|=|\^=|<<|>>|<<=|>>=|\(|\)|\{|\}|\[|\])', 0, self.operatorFormat),
            (r'\b\d+\b', 0, self.numberFormat),  # Match numbers
            (r'"[^"]*"', 0, self.stringFormat),   # Match strings
            (r'#\w+', 0, self.directiveFormat),   # Match preprocessor directives
        ]

        self.multiLineCommentFormat = QTextCharFormat()
        self.multiLineCommentFormat.setForeground(QColor("#57A64A"))

        

    def highlightBlock(self, text):
        for pattern, nth, format in self.rules:
            expression = QRegularExpression(pattern)
            match_iterator = expression.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)

        self.setCurrentBlockUserData(None)
        self.matchMultilineComment(text, self.multiLineCommentFormat)

    def matchMultilineComment(self, text, format):
        startIndex = 0
        if self.previousBlockState() > 0:
            startIndex = self.previousBlockState()

        if startIndex == -1:
            startIndex = 0

        commentStart = text.find("/*", startIndex)
        while commentStart >= 0:
            commentEnd = text.find("*/", commentStart)
            if commentEnd == -1:
                self.setCurrentBlockState(commentStart)
                break
            else:
                commentLength = commentEnd - commentStart + 2
                self.setFormat(commentStart, commentLength, format)
                commentStart = text.find("/*", commentEnd + 2)

    def highlightCurrentLine(self):
        newCurrentLineNumber = self.textCursor().blockNumber()
        if newCurrentLineNumber != self.currentLineNumber:
            self.currentLineNumber = newCurrentLineNumber
            hi_selection = QTextEdit.ExtraSelection()
            hi_selection.format.setBackground(self.currentLineColor)
            hi_selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            hi_selection.cursor = self.textCursor()
            hi_selection.cursor.clearSelection()
            self.setExtraSelections([hi_selection])

    class CommentUserData(QTextBlockUserData):
        def __init__(self, endingIndex):
            super().__init__()
            self._endingIndex = endingIndex

        def endingIndex(self):
            return self._endingIndex

class CPPCheckerApp(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        title_label = QLabel("C++ Code:", self)
        layout.addWidget(title_label)

        # icon
        self.setWindowIcon(QtGui.QIcon('icon.png'))

        self.code_text = QCodeEditor(self)
        layout.addWidget(self.code_text)

        cppButtons = QHBoxLayout()

        browse_cpp_button = QPushButton("Browse CPP", self)
        browse_cpp_button.clicked.connect(self.browseCPP)
        cppButtons.addWidget(browse_cpp_button)

        self.remove_io_button = QPushButton("Remove IO", self)
        self.remove_io_button.clicked.connect(self.removeIO)
        cppButtons.addWidget(self.remove_io_button)

        layout.addLayout(cppButtons)

        mingw_label = QLabel("Mingw Path:", self)
        layout.addWidget(mingw_label)

        self.mingw_entry = QLineEdit(self)
        layout.addWidget(self.mingw_entry)

        mingw_button_layout = QHBoxLayout()

        mingw_browse_button = QPushButton("Browse", self)
        mingw_browse_button.clicked.connect(self.browseMingw)
        mingw_button_layout.addWidget(mingw_browse_button)

        mingw_autofind_button = QPushButton("Auto-Find", self)
        mingw_autofind_button.clicked.connect(self.autoFindMingw)
        mingw_button_layout.addWidget(mingw_autofind_button)

        layout.addLayout(mingw_button_layout)

        self.result_table = QTableWidget(0, 3)
        self.result_table.setHorizontalHeaderLabels(["Test No.", "Result", "Time Taken"])
        layout.addWidget(self.result_table)

        self.highlighter = CppSyntaxHighlighter(self.code_text.document())

        simple_check_button = QPushButton("Simple Check", self)
        simple_check_button.clicked.connect(self.simpleCheck)

        mass_check_button = QPushButton("Mass Check", self)
        mass_check_button.clicked.connect(self.massCheck)

        # use qboxlayout for mass check/ simple check buttons
        check_button_layout = QHBoxLayout()

        check_button_layout.addWidget(simple_check_button)
        check_button_layout.addWidget(mass_check_button)

        layout.addLayout(check_button_layout)

        # make the table to be the width of the box
        header = self.result_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        #make the table text noon editable
        self.result_table.setEditTriggers(QTableWidget.NoEditTriggers)

        #make text color black
        self.result_table.setStyleSheet("color: black")

        self.setLayout(layout)
        self.setGeometry(100, 100, 600, 400)
        self.setWindowTitle('Judgee 0.3')
        self.show()

    @pyqtSlot()
    def simpleCheck(self):
        cpp_code = self.code_text.toPlainText()
        mingw_path = self.mingw_entry.text()
        in_file = QFileDialog.getOpenFileName(self, "Select IN file")[0]
        out_file = QFileDialog.getOpenFileName(self, "Select OUT file")[0]

        if not in_file or not out_file:
            self.showError("Error: Please select both IN and OUT files.")
            return

        # Save the CPP code to a temporary file
        with open('temp.cpp', 'w') as f:
            f.write(cpp_code)

        # Compile the C++ code first
        compile_command = f'"{mingw_path}/g++.exe" -o temp.exe temp.cpp'

        try:
            subprocess.run(compile_command, shell=True, timeout=10, check=True)
        except subprocess.CalledProcessError:
            print("Compilation failed.")
            return
        
        # Run the compiled executable with the input file & get the output
        command = f'temp.exe < "{in_file}" > temp.out'
        
        try:
            start_time = time.time()
            result = subprocess.run(command, shell=True, timeout=10, check=True)
            end_time = time.time()
            with open('temp.out', 'r') as f:
                output = f.read()
            print(f'Output: {output}')
        except subprocess.TimeoutExpired:
            self.showResult('Failed', 'Timeout')
            return
        
        # Compare the output to the expected output
        with open(out_file, 'r') as f:
            expected_output = f.read()

        elapsed_time = end_time - start_time
        if output == expected_output:
            self.showResult('Passed', f'{elapsed_time:.2f}s')
        else:
            self.showResult('Failed', f'{elapsed_time:.2f}s')

    @pyqtSlot()
    def massCheck(self):
        cpp_code = self.code_text.toPlainText()
        mingw_path = self.mingw_entry.text()
        folder_path = QFileDialog.getExistingDirectory(self, "Select Test Folder")

        if not folder_path:
            self.showError("Error: Please select a test folder.")
            return
        
        # Save the CPP code to a temporary file
        with open('temp.cpp', 'w') as f:
            f.write(cpp_code)

        test_results = []

        # Compile the C++ code first
        compile_command = f'"{mingw_path}/g++.exe" -o temp.exe temp.cpp'
        try:
            subprocess.run(compile_command, shell=True, timeout=10, check=True)
        except subprocess.CalledProcessError:
            print("Compilation failed.")
            return

        for file in os.listdir(folder_path):
            if file.endswith(".in"):
                test_number = file.split('.')[0]
                in_file = f'{folder_path}/{test_number}.in'
                out_file = f'{folder_path}/{test_number}.out'

                # Run the compiled executable with the input file & get the output
                command = f'temp.exe < "{in_file}" > temp.out'
                print(command)
                try:
                    start_time = time.time()
                    result = subprocess.run(command, shell=True, timeout=10, check=True)
                    end_time = time.time()
                    with open('temp.out', 'r') as f:
                        output = f.read()
                    print(f'Test {test_number}: {output}')
                except subprocess.TimeoutExpired:
                    test_results.append({'Test No.': test_number, 'Result': 'Failed', 'Time Taken': 'Timeout'})
                    continue

                # Compare the output to the expected output
                with open(out_file, 'r') as f:
                    expected_output = f.read().strip()

                elapsed_time = end_time - start_time
                if output == expected_output:
                    test_results.append({'Test No.': test_number, 'Result': 'Passed', 'Time Taken': f'{elapsed_time:.2f}s'})
                else:
                    test_results.append({'Test No.': test_number, 'Result': 'Failed', 'Time Taken': f'{elapsed_time:.2f}s'})

        self.updateTable(test_results)
    
    def updateTable(self, test_results):
        self.result_table.setRowCount(len(test_results))
        for i, test_result in enumerate(test_results):
            self.result_table.setItem(i, 0, QTableWidgetItem(str(test_result['Test No.'])))
            self.result_table.setItem(i, 1, QTableWidgetItem(test_result['Result']))
            self.result_table.setItem(i, 2, QTableWidgetItem(test_result['Time Taken']))
    
            if test_result['Result'] == 'Passed':
                self.result_table.item(i, 0).setBackground(QColor(0, 255, 0))
                self.result_table.item(i, 1).setBackground(QColor(0, 255, 0))
                self.result_table.item(i, 2).setBackground(QColor(0, 255, 0))
            else:
                self.result_table.item(i, 0).setBackground(QColor(255, 0, 0))
                self.result_table.item(i, 1).setBackground(QColor(255, 0, 0))
                self.result_table.item(i, 2).setBackground(QColor(255, 0, 0))
    
    @pyqtSlot()
    def browseMingw(self):
        mingw_path = QFileDialog.getExistingDirectory(self, "Select MinGW Folder")
        if not mingw_path:
            self.showError("Error: Please select a MinGW folder.")
            return
        self.mingw_entry.setText(mingw_path)

    @pyqtSlot()
    def autoFindMingw(self):
        possible_paths = [
            'C:/Program Files/CodeBlocks/MinGW/bin',
            'C:/Program Files/CodeBlocks/MinGW64/bin',
            'C:/Program Files (x86)/CodeBlocks/MinGW/bin',
            'C:/Program Files (x86)/CodeBlocks/MinGW64/bin',
            'C:/Program Files (x86)/Dev-Cpp/MinGW64/bin',
            'C:/Program Files (x86)/Dev-Cpp/MinGW32/bin',
            'C:/Program Files (x86)/Dev-Cpp/MinGW/bin',
            'C:/Program Files (x86)/Dev-Cpp/MinGW64/bin',
            ]
        for path in possible_paths:
            if os.path.exists(path):
                self.mingw_entry.setText(path)
                break
            else:
                self.showError("Could not auto-find MinGW. Please select the path manually.")


    @pyqtSlot()
    def browseCPP(self):
        cpp_code, _ = QFileDialog.getOpenFileName(self, "Select CPP file", filter="C++ Files (*.cpp)")
        if not cpp_code:
            self.showError("Error: Please select a CPP file.")
            return
        with open(cpp_code, 'r') as f:
            self.code_text.setPlainText(f.read())

    def showError(self, message):
        QMessageBox.critical(self, "Error", message)

    def showResult(self, result, time_taken):
        QMessageBox.information(self, "Result", f'Test {result}! Time Taken: {time_taken}')

    @pyqtSlot()
    def removeIO(self):
        cpp_code = self.code_text.toPlainText()
        lines = cpp_code.split('\n')
        read_line = ""
        output_line = ""
        read_variable = ""
        output_variable = ""

        for line in lines:
            if "ifstream" in line:
                read_line = line
                read_variable = line.split(' ')[1].split('(')[0]
            if "ofstream" in line:
                output_line = line
                output_variable = line.split(' ')[1].split('(')[0]
            
        if read_line == "" or output_line == "":
            self.showError("Error: Could not find input/output lines. \nDoes your code use ifstream/ofstream?")
            return
        
        cpp_code = cpp_code.replace(read_line, "")
        cpp_code = cpp_code.replace(output_line, "")
        cpp_code = f'#define cin {read_variable}\n#define cout {output_variable}\n' + cpp_code
        self.code_text.setPlainText(cpp_code)
        self.highlighter = CppSyntaxHighlighter(self.code_text.document())

if __name__ == '__main__':
    qdarktheme.enable_hi_dpi()
    app = QApplication(sys.argv)
    qdarktheme.setup_theme()
    ex = CPPCheckerApp()
    sys.exit(app.exec_())
