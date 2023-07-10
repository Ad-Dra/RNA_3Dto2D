import argparse
import os
import sys

from FR3D.fr3d.classifiers.NA_pairwise_interactions import annotate_nt_nt_in_structure, focus_basepair_cutoffs, load_structure, myTimer, simplify_basepair
from FR3D.fr3d.classifiers.hydrogen_bonds import load_ideal_basepair_hydrogen_bonds
from FR3D.fr3d.classifiers.class_limits_2023 import nt_nt_cutoffs
from RNASecodaryStructure import RNASecondaryStructure   # use latest cutoffs

def adapt_category_format(string):
    """
    Adatta il formato delle stringhe di categoria ionvertend la stringa di input in una stringa 
    in modo che la prima letteria è minuscola e le ultime due maiuscole
    """
    
    first_letter = string[0].lower()
    second_letter = string[1].upper()
    third_letter = string[2].upper()
    
    return first_letter + second_letter + third_letter

def extract_triplets(input_string):
    """
    Estrae la sequenza dell'oggetto generato da FR3D tramite parsing di stringhe
    """

    start_index = input_string.find("'p_1': [") 
    end_index = input_string.find("]", start_index)
    section_string = input_string[start_index:end_index+1]

    triplets = []
    objects = section_string.split("), (")
    for obj in objects:
        parts = obj.split("|")
        if len(parts) >= 4:

            number = parts[4]; 
            index = number.find("'")
            if index != -1:
                number = number[:index + len("'")]

            number1 = parts[8]
            index = number1.find("'")
            if index != -1:
                number1 = number1[:index + len("'")]
            
            triplet = [parts[2], parts[3], number.replace("'","")]
            triplet1 = [parts[6], parts[7], number1.replace("'","")]
            
            if triplet not in triplets:
                triplets.append(triplet)
            if triplet1 not in triplets:
                triplets.append(triplet1)

    return triplets

def compute_sequence(chain):
    """
    Ritorna le coppie ['numero', 'base'] di tutta la sequenza della catena di RNA
    """

    sequence = []

    for base in chain:
        pair = []
        pair.append(base[2])
        if (len(base[1]) > 1):
            pair.append(base[1][len(base[1]) - 1])
        else:
            pair.append(base[1])
        sequence.append(pair)

    return sequence

def modelFound(input_string):
    """
    Ritorna l'array contenente tutti i numeri di modello individuati nella catena di RNA
    """

    start_index = input_string.find("'p_1': [")
    end_index = input_string.find("]", start_index)
    section_string = input_string[start_index:end_index+1]

    result = []
    objects = section_string.split("), (")
    for obj in objects:
        parts = obj.split("|")
        if len(parts) >= 4: #controlla che non è None
            model = parts[1]; 
            if model not in result:
                result.append(model)

    return result

def isSameModelNumber(a, model):
    """
    Ritorna True se la base a appartiene al modello model
    """
    # 'a' è un baseid generato da FR3D
    n = a.split("|")
    if str(n[1]) == str(model):
        return True
    else: 
        return False

def extractSecondaryStrincture(pdbid,interaction_to_list_of_tuples,categories,category_to_interactions, modelNumber):
    """
    Ritorna un oggetto di tipo RNASecondaryStructure della catena richiesta
    """

    sequence = compute_sequence(extract_triplets(str(interaction_to_list_of_tuples))) 
    rna_structure = RNASecondaryStructure(sequence, pdbid)

    for category in categories.keys():

        for interaction in category_to_interactions['basepair']:
            inter = interaction
            if category == 'basepair':
                inter = simplify_basepair(interaction)

            if len(categories[category]) == 0 or inter in categories['basepair']:
                for a,b,c in interaction_to_list_of_tuples[interaction]:
                    # Itera fra tutti i legami individuati da FR3D
                    if isSameModelNumber(a, abs(int(modelNumber))):
                        b1 = int((a.split("|"))[4])
                        b2 = int((b.split("|"))[4])
                        # Aggiunge i legami all'oggetto RNASecondaryStructure
                        rna_structure.add_bond(b1, b2, str(inter), int(modelNumber))                
        
        return rna_structure

