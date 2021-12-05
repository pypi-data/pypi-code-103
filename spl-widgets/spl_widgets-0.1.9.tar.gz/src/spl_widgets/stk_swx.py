import pandas as pd
import numpy as np
from io import StringIO
import tkinter as tk
from tkinter import filedialog
import sys
from subprocess import run

# --- Config --- #
formants = 4
desired_cols=['f0','f1','a1f','f2','a2f','f3','a3f','f4','a4f']
amp_cols = ['a1f','a2f','a3f','a4f']
multipliers = [.7,.4,.2,.1]

def tuneFile(filepath):
	global formants, desired_cols, amp_cols, multipliers

	# --- Read .stk file, and take the info to a dataframe --- #
	with open(filepath, 'r') as reader:
		file_content = ''.join(reader.readlines()[8:])
		df = pd.read_csv(StringIO(file_content), sep='\t')[desired_cols]

	# --- Tune amplitude vals --- #
	amp_max = [max(df[col]) for col in amp_cols]
	for i in range(formants):
		df[amp_cols[i]] = np.where(df[amp_cols[i]] > 30, multipliers[i]/df[amp_cols[i]]*amp_max[i], 0)

	# --- Format df column names and timestamp column --- #
	df.columns = [formants]+['']*8
	df[formants] = [10*i for i in range(len(df.index))]

	# --- Truncate output filepath --- #
	outFilepath = filepath[:-4]

	# --- Write to .tsv, then manually convert to .swx --- #
	df.to_csv(f'{outFilepath}.tsv', index=False, sep='\t')
	run(['mv', f'{outFilepath}.tsv', f'{outFilepath}.swx'], capture_output=False)

	return outFilepath

def main():
	# --- Get filepath to .stk file --- #
	root = tk.Tk()
	root.focus_force()
	root.wm_geometry("0x0+0+0")

	if 'folder' in sys.argv:
		filepath = filedialog.askdirectory()
		if filepath == '': return False

		filesInDir = str(run(['ls', filepath], capture_output=True).stdout)[2:-1].split('\\n')[:-1]
		operableFiles = [file for file in filesInDir if '.stk' in file]

		for file in operableFiles:
			tuneFile(f'{filepath}/{file}')

		print('\nCompatible files have been successfully converted')

	else:
		filepath=filedialog.askopenfilename(filetypes=[('','.stk')])
		if filepath == '': return False

		outFilepath = tuneFile(filepath)
		print('\n'+f'File written to {outFilepath}.swx.')

	# --- Display completion message, open .swx file/dir if user chooses --- #
	if input('Open Output? (y/n): ').lower() == 'y':
		run(['open', outFilepath], capture_output=False)

if __name__ == '__main__':
	main()
