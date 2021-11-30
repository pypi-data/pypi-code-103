import os
import io
import typing
import numpy as np
import cv2
import numpy as np
import pdf2image
import time
import pytesseract
import yaml
import json
import difflib
import unidecode
import matplotlib.pyplot as plt
import PIL

# print("Hello sheet music")

def generateImagesFromPdf(pdfPath, outputDir, startPage, endPage):
	print("Generating images from ", pdfPath, "...", sep="")
	print()
	images = pdf2image.convert_from_path(pdfPath, dpi=200, first_page=startPage, last_page=endPage)
	generatedImages = []
	for i in range(len(images)):
		path = f"{outputDir}/page_{i+1}.jpg"
		print("Generated image from pdf:", path)
		images[i].save(path)
		generatedImages.append(path)
	print()
	return generatedImages

def textRecognizer(imagePath):
	img = cv2.imread(imagePath)
	imgWithBoxes = img.copy()
	res = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
	filtered = {}
	for key in res:
		filtered[key] = []
	for i in range(len(res["text"])):
		if int(res["conf"][i]) > 10 and res["text"][i].strip(" ") != "":
			for key in res:
				filtered[key].append(res[key][i])
			x1 = res["left"][i]
			y1 = res["top"][i]
			x2 = x1 + res["width"][i]
			y2 = y1 + res["height"][i]
			print(x1, y1, x2, y2)
			cv2.rectangle(imgWithBoxes, (x1, y1), (x2, y2), (0, 0, 255), thickness=2) # (, res["top"]), (res["left"] + , res["top"] + res["width"]), (0, 0, 255))
	for key in filtered:
		print("{:>10}".format(key), end=": ")
		for i in range(len(filtered[key])):
			print("{:>10}".format(filtered[key][i]), end=" ")
		print()
	print(pytesseract.image_to_string(img))
	cv2.imshow("Text recognition", imgWithBoxes)
	cv2.waitKey(0)

