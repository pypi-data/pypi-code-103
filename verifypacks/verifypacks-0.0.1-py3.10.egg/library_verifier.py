import json
from piprot.piprot import get_version_and_release_date


class library_version_verifier:
  def __init__(self, file_name):
    self.file_name= file_name

  def openFile(self):
    with open(self.file_name) as f:
        lines = f.readlines() # list containing lines of file
    return lines
   
  def jsonResults(self):
    
    """
    This function return the libraries in the requirements.txt file:
    their version, their newest version and whether or not their are up to date
    as a json file

    """
    listOfPackages = []
    d={}
    lines = self.openFile()
    for line in lines:
      if len(line)>1 and "==" in line:
        columns = [item.strip() for item in line.split('==')]
        library_name = columns[0]
        current_version = columns[1]
        latest_version, r1 = get_version_and_release_date(library_name)
        if latest_version != None:
          d["packageName"] = library_name
          d["currentVersion"]  = current_version
          d["latestVersion"] = latest_version
          if current_version != latest_version:
            outOfDate = True
          else:
            outOfDate = False
          d['outOfDate'] = outOfDate

          json_obj = json.dumps(d, indent=4)
          listOfPackages.append(json_obj)
        #else:
          #print(f"\nLibrary {library_name} is not correct or doesn't exist\n")
          
    return listOfPackages

  def printJson(self):
    
    """
    This function pretty prints the results from the function jsonResults
    
    """
    
    listOfPackages = self.jsonResults()
    for x in listOfPackages:
      print(x)

  def formattedWrong(self):
    
    """
    This function prints the libraries in the requirements.txt file
    which are not formatted properly
    
    """
    listOfPackages = []
    d={}
    lines = self.openFile()
    for line in lines:
        if len(line)>1:
            columns = [item.strip() for item in line.split('==')]
            library_name = columns[0]
            if '==' in line:
                latest_version, r1 = get_version_and_release_date(library_name)
                if latest_version == None:
                    listOfPackages.append(library_name)
            else:
                listOfPackages.append(library_name)
    
    if len(listOfPackages)==0:
        print('All packages are formatted correctly')
    else:
        i=0
        print('\n=======================')
        print("\nThese packages are not formatted correclty in the " + self.file_name +  " file\n")
        for name in listOfPackages:
            i+=1
            print(f'{i} - {name}')
        print('\n=======================\n')

file_name = "requirements.txt"

if __name__ == '__main__':
    p1 = library_version_verifier(file_name)
    p1.printJson()
    #p1.formattedWrong()