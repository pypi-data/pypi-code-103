import os,sys
from io import StringIO
class csv2cleartable:
    def printtable(message):
        #finalmessage=""
        #finalmessage=finalmessage +
        term_size = os.get_terminal_size()
        print('=' * term_size.columns)
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
                        print('=' * term_size.columns)
                        flag = 1
                elif word != '':
                   #finalmessage=finalmessage+str('{:>16}'.format(word),end ="|")
                    print('{:>16}'.format(word),end ="|")
                else:
                    print("\t\t\t",end =" ")
            
        print('=' * term_size.columns)
            
    def finalprinttable(self,message):
        old_stdout = sys.stdout
        new_stdout = StringIO()
        sys.stdout = new_stdout
        self.printtable(message)
        output = new_stdout.getvalue()
        sys.stdout = old_stdout
        return output   