def cropImage(img):
	# findContentBox(img)
	return img
	return img[0:len(img)//2, 0:len(img[0])//2]

def processDetectionData(detectionData, img):
	imgWithBoxes = img.copy()
	nicePrint  = "+------------------------------+------------+----------+----------+\n"
	nicePrint += "| text                         | confidence | pos_left | pos_top  |\n"
	nicePrint += "+------------------------------+------------+----------+----------+\n"
	for i in range(len(detectionData["text"])):
		if int(detectionData["level"][i]) == 5:
			x1 = detectionData["left"][i]
			y1 = detectionData["top"][i]
			x2 = x1 + detectionData["width"][i]
			y2 = y1 + detectionData["height"][i]
			cv2.rectangle(imgWithBoxes, (x1, y1), (x2, y2), (0, 0, 255), thickness=2)
			nicePrint += "| {:28} | {:>10} | {:>8} | {:>8} |\n".format(detectionData["text"][i],
				detectionData["conf"][i], detectionData["left"][i], detectionData["top"][i])
	nicePrint += "+------------------------------+------------+----------+----------+\n"
	return imgWithBoxes, nicePrint

class Detection:
	# This class describes a single text detection from tesseract
	# Meaning of variables is same as the raw tesseract output, an explanation can be found here:
	# https://www.tomrochette.com/tesseract-tsv-format

	__level = 1
	__page_num = 1
	__block_num = 0
	__par_num = 0
	__line_num = 0
	__word_num = 0
	__left = 0
	__top = 0
	__width = 0
	__height = 0
	__conf = 0
	__text = ""

	def __init__(self, detectionData, i):
		self.__level = detectionData["level"][i]
		self.__page_num = detectionData["page_num"][i]
		self.__block_num = detectionData["block_num"][i]
		self.__par_num = detectionData["par_num"][i]
		self.__line_num = detectionData["line_num"][i]
		self.__word_num = detectionData["word_num"][i]
		self.__left = detectionData["left"][i]
		self.__top = detectionData["top"][i]
		self.__width = detectionData["width"][i]
		self.__height = detectionData["height"][i]
		self.__conf = detectionData["conf"][i]
		self.__text = detectionData["text"][i]
	
	# Straightforward get functions
	def level(self): return self.__level
	def page_num(self): return self.__page_num
	def block_num(self): return self.__block_num
	def par_num(self): return self.__par_num
	def line_num(self): return self.__line_num
	def word_num(self): return self.__word_num
	def left(self): return self.__left
	def top(self): return self.__top
	def width(self): return self.__width
	def height(self): return self.__height
	def conf(self): return self.__conf
	def text(self): return self.__text

	# Useful other get functions:
	def right(self): return self.__left + self.__width
	def bot(self): return self.__top + self.__height



def isSimilarEnough(detectedText, keyword):
	return difflib.SequenceMatcher(None, unidecode.unidecode_expect_ascii(detectedText.lower()),
		unidecode.unidecode_expect_ascii(keyword.lower())).ratio() > 0.9
		# or \
	    #        difflib.SequenceMatcher(None, detectedText.lower()+"s", keyword.lower()).ratio() > 0.9 or \
	    #        difflib.SequenceMatcher(None, detectedText.lower()+"es", keyword.lower()).ratio() > 0.9 or \
	    #        difflib.SequenceMatcher(None, detectedText.lower()+"r", keyword.lower()).ratio() > 0.9 or \
	    #        difflib.SequenceMatcher(None, detectedText.lower()+"er", keyword.lower()).ratio() > 0.9 or \
	    #        difflib.SequenceMatcher(None, detectedText.lower()+"as", keyword.lower()).ratio() > 0.9
	return detectedText.lower() == keyword.lower()

def predictParts(detectionData, instruments, imageWidth, imageHeight):
	# return partNames, instrumentses
	# Here, input instruments should be a dict where the keyes are instrument names and values are lists of keywords
	# The instrument names could also be the instruments id in the database, it is only used as an identifier

	# Firstly, convert detectionData to handy Detection objects
	detections = []
	for i in range(len(detectionData["text"])):
		detections.append(Detection(detectionData, i))

	# Secondly, gather a list of all matches between detected texts and instruments
	matches = []
	exceptionMatches = []
	for instrument in instruments:
		for j in range(len(instruments[instrument]["include"])):
			keyword = instruments[instrument]["include"][j]
			N = len(keyword.split(" "))
			for i in range(len(detections)-(N-1)):
				if detections[i].level() != 5: continue;
				blockNr = detections[i].block_num()
				sameBlock = True
				for k in range(1, N):
					if detections[i+k].block_num() != blockNr:
						sameBlock = False;
						break;
				if sameBlock:
					detectedWords = detections[i:i+N]
					for l in range(len(detectedWords)):
						detectedWords[l] = detectedWords[l].text()
					detectedText = " ".join(detectedWords)
					if isSimilarEnough(detectedText, keyword):
						matches.append({"i": i, "instrument": instrument, "keyword": keyword})

		for j in range(len(instruments[instrument]["exceptions"])):
			keyword = instruments[instrument]["exceptions"][j]
			N = len(keyword.split(" "))
			for i in range(len(detections)-(N-1)):
				if detections[i].level() != 5: continue;
				blockNr = detections[i].block_num()
				sameBlock = True
				for k in range(1, N):
					if detections[i+k].block_num() != blockNr:
						sameBlock = False;
						break;
				if sameBlock:
					detectedWords = detections[i:i+N]
					for k in range(len(detectedWords)):
						detectedWords[k] = detectedWords[k].text()
					detectedText = " ".join(detectedWords)
					if isSimilarEnough(detectedText, keyword):
						exceptionMatches.append({"i": i, "instrument": instrument, "keyword": keyword})

	# Lastly, predict how many, what names, and for what instruments the parts are
	if len(matches) == 0:
		return [], []
	else:
		blocksWithMatches = set()
		for match in matches:
			excepted = False
			for exception in exceptionMatches:
				if match["instrument"] == exception["instrument"] and \
					detections[match["i"]].block_num() == detections[exception["i"]].block_num():
					excepted = True; break
			if not excepted:
				blocksWithMatches.add(detections[match["i"]].block_num())
			
		nrOfBlocksWithMatches = len(blocksWithMatches)
		if nrOfBlocksWithMatches <= 2:
			partNames = []
			instrumentses = []
			for blockNr in blocksWithMatches:
				partName = []
				instrumentsWithMatchesInBlock = set()
				for i in range(len(detections)):
					if detections[i].level() == 5 and detections[i].block_num() == blockNr:
						partName.append(detections[i].text())
						for match in matches:
							if match["i"] == i:
								excepted = False
								for exception in exceptionMatches:
									if exception["instrument"] == match["instrument"] and \
										detections[exception["i"]].block_num() == blockNr:
										excepted = True; break
								if not excepted:
									instrumentsWithMatchesInBlock.add(match["instrument"])
				partName = " ".join(partName)
				partNames.append(partName)
				instrumentses.append(list(instrumentsWithMatchesInBlock))
			return partNames, instrumentses
		else:
			# Its probably a full score
			return ["full score"], [["full score"]]

# define a function which returns an image as numpy array from figure
def get_img_from_pyplot_fig(dpi=180):
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=dpi)
    buf.seek(0)
    img_arr = np.frombuffer(buf.getvalue(), dtype=np.uint8)
    buf.close()
    img = cv2.imdecode(img_arr, 1)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img

