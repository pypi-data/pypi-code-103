import csv
import concurrent.futures
from FPE import formatter
from FPE import Format
from timeit import default_timer as timer

dataExample = ['12345678','1112223334445559','CoolUsername','SecurePassword123','Cool@Email.com','1212121211']
dataFormats = [Format.DIGITS,Format.CREDITCARD,Format.LETTERS,Format.STRING,Format.EMAIL,Format.CPR]

mapping_formats = dict(zip(dataFormats, dataExample))

def generate_data(columns,dataFormat,tweak,mode):

    ciphertexts = [columns[0]]

    for text in columns[1:]:
        key = formatter.mode_selector.ff1.get_random_bytes(16)
        ciphertexts.append(formatter.encrypt(text,key,tweak,dataFormat,mode))
    return ciphertexts

def encrypt(columns,key,tweak,dataFormat,mode):

    ciphertexts = [columns[0]]

    for text in columns[1:]:
        ciphertexts.append(formatter.encrypt(text,key,tweak,dataFormat,mode))


    return ciphertexts

def decrypt(columns,key,tweak,dataFormat,mode):

    plaintexts = [columns[0]]

    for text in columns[1:]:
        plaintexts.append(formatter.decrypt(text,key,tweak,dataFormat,mode))

    return plaintexts

def encrypt_csv(csvFilePath,encryptedFilePath,key,tweak,formats,mode):
    start = timer()
    print('Encrypting...')
    n = len(formats)

    data=[]

    keys = [key]*n
    tweaks = [tweak]*n
    modes = [mode]*n

    with open(csvFilePath) as csvFile:
        csvReader = csv.reader(csvFile, delimiter = ';')
        rowCount = 0
        for row in csvReader:
            if (rowCount != 0):
                columnCount = 0
                for column in row:
                    data[columnCount].append(column)
                    columnCount += 1

                #print("%d %d" %(rowCount, columnCount))
            else:
                for column in row:
                    data.append([column])
            
                rowCount += 1

    with concurrent.futures.ProcessPoolExecutor() as executor:
        results = list(executor.map(encrypt,data,keys,tweaks,formats,modes))

        data = results


    with open(encryptedFilePath, 'w',  newline='') as encryptedCSVFile:
        csvWriter = csv.writer(encryptedCSVFile, delimiter = ';')
        for i in range(len(data[0])):
            data2 = []
            for j in range(len(data)):
                #print(i)
                #print(data[j][i])
                data2.append(data[j][i])
            csvWriter.writerow(data2)

    end = timer()
    print('Done in %5.2f seconds' % (end-start))

def decrypt_csv(csvFilePath,decryptedFilePath,key,tweak,formats,mode):
    start = timer()
    print('Decrypting...')
    n = len(formats)

    data=[]

    keys = [key]*n
    tweaks = [tweak]*n
    modes = [mode]*n

    with open(csvFilePath) as csvFile:
        csvReader = csv.reader(csvFile, delimiter = ';')
        rowCount = 0
        for row in csvReader:
            if (rowCount != 0):
                columnCount = 0
                for column in row:
                    data[columnCount].append(column)
                    columnCount += 1

                #print("%d %d" %(rowCount, columnCount))
            else:
                for column in row:
                    data.append([column])
            
                rowCount += 1

    with concurrent.futures.ProcessPoolExecutor() as executor:
        results = list(executor.map(decrypt,data,keys,tweaks,formats,modes))

        data = results


    with open(decryptedFilePath, 'w',  newline='') as decryptedCSVFile:
        csvWriter = csv.writer(decryptedCSVFile, delimiter = ';')
        for i in range(len(data[0])):
            data2 = []
            for j in range(len(data)):
                #print(i)
                #print(data[j][i])
                data2.append(data[j][i])
            csvWriter.writerow(data2)

    end = timer()
    print('Done in %5.2f seconds' % (end-start))

def generate_test_data(csvFilePath,rows,formats,names,tweak,mode):
    start = timer()
    print('Generating...')

    tweaks = [tweak]*len(formats)
    modes = [mode]*len(formats)

    data = [[x] for x in names]

    for i in range(len(names)):
        for _ in range(rows):
            data[i].append(mapping_formats[formats[i]])

    with concurrent.futures.ProcessPoolExecutor() as executor:
        results = list(executor.map(generate_data,data,formats,tweaks,modes))

        data = results



    with open(csvFilePath, 'w',  newline='') as csvFile:
            csvWriter = csv.writer(csvFile, delimiter = ';')
            for i in range(len(data[0])):
                data2 = []
                for j in range(len(data)):
                    #print(i)
                    #print(data[j][i])
                    data2.append(data[j][i])
                csvWriter.writerow(data2)
    
    end = timer()
    print('Done in %5.2f seconds' % (end-start))