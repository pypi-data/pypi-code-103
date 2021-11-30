#!/usr/bin/python  
from gtts import gTTS  
import sys, getopt, requests, cgi, os, csv  
  
def main():  

	argv = sys.argv[1:]

	vocabulary = ''  
	output = ''  
	csv = ''  
  
	try:  
		opts, args = getopt.getopt(argv, "hd:o:c:", ["vocab=", "ofile=", "csv="])  
	except getopt.GetoptError:  
		showInstruction()  
	for opt, arg in opts:  
		if opt == '-h':  
			showInstruction()  
		elif opt in ("-d", "--vocab"):  
		 	vocabulary = arg  
		elif opt in ("-o", "--ofile"):  
			output = arg  
		elif opt in ("-c", "--csv"):  
			csv = arg  
  
	if csv:  
		downloadMp3FromCSV(csv, output)  
	else:   
		downloadMp3(vocabulary, output)

def downloadMp3(vocab, output):
	if not vocab:  
		showInstruction()

	tts_en = gTTS(vocab, lang='en', tld='ca')

	filename = "%s.mp3" % vocab  
	if output:
		makedirIfNeeded(output)
		filename = output + os.sep + filename

	tts_en.save(filename)
	  
def downloadMp3FromCSV(input, output):  
	vocabList = getVocabularyList(input)  
  
	for vocab in vocabList:  
		downloadMp3(vocab, output)  
  
def getVocabularyList(csvPath):  
	vocabList = []
  
	with open(csvPath, newline='') as csvFile:  
		csvFile = csv.reader(csvFile)  
		rows = list(csvFile)  
  
		for row in rows:  
			for item in row:  
				vocabList.append(item)  
  
	return vocabList  
  
def makedirIfNeeded(output):  
	if not os.path.isdir(output):  
		os.makedirs(output)		  
  
def showInstruction():  
	print('[-c <csv_file_path> || -d <vocabulary>] -o <output_directory>')  
	sys.exit()  
  
if __name__ == "__main__":  
	main()
