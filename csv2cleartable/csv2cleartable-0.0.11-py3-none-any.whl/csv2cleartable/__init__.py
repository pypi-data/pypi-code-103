#!/usr/bin/python3 


import os
from io import StringIO
import sys




class csv2table:
    def printtable(self,message):
        #finalmessage=""
        #finalmessage=finalmessage +
        print('=' * 120)
        flag=0
        for line in message.split('\n'):
            line=line+";"
            line_list = line.split(';')
        # print(line_list)
            line_list.append("End")
        #  print(line_list)
        
            for word in line_list:
                if word == 'End':
                    print("\n")
                    if flag == 0:
                        flag = 1
                        print('=' * 120)
                elif word != '':
                   #finalmessage=finalmessage+str('{:>16}'.format(word),end ="|")
                    print('{:>16}'.format(word),end ="|")
                else:
                    print("\t\t\t",end =" ")
        
        print('=' * 120)
        
    def finalprinttable(self,message):
        old_stdout = sys.stdout
        new_stdout = StringIO()
        sys.stdout = new_stdout

        self.printtable(message)

        output = new_stdout.getvalue()

        sys.stdout = old_stdout

        return output
        


def main():
 ###
    print("")

    
    

if __name__ == '__main__':
    main()
