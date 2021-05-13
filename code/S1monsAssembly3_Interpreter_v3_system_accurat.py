"""
Acc - Accumolator
Reg - Register
mem - Memory

16-Bit Maschine

set attr - set attr into Reg

add none - Acc = Acc + Reg
sub none - Acc = Acc - Reg
shg none - Acc = Acc shifted greater
shs none - Acc = Acc shifted smaller

lor none - Acc = Acc (logical or) Reg
and none - Acc = Acc (logical and) Reg
xor none - Acc = Acc (logical xor) Reg
not none - Acc = Acc (logical not)

lDA attr - Load mem at attr into Acc
lDR attr - Load mem at attr into Reg
sAD attr - Save Acc into mem at attr
sRD attr - Save Reg into mem at attr

lPA atrr - Load mem pointed to by mem at attr into Acc
lPR atrr - Load mem pointed to by mem at attr into Reg
sAP atrr - Save Acc into mem pointed to by mem at attr
sRP atrr - Save Reg into mem pointed to by mem at attr

out attr - outputs mem at attr
inp attr - inputs  mem at attr

lab attr - define lable
got attr - goto attr
jm0 attr - goto attr if Acc = 0
jmA attr - goto attr if Acc = Reg

jmG attr - goto attr if Acc > Reg (jmG for jump great)
jmL attr - goto atrr if Acc < Reg (jmL for jump less)

jmS attr - goto attr as subroutine (pc gets push to stack)
ret none - return from subroutine (stack gets pop to pc)

pha none - push Acc to stack
pla none - pull from stack to Acc


brk none - stops programm
clr none - clears Reg and Acc

putstr none - print the Acc as ascii
"""


#please not that this is a system accurat interpreter and is NOT compatible with other S1monsAssembly3 programm
#this version is specially made of the compiler rewrite
 
class _Error(Exception):
    def __init__(self, error):
        self.error = error
        
    def __str__(self):
        return self.error


class cInt:
    def __init__(self, xInt = 0, xIntLimit = 65535):
        self.xInt = xInt
        self.xIntLimit = xIntLimit
        
        
    def Set(self, xNew):
        self.xInt = int(xNew) % self.xIntLimit
        
    def Add(self, xValue):
        self.Set(self.xInt + int(xValue))
        
        
    def Sub(self, xValue):
        self.Set(self.xInt - int(xValue))

    def __int__(self):
        return self.xInt

 