# Accepts an image matrix
# Finds a bounding box for where the main content of the page most likely is
def findContentBox(img):
	# print("yo")
	# print("hmm")
	# print("test: ", test)
	# img = np.array([[[255, 255, 255], [2, 3, 4]], [[255, 0, 0], [4, 5, 6]]])
	img = np.average(img, axis=2)       # Convert to black-white
	img = 255 - img
	rows = np.average(img, axis=1)
	cols = np.average(img, axis=0)
	# x_min = np.percentile(img, 95, axis=1)  # Find 95th percentile of data
	# x_max = np.percentile(img, 5, axis=1)  # Find 5th percentile of data
	rows_hist, _ = np.histogram(np.arange(rows.shape[0]), weights=rows, bins=16, density=False)
	cols_hist, _ = np.histogram(np.arange(cols.shape[0]), weights=cols, bins=32, density=False)
	# img[:,:] = img[:,:,:]
	print("img:\n", img)
	# print("x:", x_min, x_max)
	print("rows:", rows)
	print("cols:", cols)
	print("rows_hist:\n", rows_hist)
	print("cols_hist:\n", cols_hist)
	# print(img[2000, 1000, 1])
	print("shape:", img.shape)

	plt.clf()
	plt.bar(np.arange(rows_hist.shape[0]), rows_hist)
	histogram = get_img_from_pyplot_fig()
	# buf = io.BytesIO()
	# plt.savefig(buf, format="png", dpi=100)
	# buf.seek(0)
	# histogram = np.frombuffer(buf.getvalue(), dtype=np.uint8)
	# print("hist 1:", histogram, histogram.shape[0])
	# histogram = cv2.imdecode(histogram, cv2.IMREAD_UNCHANGED)
	# buf.close()
	# print("hist 2:", histogram)
	# histogram = cv2.cvtColor(histogram, cv2.COLOR_BGR2RGB)
	# print("hist 3:", histogram)

	kernel = np.ones((200, 200), np.float32)/(200 * 200)
	# img_filtered = cv2.filter2D(img, -1, kernel)
	kernel_size = (np.array((img.shape[1], img.shape[0])) //6) * 2 + 1
	img_filtered = cv2.GaussianBlur(img, kernel_size, 0)
	img_filtered_rows = np.average(img_filtered, axis=1)
	img_filtered_cols = np.average(img_filtered, axis=0)

	plt.clf()
	plt.plot(img_filtered_rows)
	img_filtered_chart = get_img_from_pyplot_fig()

	x = 0
	y = 0
	width = 0
	height = 0

	return x, y, width, height, histogram, 255 - 4 * img_filtered, img_filtered_chart

def predict_parts_in_img(img : io.BytesIO | bytes | PIL.Image.Image, instruments, use_lstm=False, tessdata_dir=None) -> typing.Tuple[list, list]:
	if type(img) is PIL.Image.Image:
		pass
	elif type(img) is io.BytesIO:
		img = PIL.Image.open(img)
	elif type(img) is bytes:
		img = PIL.Image.open(io.BytesIO(img))

	config = "--user-words sheetmusicUploader/instrumentsToLookFor.txt --psm 11 --dpi 96 -l eng"
	if use_lstm: config += " --oem 1"
	if tessdata_dir != None: config += " --tessdata-dir \""+tessdata_dir+"\""
	detection_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT, config=config)

	return predictParts(detection_data, instruments, *img.size)

