from analyzer import Analyzer

analyzer = Analyzer()
analyzer.set_callibration(0, (737,539))
analyzer.set_callibration(1, (42, 119))
print(analyzer.convert_coordinates((300, 400)))