def adapt_multibond_output(output_formats): 
    """
    Cambia gli output impostati dall'utente nel caso vengono selezionati legami multipli per il formato bpseq
    """

    res = []

    for optf in output_formats:
        if optf == "bpseq":
            if "aas" not in output_formats:
                res.append("aas")
        else:
            res.append(optf)

    return res


def write_txt_output_file(outputFile,pdbid,interaction_to_list_of_tuples,categories,category_to_interactions, cat, opt, allStructure, allAnnotations, mn):
    """
    Richiama le funzioni della classe RNASecondaryStructure per generare 
    i file di output richiesti
    """

    models = modelFound(str(interaction_to_list_of_tuples))

    if (mn == []):
        mn = models

    for model in mn:
        if model not in models:
            return
        model = int(model)
        if len(models) == 1:
            model = -1

        secondary_structure = extractSecondaryStrincture(pdbid,interaction_to_list_of_tuples,categories,category_to_interactions, model)

        if(not allStructure and not allAnnotations): # Se l'utente non specifica -a ne -aa (1 file per ogni legame)
            for c in cat:   
                secondary_structure.write_output_file([c], model, opt, outputFile)

        elif(allAnnotations): # Se l'utente scrive -aa (tutti i legami sullo stesso file + 1 file per ogni legame)
            secondary_structure.write_output_file(cat, model, adapt_multibond_output(opt), outputFile)
            for c in cat:
                secondary_structure.write_output_file([c], model, opt, outputFile)
        
        elif(allStructure): # Se l'utente scrive -a (tutti i legami sullo stesso file)
            secondary_structure.write_output_file(cat, model, adapt_multibond_output(opt), outputFile)                

def generate_output_files(entry_id, inputPath, outputPath, category, opt, allStructure, allAnnotations, mn):
    """
    Utilizza le funzioni di FR3D per calcolare i legami e
    imposta le tipologie di legami richieste dall'utente.
    """
    if isinstance(entry_id,str):
        entry_id = [entry_id]

    # Set up delle categorie richieste fra quelle canoniche
    categories = {}

    Leontis_Westhof_basepairs = ['cWW', 'cSS', 'cHH', 'cHS', 'cHW', 'cSH', 'cSW', 'cWH', 'cWS', 'tSS', 'tHH', 'tHS', 'tHW', 'tSH', 'tSW', 'tWH', 'tWS', 'tWW']
    
    cat = Leontis_Westhof_basepairs
    
    if category != 'basepair':
        cat = category.split(",")
        for i in range(len(cat)):
            cat[i] = adapt_category_format(cat[i]) # Aggiusta maiuscole e minuscole
            if cat[i] not in Leontis_Westhof_basepairs:
                print("THE CATEGORY: " + cat[i] + " IS NOT RECOGNISED!")
                sys.exit()

    if category:
        for category in category.split(","):
            categories[category] = []
    else:
        # Se l'utente non specifica nulla vengono considerati tutti i legai
        categories['basepair'] = Leontis_Westhof_basepairs

    if 'basepair' in categories:
        categories['basepair'] = Leontis_Westhof_basepairs
    else:
        categories['basepair'] = cat # Caso in cui l'utente specifica le categorie

    # Controllo l'esistenza dell'input path
    if len(inputPath) > 0 and not os.path.exists(inputPath):
        print("Attempting to create input path %s" % inputPath)
        os.mkdir(inputPath)

    # Controllo l'esistenza dell'output path
    if len(outputPath) > 0 and not os.path.exists(outputPath):
        print("Attempting to create output path %s" % outputPath)
        os.mkdir(outputPath)

    # Gestisce file di input miltipli
    PDBs = []
    entries = entry_id
    for entry in entries:
        path_split = os.path.split(entry)

        if len(path_split[0]) > 0:
            PDBs.append(path_split)
        else:
            PDBs.append((inputPath,entry))

    timerData = myTimer("start")
    failed_structures = []
    counter = 0

    # Funzioni di FR3D per identificare le basi e i cutoff in base ai legami richiesti
    focused_basepair_cutoffs = focus_basepair_cutoffs(nt_nt_cutoffs,categories['basepair'])
    ideal_hydrogen_bonds = load_ideal_basepair_hydrogen_bonds()

    for path, PDB in PDBs:
        counter += 1

        # Identifica il pbd id
        pdbid = PDB.replace(".cif","").replace(".pdb","").replace(".gz","")

        filename = os.path.join(path,PDB)

        print("Reading file %s, which is number %d out of %d" % (filename, counter, len(PDBs)))
        timerData = myTimer("Reading CIF files",timerData)

        structure, messages = load_structure(filename,pdbid)

        if not structure:
            for message in messages:
                failed_structures.append((pdbid,message))
            continue

        interaction_to_list_of_tuples, category_to_interactions, timerData, pair_to_data = annotate_nt_nt_in_structure(structure,categories,focused_basepair_cutoffs,ideal_hydrogen_bonds,[],timerData)
        timerData = myTimer("Recording interactions",timerData)
        print("  Recording interactions in %s" % outputPath)

        # Genera i file di output
        write_txt_output_file(outputPath,pdbid,interaction_to_list_of_tuples,categories,category_to_interactions, cat, opt, allStructure, allAnnotations, mn)

    myTimer("summary",timerData)

    if len(failed_structures) > 0:
        print("Error messages:")
        for message in failed_structures:
            print("%s %s" % message)
    else:
        print("All files read successfully")

