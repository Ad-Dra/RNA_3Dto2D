import argparse
import os
import sys
import re

def extractBpseqFromBpseq(chain):
    """
    Questa funzione ritorna la catena e i legami da un file che contiene la struttura secondaria in formato bpseq
    """

    triplets = []
    lines = chain.split('\n')
    for line in lines:
        # Legge la terna di numeri da ogni linea che non è un commento (#)
        if len(line) > 0 and line[0] != '#':
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
    """
    Questa funzione legge la catena e i legami da un file che contiene la struttura secondaria in formato aas
    e ritorna una lista di terne in formato bpseq
    """
    for line in chain.strip().split('\n'):
        if len(line) > 0 and line[0] != '#':
            sequence = line
            break

    # Estrae la lista di coppie numero-lettera usando le espressioni regolari
    couples = re.findall(r'\((\d+),(\d+)\)', chain)
    couples = [(int(num), int(letter)) for num, letter in couples]

    triplets = []
    for index, char in enumerate(sequence, start=1):
        num = next((couple[0] for couple in couples if couple[1] == index), 0)
        triplet = [index, char, num]
        triplets.append(triplet)

    return triplets

def get2dFromInputFile(inputPath):
    """
    Questa funzione ritorna la struttura secondaria in stile di terne bpseq 
    """
    # Controlla che il file di input esiste
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
    """
    Questa funzione ritorna True se il file è in formato aas 
    """

    for line in file_content.strip().split('\n'):
        if len(line) > 0 and line[0] != '#':
            # Aas inizia con una lettera
            if str.isalpha(line[0]): 
                return True
            else:
                return False
    return False

def isBpseq(file_content):
    """
    Questa funzione ritorna True se il file è in formato bpseq 
    """

    for line in file_content.strip().split('\n'):
        if len(line) > 0 and line[0] != '#':
            # Bpseq inizia con un carattere numerico
            if str.isnumeric(line[0]): 
                return True
            else:
                return False
    return False

def write_Tkz_txt(bpseq, filename):
    """
    Questa funzione genera il file in formato tkz a partire da un bpseq
    """
    res = f"\\begin{{tikzpicture}}\n"

    i = 0
    si = bpseq[0][0]
    li = bpseq[-1][0]
    # Aggiungi un nodo per ogni base nella sequenza con lettera e numero
    for n1,b,n2 in bpseq:
        res += f"\t\\node [draw, fill=black, circle] ({n1}) at ({i}, 0) " + "{}" + ";\n"
        res += f"\t\\node [] ({n1}a) at ({i}, -0.5) {{{b}}};\n"
        res += f"\t\\node [] ({n1}b) at ({i}, -1) {{{n1}}};\n"
        i = i+1

    res += f"\t\\draw ({si}.center) to ({li}.center);\n"
    temp = []

    # Aggiungi un arco per ogni legame
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

    print("Tkz written successfully!")

def write_Tkz_with_holes(bpseq, filename):
    """
    Questa funzione genera il file in formato tkz con "buchi" a partire da un bpseq
    """
    res = f"\\begin{{tikzpicture}}\n\t\\node [] (h1) at (0, 0) " + "{}" + ";\n\t\\node [] (h1a) at (0, -0.5) {$\Box$};\n\t\\node [] (h1b) at (0, -1) {$1$};\n"

    values = []
    # Ordina le basi che formano legami
    for n1, b, n2 in bpseq:
        if n2 != 0:
            values.append(n1)
            values.append(n2)
    values.sort()

    i = 1
    h = 0
    
    # Disegna un nodo per una base legata seguito da un nodo vuoto per rappresentare un buco
    for val in values:
        res += f"\t\\node [draw, fill=black, circle] ({val}) at ({i+h}, 0) " + "{}" + ";\n"
        res += f"\t\\node [] (h{h+2}) at ({h+i+1}, 0) "+"{}"+f";\n\t\\node [] (h{h+2}a) at ({h+i+1}, -0.5)"+"{$\Box$};\n\t\\node []"+f"(h{h+2}b) at ({h+i+1}, -1)"+"{$"+f"{h+2}"+"$};\n"
        i = i + 1
        h = h + 1

    res += f"\t\\draw (h1.center) to (h{h+1}.center);\n"
    temp = []

    # Disegna un arco per ogni legame fra basi
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

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Description of your program')
    parser.add_argument('input_path', help='input paths of the files containing the 2d structure')
    parser.add_argument('output_path', help='output path of the file in which the program will produce the output')
    parser.add_argument('-b', action='store_true', help="generates tkz to show the section in witch new bonds can be formed instead of every single base of the chain")
    args = parser.parse_args()

    outputPath = args.output_path
    inputPath = args.input_path
    structure_with_holes = args.b

    # Calcolo il formato bpseq dal file di input
    chain = get2dFromInputFile(inputPath)

    if not args.b:
        write_Tkz_txt(chain, outputPath)
    else:
        # Se il flag "-b" è presente produco output con "buchi"
        write_Tkz_with_holes(chain, outputPath)