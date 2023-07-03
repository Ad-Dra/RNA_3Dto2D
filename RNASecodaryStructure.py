import os
from PIL import Image, ImageDraw, ImageFont

class RNASecondaryStructure:
    def __init__(self, sequence, pdbid):
        self.sequence = sequence
        self.pdbid = pdbid
        self.bonds = []

    def add_bond(self, base1_number, base2_number, bond_type, model_number):
        base1_number = int(base1_number)
        base2_number = int(base2_number)

        if base1_number == base2_number:
            # Indici uguali, return 
            return

        if base1_number > base2_number:
            # Scambia base1_number e base2_number (base1 indice sempre minore)
            base1_number, base2_number = base2_number, base1_number

        base_indexes = [int(base[0]) for base in self.sequence]
        if base1_number not in base_indexes or base2_number not in base_indexes:
            
            # Indice fuori dalla sequenza, return
            return

        for bond in self.bonds:
            if bond.base1 == base1_number and bond.base2 == base2_number and bond.bondType == bond_type and abs(bond.model_number) == abs(model_number):
                # Il legame esiste già
                return

        # Tutti i controlli passati, aggiungi il legame
        bond = Bond([base1_number, base2_number], bond_type, abs(model_number))
        self.bonds.append(bond)

    def write_output_file(self, bond_types, model_number, output_formats, outputFolder):
        if 'bpseq' in output_formats:
            self.write_bpseq_txt(bond_types, model_number, outputFolder)
        if "aas" in output_formats:
            self.write_aas_txt(bond_types, model_number, outputFolder)
        if "tkz" in output_formats:
            self.write_tkz_txt(bond_types, model_number, outputFolder)
        if "tkzb" in output_formats:
            self.write_Tkz_with_holes(bond_types, model_number, outputFolder)
        if  "png" in output_formats:
            self.write_arc_diagram_png(bond_types, model_number, outputFolder)

    def generate_bpseq_sequence(self, bondType, model_number):
        bpseq_sequence = []
        for baseNumber, base in self.sequence:

            baseNum1 = baseNumber
            baseLetter = base
            baseNum2 = 0

            for bond in self.bonds:
                if bond.bondType == bondType and int(baseNumber) == bond.base1 and abs(model_number) == abs(bond.model_number):
                    baseNum2 = bond.base2   
                elif bond.bondType == bondType and int(baseNumber) == bond.base2 and abs(model_number) == abs(bond.model_number):
                    baseNum2 = bond.base1

            bpseq_sequence.append(f"{baseNum1} {baseLetter} {baseNum2}")

        return bpseq_sequence
        
    def generate_aas_sequence(self, bond_types, model_number):
        aas_sequence = []
        firstBaseIndex = int(self.sequence[0][0]) - 1
        aas_sequence.append(''.join(pair[1] for pair in self.sequence))
        
        unique_bonds = set()
        sorted_bonds = sorted(self.bonds, key=lambda bond: bond.base1)
        
        for bond in sorted_bonds:
            if bond.bondType in bond_types and abs(model_number) == abs(bond.model_number):
                # Create a tuple representing the bond
                bond_tuple = (bond.base1, bond.base2)
                
                # Check if the bond is already in the set
                if bond_tuple in unique_bonds:
                    continue  # Skip duplicate bond
                
                unique_bonds.add(bond_tuple)  # Add the bond to the set
                aas_sequence.append(f"({bond.base1 - firstBaseIndex},{bond.base2 - firstBaseIndex});")
        
        return aas_sequence

    def write_aas_txt(self, bond_types, model_number, output_folder):

        if not self.any_bonds_found(bond_types, model_number):
            return

        filename = generate_file_name(self.pdbid, model_number, bond_types, "aas", output_folder, "txt")

        aas = self.generate_aas_sequence(bond_types, model_number)

        with open(filename,'w') as f:
            f.write(str(aas[0] + "\n\n"))
            aas.remove(aas[0])
            for line in aas:
                f.write(str(line))

    def write_bpseq_txt(self, bond_type, model_number, output_folder):
        if len(bond_type) > 1 or not self.any_bonds_found(bond_type, model_number): # Bpseq con più di un legame può causare conflitti
            return

        filename = generate_file_name(self.pdbid, model_number, bond_type, "bpseq", output_folder, "txt")
        
        bpseq = self.generate_bpseq_sequence(bond_type[0], model_number)
        if bpseq == None:
            return

        with open(filename,'w') as f:
            for line in bpseq:
                f.write(str(line + "\n"))

    def write_arc_diagram_png(self, bond_types, model_number, output_folder):

        if not self.any_bonds_found(bond_types, model_number):
            return

        n = len(self.sequence)
        start_number = int(self.sequence[0][0])
        connections = []
        filename = generate_file_name(self.pdbid, model_number, bond_types, "arc", output_folder, "png")

        for bond in self.bonds:
            if bond.bondType in bond_types and abs(model_number) == abs(bond.model_number):
                connections.append([int(bond.base1), int(bond.base2)])

        width = 120 + (n - 1) * 60
        height = 120 + (n - 1) * 60 

        # Crea una nuova immagine
        image = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(image)

        y = height // 2
        start_x = 60
        end_x = width - 60

        # Linea orizzontale
        line_color = (0, 0, 0) 
        draw.line([(start_x, y), (end_x, y)], fill=line_color, width=2)

        # Calcola la distanza fra i cerchi
        gap = (end_x - start_x) / (n - 1)

        circle_radius = 10
        circle_color = (0, 0, 0)  # RGB nero
        text_color = (0, 0, 0)  # RGB nero

        # font e dimensioni del testo
        font = ImageFont.truetype("arial.ttf", circle_radius*2)

        for i in range(n):
            center_x = start_x + i * gap
            center = (int(center_x), y)

            # Disegna i cerchi per le basi
            draw.ellipse([(center[0] - circle_radius, center[1] - circle_radius),
                        (center[0] + circle_radius, center[1] + circle_radius)],
                        fill=circle_color)

            # Scrivi i numeri
            number = start_number + i
            text = str(number)
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            text_x = center[0] - text_width // 2
            text_y = center[1] - text_height // 2 + (gap * 2)
            draw.text((text_x, text_y), text, font=font, fill=text_color)

            # Scrivi le lettere
            char = self.sequence[i][1]
            char_bbox = draw.textbbox((0, 0), char, font=font)
            char_width = char_bbox[2] - char_bbox[0]
            char_x = center[0] - char_width // 2
            char_y = center[1] + gap  # 5-pixel spacing
            draw.text((char_x, char_y), char, font=font, fill=text_color)

        # Archi
        arc_color = (0, 0, 0)  # RGB colore blu
        for connection in connections:
            b1, b2 = connection
            
            start_index = b1 - start_number
            end_index = b2 - start_number
            start_x1 = start_x + (start_index * gap)
            end_x = start_x + (end_index * gap)

            # Calcola il centro del semicerchio
            arc_center_x = (start_x1 + end_x) / 2
            arc_center_y = y + circle_radius

            # Calcola il raggio del cerchio
            arc_radius = (end_x - start_x1) / 2

            # Disegna il semicerchio
            start_angle = 180
            end_angle = 0
            draw.arc([(arc_center_x - arc_radius, arc_center_y - arc_radius),
                        (arc_center_x + arc_radius, arc_center_y + arc_radius)],
                        start=start_angle, end=end_angle, fill=arc_color)

        image.save(filename, "PNG")
    
    def write_tkz_txt(self, bond_types, model_number, output_folder):

        if not self.any_bonds_found(bond_types, model_number):
            return

        filename = generate_file_name(self.pdbid, model_number, bond_types, "tkz", output_folder, "txt")

        res = f"\\begin{{tikzpicture}}\n"

        i = 0
        si = self.sequence[0][0]
        li = self.sequence[-1][0]
        for n1,b in self.sequence:
            res += f"\t\\node [draw, fill=black, circle] ({n1}) at ({i}, 0) " + "{}" + ";\n"
            res += f"\t\\node [style=none] ({n1}a) at ({i}, -0.5) {{{b}}};\n"
            res += f"\t\\node [style=none] ({n1}b) at ({i}, -1) {{{n1}}};\n"
            i = i+1

        res += f"\t\draw ({si}.center) to ({li}.center);\n"

        # for n1,b in self.sequence:
        #     for bond in self.bonds:
        #         if bond.bondType in bond_types and n1 == bond.base1 and abs(model_number) == bond.model_number:
        #             res += f"\t\t\draw [bend left=90, looseness=2.00] ({n1}.center) to ({bond.base2}.center);\n"

        for bond in self.bonds:
            print(bond.base1, bond.base2)
            if bond.bondType in bond_types and abs(model_number) == abs(bond.model_number):
                res += f"\t\draw [bend left=90, looseness=2.00] ({bond.base1}.center) to ({bond.base2}.center);\n"

        res += f"\end{{tikzpicture}}"

        with open(filename,'w') as f:
            f.write(res)

    def any_bonds_found(self, bond_types, model_number):
        for bond in self.bonds:
            if abs(bond.model_number) == abs(model_number) and bond.bondType in bond_types:
                return True

    def write_Tkz_with_holes(self, bond_types, model_number, output_folder):
        
        if not self.any_bonds_found(bond_types, model_number):
            return

        res = f"\\begin{{tikzpicture}}\n\t\\node [] (h1) at (0, 0) " + "{}" + ";\n\t\\node [] (h1a) at (0, -0.5) {$\Box$};\n\t\\node [] (h1b) at (0, -1) {$1$};\n"

        filename = generate_file_name(self.pdbid, model_number, bond_types, "tkzB", output_folder, "txt")

        values = []
        for bond in self.bonds:
            if bond.base1 not in values: 
                values.append(bond.base1)
                values.append(bond.base2)
        values.sort()

        i = 1
        h = 0
        for val in values:
            res += f"\t\\node [draw, fill=black, circle] ({val}) at ({i+h}, 0) " + "{}" + ";\n"
            res += f"\t\\node [] (h{h+2}) at ({h+i+1}, 0) "+"{}"+f";\n\t\\node [] (h{h+2}a) at ({h+i+1}, -0.5)"+"{$\Box$};\n\t\\node []"+f"(h{h+2}b) at ({h+i+1}, -1)"+"{$"+f"{h+2}"+"$};\n"
            i = i + 1
            h = h + 1

        res += f"\t\\draw (h1.center) to (h{h+1}.center);\n"

        for bond in self.bonds:
            if bond.bondType in bond_types and abs(model_number) == abs(bond.model_number):
                res += f"\t\draw [bend left=90, looseness=2.00] ({bond.base1}.center) to ({bond.base2}.center);\n"

        res += f"\end{{tikzpicture}}"

        with open(filename,'w') as f:
            f.write(res)

def generate_file_name(pbdID, model_number, bond_types, output_format, output_folder_path, extension):

    filename = ""

    if model_number == -1:
        if len(bond_types) == 1:
            filename = os.path.join(output_folder_path, pbdID + "_" + bond_types[0] + "_" + output_format + "." + extension)
        else:
            filename = os.path.join(output_folder_path, pbdID  + "_" + output_format + "." + extension)
    else:
        if len(bond_types) == 1:
            filename = os.path.join(output_folder_path, pbdID + "_" + bond_types[0] + "_" + output_format + "_" + str(model_number) + "." + extension)
        else:
            filename = os.path.join(output_folder_path, pbdID+ "_" + output_format + "_" + str(model_number) + "." + extension)

    return filename

class Bond:
    def __init__(self, bases, bond_type, model_number):
        self.bases = bases
        self.bond_type = bond_type
        self.model_number = model_number

    @property
    def base1(self):
        return self.bases[0]

    @property
    def base2(self):
        return self.bases[1]
    
    @property
    def bondType(self):
        return self.bond_type
    
    @property
    def model_number(self):
        return self._model_number

    @model_number.setter
    def model_number(self, value):
        self._model_number = value