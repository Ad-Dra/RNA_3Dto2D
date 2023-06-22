import argparse
import os
import sys
import re

def extractBpseqFromBpseq(chain):
    triplets = []
    lines = chain.split('\n')
    for line in lines:
        parts = line.split()
        if len(parts) == 3:
            try:
                num1 = int(parts[0])
                char = parts[1]
                num2 = int(parts[2])
                triplets.append([num1, char, num2])
            except ValueError:
                pass
    return triplets

def extractBpseqFromAas(chain):
    # Extract the sequence of characters
    sequence = chain.strip().split('\n')[0]

    # Extract the list of number-letter couples using regular expressions
    couples = re.findall(r'\((\d+),(\d+)\)', chain)
    couples = [(int(num), int(letter)) for num, letter in couples]

    triplets = []
    for index, char in enumerate(sequence, start=1):
        num = next((couple[0] for couple in couples if couple[1] == index), 0)
        triplet = [index, char, num]
        triplets.append(triplet)

    return triplets

def get2dFromInputFile(inputPath):
        
    if not inputPath.endswith('.txt'):
        inputPath += ".txt"

    if not os.path.isfile(inputPath):
        print(f"Error: Invalid file path: {inputPath}")
        sys.exit()

    with open(inputPath, 'r') as file:
        content = file.read()

        if str.isdigit(content[0]):
            bpseq = extractBpseqFromBpseq(content)
        elif str.isalpha(content[0]):
            bpseq = extractBpseqFromAas(content)

    return bpseq

def write_Tkz_txt(bpseq, filename):
    res = f"\\begin{{tikzpicture}}\n\t\\begin{{pgfonlayer}}{{nodelayer}}\n"

    i = 0
    si = bpseq[0][0]
    li = bpseq[-1][0]
    for n1,b,n2 in bpseq:
        res += f"\t\t\\node [draw, fill=black, circle] ({n1}) at ({i}, 0) " + "{}" + ";\n"
        res += f"\t\t\\node [style=none] ({n1}a) at ({i}, -1) {{{b}}};\n"
        res += f"\t\t\\node [style=none] ({n1}b) at ({i}, -2) {{{n1}}};\n"
        i = i+1

    res += f"\t\end{{pgfonlayer}}\t\n\\begin{{pgfonlayer}}{{edgelayer}}\n\t\t\draw ({si}.center) to ({li}.center);\n"
    temp = []

    for n1,b,n2 in bpseq:
        if(int(n2) != 0 and n1 not in temp):
            temp.append(n2)
            if n2 > n1:
                res += f"\t\t\draw [bend left=90, looseness=2.00] ({n1}.center) to ({n2}.center);\n"
            else:
                res += f"\t\t\draw [bend left=90, looseness=2.00] ({n2}.center) to ({n1}.center);\n"

    res += f"\t\end{{pgfonlayer}}\n\end{{tikzpicture}}"

    with open(filename,'w') as f:
        f.write(res)

    print("Tkz written successfully ")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Description of your program')
    parser.add_argument('input_path', help='input paths of the files containing the 2d structure')
    parser.add_argument('output_path', help='output path of the file in which the program will produce the output')
    args = parser.parse_args()

    outputPath = args.output_path

    inputPath = args.input_path

    chain = get2dFromInputFile(inputPath)

    write_Tkz_txt(chain, outputPath)