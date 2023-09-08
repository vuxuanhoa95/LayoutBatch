from io import TextIOWrapper


logfile = open('temp.log', 'w')

print(logfile, type(logfile), isinstance(logfile, TextIOWrapper))

logfile.close()