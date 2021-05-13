

class _Error:
    def __init__(self, xMessage, xLine, xErrorCode):
        print("\n" * 10)
        
        print("Error at Line {xLine}: {xMessage}\n    {xErrorCode}".format(xLine = xLine, xMessage = xMessage, xErrorCode = xErrorCode))
        exit(0)
    
class cBaabnq:    
    class cCodeGen:
        def __init__(self):
            self.xIntLimit = int("1" * 16, 2) #16 bit memlimit
            
            self.xMemUsed = [] #list of used mem addresses
            self.xMemFree = [x for x in range(self.xIntLimit)] #list of free mem addresses
            
            self.xVarMapper = {}
            self.xLabels = [] #i only store the labels to generate intermediate ones and so as to not have 1 label 2 times 
        
            self.xStructSizeMapper = {}
    
        
        
        def genError(self, xMessage, xLine, xErrorCode):
            xErrorLineOffset = self.xLineMapper[xLine]
            _Error(xMessage, xLine + xErrorLineOffset, xErrorCode)
    
        def checkMemFree(self, xSampleIndex = 0):
            if len(self.xMemFree) == 0:
                cCodeGen.genError("out of memory", self.xLine, " ".join([str(x[0]) for x in self.xLineParserStruct]))
            
            else:
                return self.xMemFree[xSampleIndex]
        
        
        
        #this will check memory in a row, so we can make sure that if we need more than one memory address, that the list of addresses is in the right order
        def checkMemFreeRow(self, xSize):
            for xMemScanIndex in range(self.xIntLimit):

                xRowScanIndex = 0
                while True:
                    if xMemScanIndex + xRowScanIndex in self.xMemUsed:
                        break
                    
                    elif xRowScanIndex == xSize:
                        return [int(x) for x in range(xMemScanIndex ,xMemScanIndex + xSize)]
                        
                    xRowScanIndex += 1
                
                        
        def malloc(self, xInput):
            self.xMemFree.remove(int(xInput))
            self.xMemUsed.append(int(xInput))
            
        
        def getLabFree(self):
            xIndex = 0
            while "Temp" + str(xIndex) in self.xLabels:
                xIndex += 1
            
            xTempLabel = "Temp" + str(xIndex)
            
            self.xLabels.append(xTempLabel)
            return xTempLabel
        
                
        def Main(self, xParserStruct):
            
            self.xOutputCode = []
            
            for xLine in range(len(xParserStruct)):
                self.xLine = xLine
                
                self.xLineParserStruct = xParserStruct[self.xLine]
                self.xOutputCode.append(" ")
                self.xOutputCode.append('"' + " ".join([str(x[0]) for x in self.xLineParserStruct])) #this adds a comment of the uncompild source, just for debuging
                
                
                xLineTypes = [x[1] for x in self.xLineParserStruct] #these are all the type of the tokens in the current line
                xLineObj =   [x[0] for x in self.xLineParserStruct] #these hold the member objs
                                
                #check if the first token is a command                
                if xLineTypes[0] != "Command":
                    self.genError("first element in statement must be command", self.xLine, " ".join([str(x[0]) for x in self.xLineParserStruct]))
                
                
                elif xLineObj[0] == "put":
                    xAssignmentType = xLineObj[2]
                    xBase           = xLineObj[1]
                    xOverrideObj    = xLineObj[3]                    
                    
                    #check type and given tokens
                    if xAssignmentType == "=" and xLineTypes[1:] in [["Obj", "AssignmentType", "Obj"], ["Obj", "AssignmentType", "Expr"]]:
                        if xBase.xType != "Var":
                            self.genError("assignment base must be variable", self.xLine, " ".join([str(x[0]) for x in self.xLineParserStruct]))
        
                        #check if obj need to allocated
                        if xBase.xValue not in self.xVarMapper.keys():
                            xAllocateAddr = self.checkMemFree()
                            self.xVarMapper[xBase.xValue] = xAllocateAddr
                            self.malloc(xAllocateAddr)
                        
                        self.xOutputCode += xOverrideObj.Eval(self)
                        self.xOutputCode += xBase.Set(self)

                    elif xAssignmentType == "<-" and xLineTypes[1:] in [["Obj", "AssignmentType", "Obj"], ["Obj", "AssignmentType", "Expr"]]:
                        try:                        
                            xTempAddr = str(self.checkMemFree())
                            self.malloc(xTempAddr)
                            self.xOutputCode += xOverrideObj.Eval(self)
                            self.xOutputCode += ["pla", "sAD " + xTempAddr, "lPA " + xTempAddr, "pha"] #direct pointer deref
                            self.xOutputCode += xBase.Set(self)

                        except Exception:
                            self.genError("invaild command argument types", self.xLine, " ".join([str(x[0]) for x in self.xLineParserStruct]))

                    
                    elif xAssignmentType == "->" and xLineTypes[1:] in [["Obj", "AssignmentType", "Obj"], ["Expr", "AssignmentType", "Obj"], ["Obj", "AssignmentType", "Expr"], ["Expr", "AssignmentType", "Expr"]]:
                        #try catch here cuz' im too lazy to do the logic for checking "Obj" against "Expr" and it doesnt really matter
                        try:
                            if xOverrideObj.xType == "Name" or xBase.xType == "Name":
                                self.genError("invaild command argument types", self.xLine, " ".join([str(x[0]) for x in self.xLineParserStruct]))

                        except Exception:
                            pass
                        
                        xTempAddr = str(self.checkMemFree())
                        self.malloc(xTempAddr)
                        self.xOutputCode += xBase.Eval(self)
                        self.xOutputCode += xOverrideObj.Eval(self)                        
                        self.xOutputCode += ["pla", "sAD " + xTempAddr, "pla", "sAP " + xTempAddr]
                        
                    else:
                        self.genError("invaild command arguments", self.xLine, " ".join([str(x[0]) for x in self.xLineParserStruct]))
                
                elif xLineObj[0] == "del":
                    if xLineTypes[1:] == ["Obj"]:
                        xSoonGoneObj = xLineObj[1]
                        if xSoonGoneObj.xType != "Var":
                            self.genError("can only unallocate variable", self.xLine, " ".join([str(x[0]) for x in self.xLineParserStruct]))

                        #unallocate memory
                        xUnallocateAddr = self.xVarMapper[xSoonGoneObj.xValue]
                        self.xMemUsed.remove(xUnallocateAddr)
                        self.xMemFree.append(xUnallocateAddr)
                        
                        #delete mapper
                        del self.xVarMapper[xSoonGoneObj.xValue]
                        
                    else:
                        self.genError("invaild command arguments", self.xLine, " ".join([str(x[0]) for x in self.xLineParserStruct]))                        
                
                elif xLineObj[0] == "input":
                    if xLineTypes[1:] == ["Obj"]:
                        xInputObj = xLineObj[1]
                        if xInputObj.xType != "Var":
                            self.genError("can only input to variable", self.xLine, " ".join([str(x[0]) for x in self.xLineParserStruct]))
                
                        #call input
                        self.xOutputCode += ["inp " + str(self.xVarMapper[xInputObj.xValue])]
                
                    else:
                        self.genError("invaild command arguments", self.xLine, " ".join([str(x[0]) for x in self.xLineParserStruct]))                                                
                
                elif xLineObj[0] == "print":
                    if xLineTypes[1] in ["Obj", "Expr"]:
                        xInputObj = xLineObj[1]
                        if xLineTypes[1] == "Obj" and xInputObj.xType == ["Name"]:
                            self.genError("can not print name", self.xLine, " ".join([str(x[0]) for x in self.xLineParserStruct]))
                
                        #call print
                        xTempAddr = str(self.checkMemFree())
                        self.malloc(xTempAddr)
                        self.xOutputCode += xInputObj.Eval(self) + ["pla", "sAD " + xTempAddr, "out " + xTempAddr]
                                                
                    else:
                        self.genError("invaild command arguments", self.xLine, " ".join([str(x[0]) for x in self.xLineParserStruct]))                                                
                    
                
                elif xLineObj[0] == "lab":
                    if xLineTypes[1:] == ["Obj"]:
                        xLabName = xLineObj[1]
                        if xLabName.xType != "Name":
                            self.genError("label must be defind with name", self.xLine, " ".join([str(x[0]) for x in self.xLineParserStruct]))

                        self.xLabels.append(xLabName.xValue)
                        self.xOutputCode += ["lab " + xLabName.xValue]
                            
                    else:
                        self.genError("invaild command arguments", self.xLine, " ".join([str(x[0]) for x in self.xLineParserStruct]))                                                
                
                elif xLineObj[0] == "jump":
                    if xLineTypes[1:] == ["Obj"]:
                        self.xOutputCode += ["got " + xLineObj[1].xValue]
                        
                    elif xLineTypes[1:] in [["Obj", "Obj", "Obj", "JumpOpp", "Obj"], ["Obj", "Obj", "Obj", "JumpOpp", "Expr"], ["Obj", "Obj", "Expr", "JumpOpp", "Obj"], ["Obj", "Obj", "Expr", "JumpOpp", "Expr"]]:
                        if xLineObj[1].xType == "Name" and xLineObj[2].xValue == "~":
                            xJumpConType = xLineObj[4]
                            xConArg1 = xLineObj[3]
                            xConArg2 = xLineObj[5]
                            
                            #load values
                            xTempAddr = self.checkMemFree()
                            self.malloc(xTempAddr)
                            xJumpLabel = str(xLineObj[1].xValue)
                            self.xOutputCode += xConArg1.Eval(self) + xConArg2.Eval(self) + ["pla", "sAD " + str(xTempAddr), "pla", "lDR " + str(xTempAddr)]
                            
                            if xJumpConType == "==":
                                self.xOutputCode += ["jmA " + xJumpLabel]
                                
                            elif xJumpConType == ">":
                                self.xOutputCode += ["jmG " + xJumpLabel]
                            
                            elif xJumpConType == "<":
                                self.xOutputCode += ["jmL " + xJumpLabel]
                                
                            elif xJumpConType == "!=":
                                xTempLab = self.getLabFree()
                                self.xOutputCode += ["jmA " + xTempLab, "got " + xJumpLabel, "lab " + xTempLab]
                            
                        else:
                            self.genError("invaild jump type", self.xLine, " ".join([str(x[0]) for x in self.xLineParserStruct]))                                                
                            

                
                    else:
                        self.genError("invaild command arguments", self.xLine, " ".join([str(x[0]) for x in self.xLineParserStruct]))                                                

                elif xLineObj[0] == "sub":
                    if xLineTypes[1:] == ["Obj"]:
                        xSubroutineLabel = xLineObj[1]
                        
                        if xSubroutineLabel.xType == "Name":                            
                            self.xOutputCode += ["jmS " + str(xSubroutineLabel)]
                            
                        else:
                            self.genError("can not call subroutine on non label obj", self.xLine, " ".join([str(x[0]) for x in self.xLineParserStruct]))
                    
                    elif xLineTypes[1:] in [["Obj", "Obj", "Obj", "JumpOpp", "Obj"], ["Obj", "Obj", "Obj", "JumpOpp", "Expr"], ["Obj", "Obj", "Expr", "JumpOpp", "Obj"], ["Obj", "Obj", "Expr", "JumpOpp", "Expr"]]:
                        xSubroutineLabel = xLineObj[1]
                        
                        if xSubroutineLabel.xType == "Name" and xLineObj[2].xValue == "~":
                            xJumpConType = xLineObj[4]
                            xConArg1 = xLineObj[3]
                            xConArg2 = xLineObj[5]

                            #this is for load the 2 con args
                            xTempAddr = self.checkMemFree()
                            self.malloc(xTempAddr)
                            
                            
                            #this is for the jumping logic
                            xSkipLab = str(self.getLabFree())
                            xCheckLab = str(self.getLabFree())
                            
                            self.xOutputCode += xConArg1.Eval(self) + xConArg2.Eval(self) + ["pla", "sAD " + str(xTempAddr), "pla", "lDR " + str(xTempAddr)]

                            if xJumpConType == "==":
                                self.xOutputCode += ["jmA " + xCheckLab, "got " + xSkipLab, "lab " + xCheckLab, "jmS " + str(xSubroutineLabel), "lab " + xSkipLab]
                            
                            elif xJumpConType == ">":
                                self.xOutputCode += ["jmG " + xCheckLab, "got " + xSkipLab, "lab " + xCheckLab, "jmS " + str(xSubroutineLabel), "lab " + xSkipLab]

                            elif xJumpConType == "<":
                                self.xOutputCode += ["jmL " + xCheckLab, "got " + xSkipLab, "lab " + xCheckLab, "jmS " + str(xSubroutineLabel), "lab " + xSkipLab]
                            
                            elif xJumpConType == "!=":
                                self.xOutputCode += ["jmA " + xSkipLab, "jmS " + str(xSubroutineLabel), "lab " + xSkipLab]
                            
                                                        
                        else:
                            self.genError("invaild call type", self.xLine, " ".join([str(x[0]) for x in self.xLineParserStruct]))
                        
                                                    
                    else:
                        self.genError("invaild command arguments", self.xLine, " ".join([str(x[0]) for x in self.xLineParserStruct]))                                                
                
                elif xLineObj[0] == "return":
                    self.xOutputCode += ["ret"]

                elif xLineObj[0] == "push":
                    if xLineTypes[1] in ["Obj", "Expr"]:
                        if xLineTypes[1] == "Obj" and xLineObj[1].xType == "Name":
                            self.genError("can not push name", self.xLine, " ".join([str(x[0]) for x in self.xLineParserStruct]))                                                
                            
                        self.xOutputCode += xLineObj[1].Eval(self) #we dont need to do anything cuz' Eval will push to the stack
                         
                           
                    else:
                        self.genError("invaild command arguments", self.xLine, " ".join([str(x[0]) for x in self.xLineParserStruct]))                                                

                elif xLineObj[0] == "pull":
                    if xLineTypes[1] == "Obj":
                        if xLineObj[1].xType != "Var":
                            self.genError("can not pull to other than variable", self.xLine, " ".join([str(x[0]) for x in self.xLineParserStruct]))                                                
                        
                        self.xOutputCode += xLineObj[1].Set(self)
                        
                    else:
                        self.genError("invaild command arguments", self.xLine, " ".join([str(x[0]) for x in self.xLineParserStruct]))                                                
                
                elif xLineObj[0] == "struct":
                    if xLineTypes[1:] == ["Obj", "Obj"]:
                        xStructName = xLineObj[1].xValue
                        xStructSize = xLineObj[2].xValue
                        
                        #first check types
                        if xLineObj[1].xType != "Name" or xLineObj[2].xType != "Const":
                            self.genError("struct types must be predefind", self.xLine, " ".join([str(x[0]) for x in self.xLineParserStruct]))                                                
                            
                        #then check if struct is alredy defind
                        if xStructName in self.xStructSizeMapper.keys():
                            self.genError("struct must not be redefind", self.xLine, " ".join([str(x[0]) for x in self.xLineParserStruct]))
                            
                        else:
                            self.xStructSizeMapper[xStructName] = int(xStructSize)

                    else:
                        self.genError("invaild command arguments", self.xLine, " ".join([str(x[0]) for x in self.xLineParserStruct]))                                                
                    
                
                
                elif xLineObj[0] == "new":
                    if xLineTypes[1:] == ["Obj", "Obj"]:
                        xAllocStructName = xLineObj[1].xValue
                        xPtrVariable = xLineObj[2]
                        xAllocStructSize = self.xStructSizeMapper[xAllocStructName]
                        
                        if xLineObj[1].xType != "Name" or xLineObj[2].xType != "Var":
                            self.genError("struct must be allocated to variable pointer", self.xLine, " ".join([str(x[0]) for x in self.xLineParserStruct]))                                                
                
                        #allocate memory                        
                        xAddrSpace = self.checkMemFreeRow(xAllocStructSize)                        
                        xBaseAddr = xAddrSpace[0]
                        for xI in xAddrSpace:
                            self.malloc(xI)
                            
                        #allocate variable
                        xVarAlloc = self.checkMemFree()
                        self.malloc(xVarAlloc)
                        self.xVarMapper[xPtrVariable.xValue] = xVarAlloc
                        
                        #set pointer variable
                        self.xOutputCode += ["clr", "set " + str(xBaseAddr), "add", "pha"]
                        self.xOutputCode += xPtrVariable.Set(self)
                    
                    elif xLineTypes[1:] == ["String", "Obj"]:
                        #get the string thats gonna be allocated and remove the quotation
                        xAllocString = xLineObj[1].replace("'", "")
                    
                        
                        #convert in into ascii and add a NULL terminator
                        xAllocAscii = []
                        for xLineIterator in xAllocString.split("\\n"):
                            xAllocAscii += [ord(x) for x in xLineIterator] + [10]

                        #override the last newline with a NULL terminator
                        xAllocAscii[-1] = 0
                                                
                        #then allocate memory for the string
                        xAllocSize = len(xAllocAscii)
                        
                        xAllocAddr = self.checkMemFreeRow(xAllocSize)
                        xBaseAddr = xAllocAddr[0]
                        
                        for xI in xAllocAddr:
                            self.malloc(xI)
                            
                            
                        #then generate the code
                        for xI in range(xAllocSize):
                            self.xOutputCode += ["set " + str(xAllocAscii[xI]), "sRD " + str(xAllocAddr[xI])]
                        
                        #now handle pointer variable to the base
                        xPtrVariable = xLineObj[2]                        
                        
                        #if varibale doesn't exist, malloc
                        if xPtrVariable.xValue not in self.xVarMapper.keys():
                            xVarAlloc = self.checkMemFree()
                            self.malloc(xVarAlloc)
                            self.xVarMapper[xPtrVariable.xValue] = xVarAlloc
                        
                        #set pointer variable
                        self.xOutputCode += ["clr", "set " + str(xBaseAddr), "add", "pha"]
                        self.xOutputCode += xPtrVariable.Set(self)
                        
                        
                       
                    else:
                        self.genError("invaild command arguments", self.xLine, " ".join([str(x[0]) for x in self.xLineParserStruct]))                                                
                
                
                elif xLineObj[0] == "putstr":
                    if xLineTypes[1:] == ["Obj"]:
                        self.xOutputCode += xLineObj[1].Eval(self) + ["pla", "putstr"]
                        
                    else:
                        self.genError("invaild command arguments", self.xLine, " ".join([str(x[0]) for x in self.xLineParserStruct]))                                                
                
                
                
                
            self.xOutputCode += ["", "brk"]
            return "\n".join(self.xOutputCode)

    class cObj: #this class  will hold an obj like var, const and labels
        def __init__(self, xValue):
            self.xValue = xValue
            self.xType = None
            self.xLen = len(self.xValue)
        
            if self.xLen != 0:
                if self.xValue[0] == "_" and self.xLen > 1:
                    self.xType = "Var"
                    
                elif self.xValue.isdigit():
                    self.xType = "Const"
                    
                else:
                    self.xType = "Name"
        
        #this will return the eval code
        #the code will eval to the stack
        def Eval(self, cCodeGen):
            if self.xType == "Var":
                return ["clr", "lDA " + str(self.checkVarMapper(cCodeGen, self.xValue)), "pha"]
            
            elif self.xType == "Const":
                return ["clr", "set " + str(self.xValue), "add", "pha"]
        
            else:
                cCodeGen.genError("can not eval name", cCodeGen.xLine, " ".join([str(x[0]) for x in cCodeGen.xLineParserStruct]))                        
        
        
        def EvalPointer(self, cCodeGen):
            if self.xType == "Var":
                return ["clr", "lPA " + str(self.checkVarMapper(cCodeGen, self.xValue)), "pha"]
            
            elif self.xType == "Const":
                return ["clr", "lDA " + str(self.xValue), "pha"]            
        
                    
        #this will return set code
        #set take the last value on the stack and overrides this obj with it          
        def Set(self, cCodeGen):
            if self.xType == "Var":
                return ["pla", "sAD " + str(self.checkVarMapper(cCodeGen, self.xValue))]
                
        
        def SetPointer(self, cCodeGen):
            if self.xType == "Var":
                return ["pla", "sAP " + str(self.checkVarMapper(cCodeGen, self.xValue))]
                
            elif self.xType == "Const":
                return ["pla", "sAD " + str(self.xValue)]
                
        
        def checkVarMapper(self, cCodeGen, xIndex):
            if xIndex in cCodeGen.xVarMapper.keys():
                return cCodeGen.xVarMapper[xIndex]
                
            else:
                cCodeGen.genError("unable to map variable", cCodeGen.xLine, " ".join([str(x[0]) for x in cCodeGen.xLineParserStruct]))                        

        
        def __str__(self):
            return self.xValue
        
        
    class cExpr:
        def __init__(self, xInput):
            self.xOpps = [["+", "-"], ["|", "&", "'", "^", "<<", ">>"]]
            self.xPrecedenceLevel = 0
            
            
            self.xOpp = None
            self.xInput = xInput

            #remove brackets for simplification
            if self.xInput[0] == "(" and self.xInput[-1] == ")" and "(" not in self.xInput[1:-1] and")" not in self.xInput[1:-1]:
                self.xInput = self.xInput[1:-1]
                
            xBracketIndex = 0
            
            
            #check opps, lower priority first because reverse polish
            #btw excuse the messy code
            while len(self.xOpps) != self.xPrecedenceLevel:
                for xOppsIter in self.xOpps[self.xPrecedenceLevel]:
                    if xOppsIter in self.xInput and self.getBracketLvl(self.xInput, self.xInput.index(xOppsIter)) == 0:
                        self.xOpp = xOppsIter

                self.xPrecedenceLevel += 1
            
            if self.xOpp:
                xSubExprs = self.xInput.split(self.xOpp, 1)
                                
                self.xSubExpr1 = cBaabnq.cExpr(xSubExprs[0])
                self.xSubExpr2 = cBaabnq.cExpr(xSubExprs[1])
                
        def getBracketLvl(self, xInputString, xSamplePoint):
            xIndex = 0
            xBracketCounter = 0
            
            while xIndex != xSamplePoint:
                if xInputString[xIndex] == "(":
                    xBracketCounter += 1
                    
                elif xInputString[xIndex] == ")":
                    xBracketCounter -= 1
                
                xIndex += 1
            
            return xBracketCounter
        
        
        #this function will return code that will eval the expr holded in this class
        #the result will be push to the stack
        def Eval(self, cCodeGen):
            if self.xOpp:
                xSubExpr1Code = self.xSubExpr1.Eval(cCodeGen)
                xSubExpr2Code = self.xSubExpr2.Eval(cCodeGen)
                xOppCode = {"+" : "add", 
                            "-" : "sub",
                            "|" : "lor",
                            "&" : "and",
                            "'" : "not",
                            "^" : "xor",
                            "<<": "shg",
                            ">>": "shs"
                
                }[self.xOpp]
                
                if xOppCode in ["shs", "shg"]:
                    xIndexAddr = str(cCodeGen.checkMemFree(0))
                    xChangeAddr = str(cCodeGen.checkMemFree(1))
                    
                    xLoopLab = cCodeGen.getLabFree()
                    xExitLab = cCodeGen.getLabFree()                    
                    
                    cCodeGen.malloc(xIndexAddr)
                    cCodeGen.malloc(xChangeAddr)
                    
                    return xSubExpr1Code + xSubExpr2Code + ["pla", "sAD " + xIndexAddr, "pla", "sAD " + xChangeAddr, "lab " + str(xLoopLab), "lDA " + str(xChangeAddr), xOppCode, "sAD " + str(xChangeAddr), "lDA " + str(xIndexAddr), "set 1", "sub", "sAD " + str(xIndexAddr), "jm0 " + xExitLab, "got " + xLoopLab, "lab " + xExitLab, "lDA " + str(xChangeAddr), "pha"]

                    
                else:
                    xTempAddr = str(cCodeGen.checkMemFree())
                    cCodeGen.malloc(xTempAddr)
                    
                    return xSubExpr1Code + xSubExpr2Code + ["pla", "sAD " + xTempAddr, "pla", "lDR " + xTempAddr, xOppCode, "pha"]
                
            else:                
                xThisObj = cBaabnq.cObj(self.xInput) #if there is not opperator then make the input a obj and eval
                return xThisObj.Eval(cCodeGen)
        
        def __str__(self):
            return self.xInput
        
    class cParser:
        def __init__(self):
            self.xParserStruct = []
            
        def Main(self, xInput):
            for xLines in xInput:
                self.xParserStruct.append([])
                for xToken in xLines:
                    xCurrentlyParsedObj = None
                    
                    if xToken[1] == "Obj":
                        xCurrentlyParsedObj = cBaabnq.cObj(xToken[0])
                    
                    elif xToken[1] in ["Command", "AssignmentType", "JumpOpp", "String"]:
                        xCurrentlyParsedObj = xToken[0]
                    
                    elif xToken[1] == "Expr":
                        xCurrentlyParsedObj = cBaabnq.cExpr(xToken[0])
                    
                    self.xParserStruct[-1].append([xCurrentlyParsedObj, xToken[1]])
                    
            
            
            return self.xParserStruct
    
    
    class cTokenizer:
        def __init__(self):
            self.xCommands = ["put", "del", "jump", "input", "print", "sub", "return", "push", "pull", "struct", "new", "lab", "putstr"]
            self.xOpperators = ["+", "-", "|", "&", "^", "<<", ">>"]
            self.xAssignmentType = ["<-", "->", "="]
            self.xJumpOpps = ["==", ">", "<", "!="]
            self.xStringMark = "'"
        
        def removeDoubleSpace(self, xInput):
            while "  " in xInput:
                xInput = xInput.replace("  ", " ")
        
            return xInput
        
        def removeGarbage(self, xInput):
            xLines = xInput.split("\n")
            
            for xI in range(len(xLines)):
                if len(xLines[xI]) > 0:
                    while xLines[xI][0] in [" ", "\t"]:
                        xLines[xI] = xLines[xI][1:]


            return "\n".join(xLines)
            
        #this will correct the error output
        def LineMapper(self, xInput):
            xLinesRaw = self.removeGarbage(xInput).split("\n")
            xLineRelevantsCounter = 0
            xLineCounts = []
            
            
            for xI in range(len(xLinesRaw)):
                xLineIndex = xLinesRaw[xI]                
                if (xLineIndex == '' or xLineIndex[0] == '"'): 
                    xLineRelevantsCounter += 1
                    
                else:
                    xLineCounts.append(xLineRelevantsCounter)
                    
            self.xLineCounts = xLineCounts


        def evalImports(self, xInput):
            #filter all the comments
            xComments = [x.split("\n")[0].split(";")[0].replace("  ", " ").split(" ") for x in xInput.split('"') if x.replace(" ", "") != ""]
            xFullInput = ""
            
            for xI in xComments:
                if xI[0] == "use":
                    if xI[1] == self.xInputDatapath:
                        print("Error: Import circle reference")
                        exit(0)
                        
                    else:
                        xFullInput += self.evalImports(open(xI[1], "r").read())
            
            return xFullInput + "\n" + xInput


        
        def Lex(self, xInput):
            #eval imports 
            xFullInput = self.evalImports(xInput)
            
            #print with line numbers
            #xFullLines = xFullInput.split("\n")
            #print("\n".join([str(xI) + " " + xFullLines[xI] for xI in range(len(xFullLines))]))
            
            #map line for error line correction
            self.LineMapper(xFullInput)

            
            
            xNoComments = "\n".join([x for x in xFullInput.split("\n") if x.replace(" ", "") != "" and x.replace(" ", "")[0] != '"'])

            xCommandArray = self.removeDoubleSpace(self.removeGarbage(xNoComments).replace("\n", " ")).split(";")[:-1]
            xFormatArray = [] #the format array is for removeing odditss like spackes at the start of the line
                        
            for xCommand in xCommandArray:
                
                xCommandHolder = xCommand.split(" ")
                try:
                    while xCommandHolder[0] == "":
                        xCommandHolder.pop(0)

                except IndexError:
                    pass
                
                xFormatArray.append(" ".join(xCommandHolder))
                
            return xFormatArray
    
    
        def Main(self, xInput, xInputDatapath):
            self.xInputDatapath = xInputDatapath
            xLexedCode = self.Lex(xInput)            
            xTokens = []

            for xLines in range(len(xLexedCode)):

                xNewToken = []
                for xSubToken in xLexedCode[xLines].split(" "):                    
                    try:
                        if self.xStringMark in xSubToken:
                            if (len(xSubToken.split(self.xStringMark)) - 1) > 2:
                                _Error(xMessage = "Invalid string", xLine = xLines, xErrorCode = xLexedCode[xLines])
                                
                            elif (len(xSubToken.split(self.xStringMark)) - 1) > 1:
                                xNewToken.append([xSubToken, "String"])

                            #if the is the end of the string append the current subtoken and change the last type form string in progress to string done
                            elif xNewToken[-1][1] == "StringPart":
                                xNewToken[-1][0] += " " +  xSubToken
                                xNewToken[-1][1] = "String"
                            
                            else:
                                xNewToken.append([xSubToken, "StringPart"])
                            
                        elif len(xNewToken) > 0 and xNewToken[-1][1] == "StringPart":
                            xNewToken[-1][0] += " " + xSubToken
                            
                            
                        elif xSubToken in self.xCommands:
                            xNewToken.append([xSubToken, "Command"])
                                            
                        elif xSubToken in self.xOpperators:
                            xNewToken.append([xSubToken, "Opp"])
                        
                        
                        elif xSubToken in self.xAssignmentType:
                            xNewToken.append([xSubToken, "AssignmentType"])
                        
                        elif xSubToken in self.xJumpOpps:
                            xNewToken.append([xSubToken, "JumpOpp"])    
                            
                                                
                        #check if last token is opp than add the current name and make it an expr
                        elif xNewToken[-1][1] == "Opp":
                            xExprArg1 = xNewToken[-2][0]
                            xExprArg2 = xSubToken
                            xExprOpp = xNewToken[-1][0]
                            
                            xNewToken.pop(-1) #remove xExprArg1 and xOpp to concatital to expr
                            xNewToken.pop(-1)
    
                            xNewToken.append([xExprArg1 + xExprOpp + xExprArg2, "Expr"])
    
        
    
                        
                        else:
                            xNewToken.append([xSubToken, "Obj"])

                    except IndexError:
                        xNewToken.append([xSubToken, "Obj"])
                        
                if xNewToken != []:            
                    xTokens.append(xNewToken)
            
            return xTokens            
                        
    class cCompiler:
        def __init__(self):
            self.cT = cBaabnq.cTokenizer()
            self.cP = cBaabnq.cParser()
            self.cG = cBaabnq.cCodeGen()
            
        def Compile(self, xInputDatapath):
            xInputFile = open(xInputDatapath).read()
            
            self.xTokens = self.cT.Main(xInputFile, xInputDatapath)
            self.xParserStruct = self.cP.Main(self.xTokens)
            
            #move error offset to codeGen
            self.cG.xLineMapper = self.cT.xLineCounts
            
            try:
                self.xCompiledCode = self.cG.Main(self.xParserStruct)
    
                return self.xCompiledCode + "\n" * 5 + '"Compiled from source: ' + str(xInputDatapath)
                
            except Exception as E:
                print("\n\nInternal Error thrown:\n{error}".format(error = E))
                print("\n\n\nFatal Error at Line: {line}".format(line = self.cG.xLine))
               
                exit(0)
            
            
if __name__ == '__main__':    
    import sys
    xArgv = sys.argv
    
    try:
        for xI in range(len(xArgv) - 1):
            if xArgv[xI] == "--input":
                xInputDatapath = str(xArgv[xI + 1])
                
            elif xArgv[xI] == "--output":
                xOutputDatapath = str(xArgv[xI + 1])
            
    except Exception:
        print("Error while loading file")
        exit()

    
    cComp = cBaabnq.cCompiler()    
    xCompiledFile = cComp.Compile(xInputDatapath)

    if xCompiledFile:    
        xOutputFile = open(xOutputDatapath, "w")
        xOutputFile.write(xCompiledFile)
        xOutputFile.close()
        
        #print("\n\n\n\n\nCompilation was sucsessful")