class cMain:
    def __init__(self):
        self.xFile = ""
        
        self.xBitSize = 16
        self.xIntLimit = 2 ** self.xBitSize 
        
        self.xReg = cInt(0, self.xIntLimit)
        self.xAcc = cInt(0, self.xIntLimit)
        
        self.xMem = [cInt(0, self.xIntLimit) for i in range(self.xIntLimit)]
        
        self.xStack = []
        
        self.xString = ""
        
        self.xProgrammIndex = 0
        self.xLables = {}
        
        self.xTotalIndex = 0
    
    
    def ParseLables(self, xCode):
        for xI in range(len(xCode)):
            xLine = xCode[xI]
            
            if xLine.split(" ")[0] == "lab" and len(xLine.split(" ")) > 1:
                self.xLables[str(xLine.split(" ")[1])] = str(xI)
            
        
    def Interpret(self):
        xCode = [x for x in self.xFile.split("\n") if x.replace(" ", "") != ""]
        self.ParseLables(xCode)
        
        try:
            while self.xProgrammIndex < len(xCode):
                
                #check for stackoverflow
                if len(self.xStack) >= self.xIntLimit:
                    raise _Error("Stack overflow")
                
                
                
                xLine = xCode[self.xProgrammIndex]
                
                xInst = None
                xAttr = None
                
                #get inst and attr
                if len(xLine.split(" ")) > 0:
                    xInst = xLine.split(" ")[0]
                
                if len(xLine.split(" ")) > 1:
                    xAttr = xLine.split(" ")[1]
                
                if self.Debug:
                    print("Acc" + str(self.xAcc.xInt) + ", Reg" + str(self.xReg.xInt) + ", Prog" + hex(self.xProgrammIndex) + ": " + str(xLine), end = "")
                    input()
                    
                #execute inst
                if xInst == "set":
                    self.xReg.Set(int(xAttr))
                    
                elif xInst == "add":
                    self.xAcc.Add(self.xReg)
                
                elif xInst == "sub":
                    self.xAcc.Sub(self.xReg)
                
                elif xInst == "shg":
                    self.xAcc.Set(int(self.xAcc) * 2)
                    
                elif xInst == "shs":
                    self.xAcc.Set(int(self.xAcc) // 2)
                
                elif xInst == "lor":
                    self.xAcc.Set(int(self.xAcc) | int(self.xReg))
    
                elif xInst == "and":
                    self.xAcc.Set(int(self.xAcc) & int(self.xReg))
    
                elif xInst == "xor":
                    self.xAcc.Set(int(self.xAcc) ^ int(self.xReg))
    
                elif xInst == "not":
                    xAccBin = bin(int(self.xAcc))[2:]
                    xFixLenAccBin = "0" * (self.xBitSize - len(xAccBin)) + xAccBin
                    
                    
                    xInverted = []
                    for xI in xFixLenAccBin:
                        if xI == "0":
                            xInverted.append("1")
                        
                        elif xI == "1":
                            xInverted.append("0")

                    self.xAcc.Set(int("".join(xInverted), 2))
    
                    
            
                elif xInst == "lDA":
                    self.xAcc.Set(int(self.xMem[int(xAttr)]))
                
                elif xInst == "lDR":
                    self.xReg.Set(int(self.xMem[int(xAttr)]))
                
                elif xInst == "sAD":
                    self.xMem[int(xAttr)].Set(self.xAcc)
                
                elif xInst == "sRD":
                    self.xMem[int(xAttr)].Set(self.xReg)
     
                elif xInst == "lPA":
                    self.xAcc.Set(int(self.xMem[int(self.xMem[int(xAttr)])]))
                
                elif xInst == "lPR":
                    self.xReg.Set(int(self.xMem[int(self.xMem[int(xAttr)])]))
    
                elif xInst == "sAP":
                    self.xMem[int(self.xMem[int(xAttr)])].Set(int(self.xAcc))
                
                elif xInst == "sRP":
                    self.xMem[int(self.xMem[int(xAttr)])].Set(int(self.xReg))
    
                
                elif xInst == "out":
                    print(int(self.xMem[int(xAttr)]))
                
                elif xInst == "inp":
                    xInput = int(input(">>>"))
                    self.xMem[int(xAttr)].Set(xInput)
                
                elif xInst == "got":
                    self.xProgrammIndex = int(self.xLables[str(xAttr)])
                    continue
                
                elif xInst == "jm0":
                    if int(self.xAcc) == 0:
                        self.xProgrammIndex = int(self.xLables[str(xAttr)])
                        continue
                    
                    
                elif xInst == "jmA":
                    if int(self.xAcc) == int(self.xReg):
                        self.xProgrammIndex = int(self.xLables[str(xAttr)])
                        continue
                  
                elif xInst == "jmG":
                    if int(self.xAcc) > int(self.xReg):
                        self.xProgrammIndex = int(self.xLables[str(xAttr)])
                        continue
                
                elif xInst == "jmL":
                    if int(self.xAcc) < int(self.xReg):
                        self.xProgrammIndex = int(self.xLables[str(xAttr)])
                        continue
    
                        
                elif xInst == "brk":
                    break
                    
                elif xInst == "clr":
                    self.xReg.Set(0)
                    self.xAcc.Set(0)
                
                elif xInst == "jmS":
                    self.xStack.append((self.xProgrammIndex + 1) * 2)
                    self.xProgrammIndex = int(self.xLables[str(xAttr)])
                    continue
                    
                    
                elif xInst == "ret":
                    if len(self.xStack) != 0:
                        self.xProgrammIndex = int(self.xStack.pop() / 2)
                        continue
                        
                elif xInst == "pha":
                    self.xStack.append(int(self.xAcc))
                    
                elif xInst == "pla":
                    if len(self.xStack) != 0:
                        self.xAcc.Set(int(self.xStack.pop()))
                
                elif xInst == "putstr":
                    print(chr(int(self.xAcc)), end = "")
                
                                
                self.xProgrammIndex += 1
                self.xTotalIndex += 1

        except KeyboardInterrupt:
            pass
        
        #print("Programm took " + str(self.xTotalIndex) + " Cycles to complete")
        
        
        if m.MemDump:
            print(self.xMem)
                
        
if __name__ == '__main__':
    import sys, os
    xArgv = sys.argv
    xDatapath = None
    
    try:
        for xI in range(len(xArgv)):
            if xArgv[xI] == "--file":
                xDatapath = str(xArgv[xI + 1])
        
        
        xFile = open(xDatapath, "r").read()
    
    except Exception:
        print("Error while loading file")
        exit()
    
    try:
        m = cMain()
        m.xFile = xFile
        m.MemDump = "--dump" in xArgv
        m.Debug = "--debug" in xArgv
        
        m.Interpret()
            
                
    except Exception:
        raise _Error("Error")
    
    
    