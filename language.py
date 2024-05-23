class language:

    def __init__(self, code):
        self.jumpLine = 0
        self.operons = ['+', '-', '*', '/']
        self.conditionals = ['>', '<', '>=', '<=', '==', '!=', 'and', 'or', 'not']
        self.codeSplitLinePos = []
        self.code = code
        self.lineToParse = 0
        self.codeSplit = []
        # code with empty lines (to keep track of call location)
        self.rawCode = []
        self.indentData = []
        self.vars = {}
        self.split()
        self.parse(self.rawCode)
        self.currentLine = 0

    @staticmethod
    def error(message):
        print("! " + message + " !")
        quit()

    def listVars(self):
        toList = self.vars.keys()
        toList = str(toList)
        toList = toList.replace("dict_keys([", '')
        toList = toList.replace("'", '')
        toList = toList.replace("])", '')
        print("Variables: " + toList)

    def listVarVals(self):
        toList = self.vars.values()
        toList = str(toList)
        toList = toList.replace("dict_keys([", '')
        toList = toList.replace("'", '')
        toList = toList.replace("])", '')
        print("(Work On More) Values: " + toList)

    def split(self):
        codeToSplit = self.code.split("\n")

        for i, val in enumerate(codeToSplit):
            lines = val.split("\n")

            for line in lines:
                numSpaces = len(line)-len(line.lstrip())
                if line.startswith("//"):
                    line = line.lstrip("\n")

                lineData = [line, i]
                self.indentData.append(int(numSpaces/4))
                self.rawCode.append(lineData)


    def clean(self):
        codeToClean = self.codeSplit
        cleanedCode = []
        # keeping track of line pos for debug
        cleanedCodeLinePos = []

        for val in range(len(codeToClean)):
            if codeToClean[val] != '':
                cleanedCode.append(codeToClean[val])
                cleanedCodeLinePos.append(val + 1)
        self.codeSplit = cleanedCode
        self.codeSplitLinePos = cleanedCodeLinePos

    # added code param, so I can choose the code to parse
    # added startLinePos to keep track of line pos in loops
    def parse(self, code, startLinePos=0):
        for task in code:
            self.currentLine = task[1]+1
            task[0] = task[0].lstrip()
            if self.jumpLine != 0:
                self.jumpLine -= 1
            elif task[0] != "":
                # semicolons
                if task[0].endswith(";"):
                    task[0] = task[0].rstrip(";")
                # print
                if task[0].startswith("print"):
                    start_index = task[0].find("(")
                    end_index = task[0].find(")")
                    if start_index != -1 and end_index != -1:
                        # Extract content between parentheses
                        content = task[0][start_index + 1:end_index]

                        self.printUtils(content)
                # comment
                elif task[0].startswith("//"):
                    pass
                # create variables
                elif task[0].startswith("make"):
                    self.createVar(task)
                # write to variables
                elif task[0].startswith("set"):
                    self.setVar(task)
                # delete variables (bcuz why not)
                elif task[0].startswith("del"):
                    self.delVar(task)
                # loop
                elif task[0].startswith("loop"):
                    self.loopFunc(task)
                #conditional
                elif task[0].startswith("if"):
                    self.conditional(task[0])
                # input
                elif task[0].startswith("input"):
                    start_index = task[0].find("(")
                    end_index = task[0].find(")")
                    if start_index != -1 and end_index != -1:
                        # Extract content between parentheses
                        content = task[0][start_index + 1:end_index]
                        split = content.split(',', 1)

                        varName = split[0]

                        question = split[1]
                        question = question.replace('"', '')
                        question = question.replace(' ', '', 1)

                        varValue = input(question + "\n")

                        varToCreate = ["make " + varName + ' = "' + varValue + '"', task[1]]

                        self.createVar(varToCreate)
                # blank line
                elif task[0] == "blank()" or task[0] == "nl()" or task[0] == "el()":
                    print("")
                # debug methods
                elif task[0].startswith("rh."):
                    task[0] = task[0].replace("rh.", '')
                    self.debug(task)
                # error
                elif not task[0].isspace():
                    language.error(f"Unknown Task | Task: {task[0]} | Line: {self.currentLine}")

    def evaluateVar(self, content):
        # handling var types in python, maybe change later if feel like :|
        varType = "NaN"
        # see if it's an existing var
        if content in self.vars:
            varType = self.vars[content][1]
            content = self.vars[content][0]

        # str detection
        if varType == "NaN" and content.startswith('"') and content.endswith('"'):
            varType = "str"
            content = content[1:-1]

        # checking if num is neg and getting rid of neg for simplicity
        if varType == "NaN" and content.startswith('-') and content[1:].isdigit():
            content = content.replace('-', '')
            isNeg = True
        else:
            isNeg = False

        if varType == "NaN" and content.count('.') == 1:
            varType = "float"
            if isNeg:
                content = '-' + content
            content = float(content)

        if varType == "NaN" and content.isdigit():
            varType = "int"
            if isNeg:
                content = '-' + content
            content = int(content)

        if varType == "NaN":
            return "error"

        return content, varType

    def createVar(self, task):
        taskContent = task[0]

        taskContent = taskContent.replace('make', '', 1)
        # find index of var content using "=" char

        declarationIndex = taskContent.index("=")
        # grab content of var (cuts at declarationIndex)
        varContent = taskContent[declarationIndex + 1:].strip()
        # grab name of var (cuts before declarationIndex)
        varName = taskContent[:declarationIndex].strip()

        varEval = self.evaluateVar(varContent)
        if varEval == "error":
            language.error(f"Incorrect var declaration | Var: {varName} | Line: {self.currentLine}")
        # creating var key in vars dictionary
        self.vars[varName] = varEval

    # write existing variable to new val
    def setVar(self, task):
        # again letting python handle the operation :(
        taskContent = task[0]
        taskContent = taskContent.replace('set', '', 1)
        # find index of var content using "=" char
        declarationIndex = taskContent.index("=")
        # grab content of var (cuts at declarationIndex)
        varContent = taskContent[declarationIndex + 1:].strip()
        # grab name of var (cuts before declarationIndex)
        varName = taskContent[:declarationIndex].strip()

        if not (varName in self.vars):
            language.error(f"Var does not exist | Var: {varName} | Line: {self.currentLine}")

        if varContent.startswith("calc"):
            self.vars[varName] = self.calcVar(varContent)
        else:
            varEval = self.evaluateVar(varContent)
            self.vars[varName] = varEval

    def delVar(self, task):
        taskContent = task[0]
        taskContent = taskContent.replace('del ', '', 1)

        try:
            del self.vars[taskContent]
        except KeyError:
            language.error(f"Var does not exist | Var: {taskContent} | Line: {self.currentLine}")

    def loopFunc(self, task):
        taskContent = task[0]
        taskContent = taskContent.replace('loop', '', 1)
        declarationIndex = taskContent.index(",")
        # grab content of var (cuts at declarationIndex)
        loopLength = taskContent[declarationIndex + 1:].strip()

        # grab name of var (cuts before declarationIndex)
        indexName = taskContent[:declarationIndex].strip()
        # create a new index var, so it can be used in the loop
        loopLength = self.evaluateVar(str(loopLength))
        if loopLength[1] != "int":
            language.error(f"loop length not int | Var: {indexName} | Line: {self.currentLine}")

        self.vars[indexName] = [0, "int"]
        # all the lines of code between the loop
        loopCode = []
        for line in self.rawCode[self.currentLine:]:
            if self.indentData[line[1]] > self.indentData[self.currentLine-1]:
                loopCode.append(line)
            else:
                break

        for i in range(loopLength[0]):
            self.vars[indexName] = [i, "int"]
            self.parse(list(loopCode), self.currentLine)
            if i == range(loopLength[0]):
                del self.vars[indexName]
        # delete the index var after loop is over

        self.jumpLine = len(loopCode)

    def calcVar(self, content):
        content = content.replace('calc', '', 1)
        c_content = content
        splitContent = []
        usedOperons = []

        for i, char in enumerate(content.strip()):

            if char in self.operons:
                usedOperons.append(char)
                c_content = c_content.replace(char, "~")

        splitString = (c_content.strip()).split(" ~ ")

        operationList = []
        for i in range(len(splitString)):
            operationList.append(str(splitString[i]))
            if i != len(splitString) - 1:
                operationList.append(str(usedOperons[i]))
        valueList = []
        for item in operationList:
            if not (item in self.operons):
                itemEval = self.evaluateVar(item)
                if itemEval[1] == "str":
                    language.error(f"Can't use str in 'calc' operation | Value: {item} | Line: {self.currentLine}")
                valueList.append(str(itemEval[0]))
            else:
                valueList.append(item)

        operation = ' '.join(valueList)

        try:
            result = eval(operation)
            if result == int(result):
                result = int(result)
            else:
                result = float(result)
        except SyntaxError:
            language.error(f"Calc syntax error | Expression: {operation} | Line: {self.currentLine}")

        return self.evaluateVar(str(result))

    def printUtils(self, content):
        # Make List
        contentAsList = []
        for element in range(0, len(content)):
            contentAsList.append(content[element])
        # Create Item To Print
        value = ""
        insideQuotes = False
        variable = False
        tempString = ""
        variableName = ''

        for char in contentAsList:
            if char == '"':
                if insideQuotes:
                    insideQuotes = False
                else:
                    insideQuotes = True

            if char == "{":
                variable = True
            elif char == "}":
                variable = False

            if variable:
                if char == '{' or char == '}':
                    pass
                else:
                    variableName += char
            elif not (variable):
                if variableName == '':
                    if char == ' ' and not (insideQuotes):
                        pass
                    elif char == '+' and not (insideQuotes):
                        tempString += ' '
                    elif char == ',' and not (insideQuotes):
                        tempString += ''
                    elif char == '"':
                        pass
                    elif not (char.isnumeric()) and not (insideQuotes):
                        print(tempString)
                        print(char)
                        print(insideQuotes)
                        self.error(f"String outside of quotation marks | Line: {self.currentLine}")
                    else:
                        tempString += char
                else:

                    tempString += str(self.vars[variableName][0])
                    variableName = ''
        value += tempString

        print(value)

    def debug(self, task):
        taskContent = task[0]
        if taskContent.startswith("variables."):
            taskContent = taskContent.replace("variables.", '')
            if taskContent == "list()":
                self.listVars()
            elif taskContent.startswith("list("):
                taskContent = taskContent.replace('list(', '')
                taskContent = taskContent.replace(')', '')
                language.error(
                    f'"rh.variables.listVars()" does not take any arguments | Argument: "{taskContent}" | Line: {self.currentLine}')
            elif taskContent == "values()":
                self.listVarVals()
            elif taskContent.startswith("values("):
                taskContent = taskContent.replace('values(', '')
                taskContent = taskContent.replace(')', '')
                language.error(
                    f'"rh.variables.values()" does not take any arguments | Argument: "{taskContent}" | Line: {self.currentLine}')
        elif taskContent.startswith("error("):
            start_index = taskContent.find("(")
            end_index = taskContent.find(")")
            if start_index != -1 and end_index != -1:
                # Extract content between parentheses
                content = taskContent[start_index + 1:end_index]

                content = content.replace('"', '')

                language.error(content)
        else:
            language.error(f'Unknown function in "rh" | Expression: {taskContent} | Line: {self.currentLine}')
            
    def conditional(self, content):
        content = content.replace('if', '', 1)
        
        splitContent = list(content.split(" "))
        
        splitContent = [i for i in splitContent if i]
        
        for i in range(len(splitContent)):
            if splitContent[i] in self.conditionals:
                splitContent[i] = str(" " + splitContent[i] + " ")
            elif splitContent[i] in self.vars.keys():
                splitContent[i] = str(self.vars[splitContent[i]][0])
                
        modContent = ''.join(splitContent)
        
        if eval(str(modContent)):
        
            conCode = []
            for line in self.rawCode[self.currentLine:]:
                if self.indentData[line[1]] > self.indentData[self.currentLine-1]:
                    conCode.append(line)
                else:
                    break
                
            self.parse(list(conCode), self.currentLine)
            self.jumpLine = len(conCode)