if __name__=="__main__":

    # Argomenti obbligatori
    parser = argparse.ArgumentParser()
    parser.add_argument('input_path', help='input paths of the files containing the 3d structure')
    parser.add_argument('output_FolderPath', help='output path of the folder in which the program will produce the output')
    # Flag per le opzioni
    parser.add_argument('-c', "--category", help='Interaction category or categories for the output separated by comma (cWW,tHS,tSW...)')
    parser.add_argument('-o', "--outputFormat", help="Establish the type of output format (aas,bpseq,tkz,png)")
    parser.add_argument('-mn', "--modelNumber", help="Writes only output in model number specified (mn1,mn2,mn3,mn4,...)")
    parser.add_argument('-p',  action='store_true', help="Download the pdb from the database")
    parser.add_argument('-a',  action='store_true', help="Annotates every bond type in one output file (the format can only be aas!)")
    parser.add_argument('-aa',  action='store_true', help="Generates one output file for each bond type and a file with every bond in it (the output format can only be aas!)")

    problem = False
    args = parser.parse_args()

    output_FolderPath = args.output_FolderPath

    input_Path = args.input_path

    if args.category:
        category = args.category
    else: 
        category = 'basepair'

    if args.modelNumber:
        mn = args.modelNumber.split(",")
    else:
        mn = []

    if args.outputFormat:
        opt = [item.lower() for item in args.outputFormat.split(",")]
    else:
        opt = ["aas"] # Default = aas

    # Controllo se il formato di output è fra i formati riconosciuti
    for outputType in opt:
        if(outputType != "aas" and outputType != "bpseq" and outputType != "tkz" and outputType != "png" and outputType != "tkzb"):
            print ("OUTPUT FORMAT IS NOT VALID: " , outputType)
            sys.exit()

    allStructure = args.a
    allAnnotations = args.aa

    if not(args.p) and not(os.path.exists(input_Path)):
        print ("INPUT PATH NOT EXIST")
        sys.exit()
        
    entry_id = os.fsdecode(input_Path)

    # Avvia RNA3Dto2D
    generate_output_files(entry_id, input_Path, output_FolderPath, category, opt, allStructure, allAnnotations, mn)