def processUploadedPdf(pdfPath, imagesDirPath, instruments_file=None, instruments=None, use_lstm=False, tessdata_dir=None):
	"""
	Arguments:
	pdfPath                     - Full path to PDF file
	imagesDirPath               - Full path to output images
	instruments_file (optional) - Full path to instruments file. Accepted formats: YAML (.yaml, .yml), JSON (.json)
	instruments      (optional) - Dictionary of instruments. Will override any provided instruments file.
	- If neither instruments_file nor instruments is provided a default instruments file will be used.
	use_lstm         (optional) - Use LSTM instead of legacy engine mode.
	tessdata_dir     (optional) - Full path to tessdata directory. If not provided, whatever the environment variable TESSDATA_DIR will be used.

	Returns:
	parts                       - A list of dictionaries { "name": "[name]", "fromPage": i, "toPage": j } describing each part
	instrumentsDefaultParts     - A dictionary { ..., "instrument_i": j, ... }, where j is the index in the parts list for the default part for instrument_i.
	"""
	if instruments == None:
		if instruments_file == None:
			with open(os.path.join(os.path.dirname(__file__), "instruments.yaml")) as file:
				instruments = yaml.safe_load(file)
		else:
			with open(instruments_file) as file:
				_, file_extension = os.path.splitext(instruments_file)
				if file_extension.lower() in [".yaml", ".yml"]:
					instruments = yaml.safe_load(file)
				elif file_extension.lower() in [".json"]:
					instruments = json.load(file)
				else:
					raise Exception("Instruments file with extension {} is not supported".format(file_extension))
	parts = []
	instrumentsDefaultParts = { instrument: None for instrument in instruments }
	instrumentsDefaultParts["full score"] = None
	imagePaths = generateImagesFromPdf(pdfPath, imagesDirPath, 1, None)
	lastPartName = ""
	lastPartNamePage = 0
	lastInstruments = []
	for i in range(len(imagePaths)):
		print("side", i+1, "av", len(imagePaths))
		print("cropper...")
		img = cropImage(cv2.imread(imagePaths[i]))
		print("detecter...")
		config = "--user-words sheetmusicUploader/instrumentsToLookFor.txt --psm 11 --dpi 96 -l eng"
		if use_lstm: config += " --oem 1"
		if tessdata_dir != None: config += " --tessdata-dir \""+tessdata_dir+"\""
		detectionData = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT, config=config)
		print("predicter...")
		partNames, instrumentses = predictParts(detectionData, instruments, img.shape[1], img.shape[0])
		print("partNames:", partNames, "instrumentses:", instrumentses)
		for j in range(len(partNames)):
			print(j, lastPartName)
			if lastPartName:
				parts.append({
					"name": lastPartName,
					"fromPage": lastPartNamePage,
					"toPage": i if j == 0 else i+1
				})
				for k in range(len(lastInstruments)):
					if instrumentsDefaultParts[lastInstruments[k]] == None:
						instrumentsDefaultParts[lastInstruments[k]] = len(parts)-1
			lastPartName = partNames[j]
			lastPartNamePage = i+1
			lastInstruments = instrumentses[j]
	if lastPartName:
		parts.append({
			"name": lastPartName,
			"fromPage": lastPartNamePage,
			"toPage": len(imagePaths)
		})
		for k in range(len(lastInstruments)):
			if instrumentsDefaultParts[lastInstruments[k]] == None:
				instrumentsDefaultParts[lastInstruments[k]] = len(parts)-1
	return parts, instrumentsDefaultParts

