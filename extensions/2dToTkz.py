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

    for line in chain.strip().split('\n'):
        if len(line) > 0 and line[0] != '#':
            sequence = line
            break

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
        
    if not os.path.isfile(inputPath):
        print(f"Error: Invalid file path: {inputPath}")
        sys.exit()

    with open(inputPath, 'r') as file:
        content = file.read()

        if isBpseq(content):
            bpseq = extractBpseqFromBpseq(content)
        elif isAas(content):
            bpseq = extractBpseqFromAas(content)

    return bpseq

def isAas(file_content):
    for line in file_content.strip().split('\n'):
        if len(line) > 0 and line[0] != '#':
            if str.isalpha(line[0]):
                return True
            else:
                return False
    return False

def isBpseq(file_content):
    for line in file_content.strip().split('\n'):
        if len(line) > 0 and line[0] != '#':
            if str.isnumeric(line[0]):
                return True
            else:
                return False
    return False

def write_Tkz_txt(bpseq, filename):
    res = f"\\begin{{tikzpicture}}\n"

    i = 0
    si = bpseq[0][0]
    li = bpseq[-1][0]
    for n1,b,n2 in bpseq:
        res += f"\t\\node [draw, fill=black, circle] ({n1}) at ({i}, 0) " + "{}" + ";\n"
        res += f"\t\\node [] ({n1}a) at ({i}, -0.5) {{{b}}};\n"
        res += f"\t\\node [] ({n1}b) at ({i}, -1) {{{n1}}};\n"
        i = i+1

    res += f"\t\end{{pgfonlayer}}\t\n\\begin{{pgfonlayer}}{{edgelayer}}\n\t\t\draw ({si}.center) to ({li}.center);\n"
    temp = []

    for n1,b,n2 in bpseq:
        if(int(n2) != 0 and n1 not in temp):
            temp.append(n2)
            if n2 > n1:
                res += f"\t\draw [bend left=90, looseness=2.00] ({n1}.center) to ({n2}.center);\n"
            else:
                res += f"\t\draw [bend left=90, looseness=2.00] ({n2}.center) to ({n1}.center);\n"

    res += f"\end{{tikzpicture}}"

    with open(filename,'w') as f:
        f.write(res)

    print("Tkz with holes written successfully!")

def write_Tkz_with_holes(bpseq, filename):
    res = f"\\begin{{tikzpicture}}\n\t\\node [] (h1) at (0, 0) " + "{}" + ";\n\t\\node [] (h1a) at (0, -0.5) {$\Box$};\n\t\\node [] (h1b) at (0, -1) {$1$};\n"

    values = []
    for n1, b, n2 in bpseq:
        if n2 != 0:
            values.append(n1)
            values.append(n2)
    values.sort()

    i = 1
    h = 0
    for val in values:
        res += f"\t\\node [draw, fill=black, circle] ({val}) at ({i+h}, 0) " + "{}" + ";\n"
        res += f"\t\\node [] (h{h+2}) at ({h+i+1}, 0) "+"{}"+f";\n\t\\node [] (h{h+2}a) at ({h+i+1}, -0.5)"+"{$\Box$};\n\t\\node []"+f"(h{h+2}b) at ({h+i+1}, -1)"+"{$"+f"{h+2}"+"$};\n"
        i = i + 1
        h = h + 1

    res += f"\t\\draw (h1.center) to (h{h+1}.center);\n"
    temp = []

    for n1,b,n2 in bpseq:
        if(int(n2) != 0 and n1 not in temp):
            temp.append(n2)
            if n2 > n1:
                res += f"\t\draw [bend left=90, looseness=2.00] ({n1}.center) to ({n2}.center);\n"
            else:
                res += f"\t\draw [bend left=90, looseness=2.00] ({n2}.center) to ({n1}.center);\n"

    res += f"\end{{tikzpicture}}"

    with open(filename,'w') as f:
        f.write(res)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Description of your program')
    parser.add_argument('input_path', help='input paths of the files containing the 2d structure')
    parser.add_argument('output_path', help='output path of the file in which the program will produce the output')
    parser.add_argument('-b', action='store_true', help="generates tkz to show the section in witch new bonds can be formed instead of every single base of the chain")
    args = parser.parse_args()

    outputPath = args.output_path

    inputPath = args.input_path

    structure_with_holes = args.b

    chain = get2dFromInputFile(inputPath)

    if not args.b:
        write_Tkz_txt(chain, outputPath)
    else:
        write_Tkz_with_holes(chain, outputPath)