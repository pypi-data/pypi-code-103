numbers = {
	0:"0",
	1:"1",
	2:"2",
	3:"3",
	4:"4",
	5:"5",
	6:"6",
	7:"7",
	8:"8",
	9:"9",
	10:"A",
	11:"B",
	12:"C",
	13:"D",
	14:"E",
	15:"F",
	16:"G",
	17:"H",
	18:"I",
	19:"J",
	20:"K",
	21:"L",
	22:"M",
	23:"N",
	24:"O",
	25:"P",
	26:"Q",
	27:"R",
	28:"S",
	29:"T",
	30:"U",
	31:"V",
	32:"W",
	33:"X",
	34:"Y",
	35:"Z"
}

def convert(number,osn):
	new_number = ""
	if number<osn:
		new_number += numbers[number%osn]
		return new_number[::-1]
	while number>=osn:
		new_number += numbers[number%osn]
		number = number//osn
	new_number += numbers[number]
	return new_number[::-1]

def convert_back(number,osn):
	return int(str(number),osn)

def convert_to(number,osn1,osn2):
	new_number = convert_back(number,osn1)
	return convert(int(new_number),osn2)

def dividers(num):
	dividers1 = [x for x in range(1, round(num**0.5) + 1) if num % x == 0]
	dividers2 = [int(num / x) for x in reversed(dividers1) if int(num / x) not in dividers1]
	return dividers1 + dividers2
