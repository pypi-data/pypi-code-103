import csv
class combiner :
    def __init__(self):
        """ only god knows why"""
        pass
    def combine(self,source,output,ignore_title = False):
        """ source should be a list """
        with open(output,"w", newline="") as finalCSV :
            csvwriter = csv.writer(finalCSV)
            file_count = 1
            for f in source:
                with open(f) as sourceFile :
                    CSVreader = csv.reader(sourceFile)
                    line_count = 1
                    for l in CSVreader:
                        if ( ignore_title ==True and file_count > 1 and line_count == 1):
                            pass
                        else:
                            csvwriter.writerow(l)
                        line_count+=1
                file_count +=1