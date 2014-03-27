import types
import weakref
import os


class GenerateTestCode(object):
    def __init__(self):
        self.indent = 4 * ' '
        self.class_indent = 0
        self.def_indent = 0
        self.fh = None

    def __RemoveRedundant(self, astr):
        return astr.replace(' ','').replace('\n','')

    def WriteTestClass(self, testClass):
        self.testClass = testClass
        self.__WriteClass(testClass)
        tmp = [x for x in dir(testClass) if x[0] != '_']
        listFunc = [getattr(testClass, x) for x in tmp if type(getattr(testClass, x)) is types.UnboundMethodType]
        for func in listFunc:
            self.__WriteDef(func)
        self.__FinishClass()

    def __WriteClass(self, testClass):
        self.class_indent += 1
        self.fh.write('class Test' + testClass.__name__ + '(unittest.TestCase):\n' + self.class_indent * self.indent)

    def __WriteDef(self, testFunc):
        if testFunc.__doc__:
            dictInfo = eval(self.__RemoveRedundant(testFunc.__doc__)) ## para. parser todo
            for item in dictInfo.items():
                self.def_indent += 1
                indent = self.class_indent + self.def_indent
                self.fh.write('def test' + testFunc.__name__ + '__' + str(item[0]) + '(self):\n' + indent * self.indent)
                self.fh.write('instance = %s.%s(%s)\n%s' % (self.testClass.__module__, self.testClass.__name__, '', indent * self.indent))  ##need get __init__ info   todo
                self.fh.write('self.assertEqual(%s.%s(%s), %s, \'%s test fail\')\n%s' %
                    (
                        'instance',
                        testFunc.__name__,
                        str(item[1]['input']),
                        str(item[1]['output']),
                        testFunc.__name__ + '__' + str(item[0]),
                        indent * self.indent
                    ))
                self.__FinishDef()

    def __FinishClass(self):
        self.fh.seek(-(self.class_indent + self.def_indent) * len(self.indent), 1)
        self.class_indent -= 1
        self.fh.write('\n')

    def __FinishDef(self):
        self.fh.seek(-(self.class_indent + self.def_indent) * len(self.indent), 1)
        self.def_indent -= 1
        self.fh.write('\n')
        self.fh.write((self.class_indent + self.def_indent) * self.indent)
    def Finish(self):
        self.fh.write('if __name__ == \'__main__\':\n\tunittest.main()')

class TestInfoExtractor(object):
    def __init__(self):
        self.listClass = []
        self.listFunc = []

    def Extracting(self, module):
        tmp = [x for x in dir(module) if x[0] != '_']
        self.listClass = [getattr(module, x) for x in tmp if type(getattr(module, x)) is types.TypeType]
        self.listFunc = [getattr(module, x) for x in tmp if type(getattr(module, x)) is types.FunctionType]

class AutoTestGer(object):
    def __init__(self, testFrameName='unittest'):
        self.testFrameName = testFrameName
        self.cExtractor = TestInfoExtractor()
        self.cGer = GenerateTestCode()
        self.outFileName = None
        self.testFileName = None

    def SetTestFile(self, testFileName):
        self.testFileName = testFileName

    def SetOutFile(self, outFileName):
        self.outFileName = outFileName

    def Relax(self):
        with open(self.outFileName, 'w') as fh:
            moduleName = self.testFileName[:-3]
            fh.write('import %s\n' % self.testFrameName)
            fh.write('import %s\n' % moduleName)
            fh.write(2 * '\n')
            module = __import__(moduleName)
            self.cExtractor.Extracting(module)
            self.cGer.fh = weakref.proxy(fh)
            self.cGer.WriteTestClass(self.cExtractor.listClass[0])
            self.cGer.Finish()
        os.system('python %s' % self.outFileName)


if __name__ == '__main__':
    a = AutoTestGer()
    a.SetTestFile('demo.py')
    a.SetOutFile('test.py')
    a.Relax()
