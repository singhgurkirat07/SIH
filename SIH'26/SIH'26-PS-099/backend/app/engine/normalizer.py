import re

class MaterialNormalizer:
    def __init__(self):
        self.abbreviations = {
            'MS': 'Mild Steel',
            'GI': 'Galvanized Iron',
            'CS': 'Carbon Steel',
            'CI': 'Cast Iron',
            'HEX': 'Hexagonal',
            'SMLS': 'Seamless',
            'ERW': 'Electric Resistance Welded',
            'HDG': 'Hot Dip Galvanized',
            'FLG': 'Flange',
            'SORF': 'Slip-On Flange',
            'WNRF': 'Weld Neck Flange',
            'SWG': 'Spiral Wound Gasket',
            'RTJ': 'Ring Type Joint',
            'XLPE': 'Cross-Linked Polyethylene',
            'PVC': 'Polyvinyl Chloride',
            'BW': 'Butt Weld',
            'THD': 'Threaded',
            'RF': 'Raised Face',
            'DCP': 'Dry Chemical Powder',
            'TEFC': 'Totally Enclosed Fan Cooled',
            'FRP': 'Fiber Reinforced Plastic',
            'DG': 'Deep Groove',
            'LH': 'Low Hydrogen',
            'ARM': 'Armoured',
            'CON': 'Concentric',
            'GRB': 'Grade B',
            '3PH': '3 Phase',
            '3PHASE': '3 Phase',
            'NB': 'Nominal Bore',
            'DN': 'Nominal Diameter',
            'SCH': 'Schedule',
            'SCH40': 'Schedule 40',
            'CL': 'Class',
            'CLASS': 'Class',
            'PN': 'Pressure Nominal',
            'NLGI': 'National Lubricating Grease Institute',
            'VG': 'Viscosity Grade'
        }
        
        self.categories_map = {
            'Fastener': ['bolt', 'nut', 'screw', 'washer', 'rivet', 'anchor', 'stud', 'u-bolt'],
            'Valve': ['gate valve', 'ball valve', 'butterfly valve', 'check valve', 'globe valve', 'needle valve', 'safety valve', 'relief valve'],
            'Pipe': ['pipe', 'tube', 'conduit'],
            'Pipe Fitting': ['elbow', 'tee', 'reducer', 'coupling', 'expansion joint', 'bend', 'cap', 'plug', 'nipple', 'union'],
            'Bearing': ['bearing', 'bush', 'sleeve'],
            'Gasket': ['gasket', 'seal', 'o-ring', 'packing'],
            'Electrical': ['cable', 'wire', 'connector', 'switch', 'breaker', 'cable gland', 'cable tray'],
            'Instrumentation': ['thermocouple', 'gauge', 'transmitter', 'sensor', 'indicator'],
            'Motor': ['motor', 'pump', 'compressor', 'blower', 'fan'],
            'Plate': ['plate', 'sheet', 'coil', 'strip'],
            'Flange': ['flange'],
            'Filter': ['filter', 'strainer', 'element', 'cartridge'],
            'Safety': ['helmet', 'glove', 'goggle', 'harness', 'mask', 'shoe', 'fire extinguisher', 'cylinder'],
            'Consumable': ['electrode', 'grease', 'oil', 'lubricant']
        }

        self.material_types_map = {
            'Hex Bolt': ['HEX BOLT', 'HEXAGONAL BOLT', 'HEX HEAD BOLT'],
            'Stud Bolt': ['STUD BOLT', 'STUD'],
            'Anchor Bolt': ['ANCHOR BOLT', 'J-BOLT ANCHOR', 'J BOLT'],
            'U-Bolt': ['U BOLT', 'U-BOLT'],
            'Gate Valve': ['GATE VALVE'],
            'Ball Valve': ['BALL VALVE'],
            'Swing Check Valve': ['SWING CHECK VALVE', 'CHECK VALVE SWING TYPE'],
            'Centrifugal Pump': ['CENTRIFUGAL PUMP'],
            'Spiral Wound Gasket': ['SPIRAL WOUND GASKET', 'SWG'],
            'Ball Bearing': ['DEEP GROOVE BALL BEARING', 'BALL BEARING', 'BEARING BALL'],
            'Taper Roller Bearing': ['TAPER ROLLER BEARING'],
            'Slip-On Flange': ['SLIP ON FLANGE', 'SORF'],
            'Weld Neck Flange': ['WELD NECK FLANGE', 'WNRF'],
            '90° Elbow': ['ELBOW 90 DEG', '90 DEG ELBOW'],
            'Equal Tee': ['TEE EQUAL', 'EQUAL TEE'],
            'Concentric Reducer': ['REDUCER CON', 'CONCENTRIC REDUCER'],
            'Welding Electrode': ['WELDING ELECTRODE', 'ELECTRODE WELDING', 'WELDING ROD']
        }

    def expand_abbreviations(self, text: str) -> str:
        # Pre-process common missing spaces (e.g., 50MM -> 50 MM, M16X50 -> M16 X 50)
        # Add space between numbers and MM/INCH
        text = re.sub(r'(\d)(MM|INCH|IN|KG|HP|KW)\b', r'\1 \2', text, flags=re.IGNORECASE)
        # Add spaces around 'X' in dimensions (e.g., M16X50 -> M16 X 50)
        text = re.sub(r'(?<=\d)(X)(?=\d)', r' X ', text, flags=re.IGNORECASE)
        # SS 304 -> SS304 so it gets caught by the next rule, or expand directly
        text = re.sub(r'\bSS\s+(304|316|410)\b', r'SS\1', text, flags=re.IGNORECASE)

        words = text.split()
        expanded = []
        for word in words:
            clean_word = re.sub(r'[^a-zA-Z0-9]', '', word.upper())
            if not clean_word:
                expanded.append(word)
                continue
                
            if clean_word == 'CS' and 'SECTION' in text.upper():
                expanded.append(word)
                continue
            if clean_word == 'SS':
                expanded.append('Stainless Steel')
                continue
                
            if clean_word in self.abbreviations:
                expanded.append(self.abbreviations[clean_word])
            else:
                if re.match(r'^SS(304|316|410L?)$', clean_word):
                    expanded.append(f'Stainless Steel {clean_word[2:]}')
                elif clean_word == 'MM':
                    expanded.append('mm')
                else:
                    expanded.append(word)
        return ' '.join(expanded)

    def extract_attributes(self, raw_description: str) -> dict:
        attrs = {}
        upper_desc = raw_description.upper()

        # 1. Material and Grade Extraction
        ss_match = re.search(r'SS\s?(304|316)|STAINLESS STEEL\s?(304|316)', upper_desc)
        if ss_match:
            attrs['material'] = 'Stainless Steel'
            attrs['grade'] = f"SS{ss_match.group(1) or ss_match.group(2)}"
        elif re.search(r'\bMS\b|MILD STEEL', upper_desc):
            attrs['material'] = 'Mild Steel'
            attrs['grade'] = 'MS'
        elif re.search(r'\bCS\b|CARBON STEEL', upper_desc):
            if 'CROSS SECTION' not in upper_desc:
                attrs['material'] = 'Carbon Steel'
                attrs['grade'] = 'CS'

        # Standard and Grade (e.g., A106 GR B, IS 2062 GR E250)
        std_match1 = re.search(r'(A106)\s*(?:GR\s*B|B|GRB)', upper_desc)
        if std_match1:
            attrs['standard'] = 'ASTM A106'
            attrs['grade'] = 'B'
            
        std_match2 = re.search(r'(IS\s*2062)\s*(?:GR\s*)?(E250)', upper_desc)
        if std_match2:
            attrs['standard'] = 'IS 2062'
            attrs['grade'] = 'E250'
            
        # Nut grade (B7/2H)
        nut_grade = re.search(r'B7\s*(?:/|WITH|C/W)\s*2H', upper_desc)
        if nut_grade:
            attrs['grade'] = 'B7'
            attrs['nut_grade'] = '2H'

        # Electrode classification
        elec = re.search(r'E(6013|7018)', upper_desc)
        if elec:
            attrs['electrode_classification'] = f"E{elec.group(1)}"

        # 2. Size/Dimension Extraction
        # Thread Size & Length
        thread_len = re.search(r'M(\d+)\s*(?:X|-|x)\s*(\d+(?:\.\d+)?)\s*(?:MM)?', upper_desc)
        if thread_len:
            attrs['thread_size'] = f"M{thread_len.group(1)}"
            attrs['length'] = f"{thread_len.group(2)} mm"
        else:
            thread = re.search(r'M(\d+)', upper_desc)
            if thread:
                attrs['thread_size'] = f"M{thread.group(1)}"
                
        # Pipe sizes
        pipe_size = re.search(r'(\d+(?:\.\d+)?)\s*(?:INCH|IN|")|DN\s*(\d+)|(\d+)\s*NB|(\d+(?:\.\d+)?)\s*MM\s*(?:DIA)?', upper_desc)
        if pipe_size:
            val = pipe_size.group(1) or pipe_size.group(2) or pipe_size.group(3) or pipe_size.group(4)
            unit = 'inch' if pipe_size.group(1) else 'mm'
            attrs['size'] = f"{val} {unit}"
            if pipe_size.group(2): attrs['size'] = f"DN{val}"
            if pipe_size.group(3): attrs['size'] = f"{val}NB"

        # Cable
        cable = re.search(r'(\d+(?:\.\d+)?)\s*C(?:ORE)?\s*(?:X|x)\s*(\d+(?:\.\d+)?)\s*(?:SQ\s*MM|MM2|SQMM)', upper_desc)
        if cable:
            attrs['cores'] = cable.group(1)
            attrs['cross_section'] = f"{cable.group(2)} sq mm"

        # Power
        power = re.search(r'(\d+(?:\.\d+)?)\s*(HP|KW)', upper_desc)
        if power:
            attrs['power'] = f"{power.group(1)} {power.group(2)}"

        # Speed
        speed = re.search(r'(\d+)\s*RPM', upper_desc)
        if speed:
            attrs['speed'] = f"{speed.group(1)} RPM"

        # Temperature
        temp = re.search(r'(\d+-\d+)\s*(?:DEG\s*C|C)', upper_desc)
        if temp:
            attrs['temp_range'] = f"{temp.group(1)} °C"

        # Pressure
        pressure = re.search(r'(\d+-\d+)\s*KG/CM2', upper_desc)
        if pressure:
            attrs['pressure_range'] = f"{pressure.group(1)} KG/CM2"

        # Thickness
        thk = re.search(r'(\d+(?:\.\d+)?)\s*(?:MM\s*)?(?:THK|THICK)', upper_desc)
        if thk:
            attrs['thickness'] = f"{thk.group(1)} mm"

        # Rating
        rating = re.search(r'(\d+)#|#(\d+)|(?:CLASS|CL)\s*(\d+)|(\d+)LB|PN(\d+)', upper_desc)
        if rating:
            val = rating.group(1) or rating.group(2) or rating.group(3) or rating.group(4) or rating.group(5)
            prefix = "PN" if rating.group(5) else "CLASS "
            if prefix == "PN":
                attrs['pressure_rating'] = f"PN{val}"
            else:
                attrs['pressure_rating'] = f"{val}#"

        # Schedule
        sch = re.search(r'(?:SCH|SCHEDULE)\s*(\d+[S]?)', upper_desc)
        if sch:
            attrs['schedule'] = f"SCH{sch.group(1)}"

        # Micron
        micron = re.search(r'(\d+)\s*MICRON', upper_desc)
        if micron:
            attrs['filtration_rating'] = f"{micron.group(1)} Micron"

        # Weight
        weight = re.search(r'(\d+(?:\.\d+)?)\s*KG', upper_desc)
        if weight:
            attrs['weight'] = f"{weight.group(1)} KG"

        # Width
        width = re.search(r'(\d+)\s*(?:MM\s*WIDE)', upper_desc)
        if width:
            attrs['width'] = f"{width.group(1)} mm"

        # Bearing number
        bearing = re.search(r'\b(6\d{3}|3\d{4})', upper_desc)
        if bearing:
            attrs['bearing_number'] = bearing.group(1)

        # Gasket ring
        ring = re.search(r'R-?(\d+)', upper_desc)
        if ring and ('RTJ' in upper_desc or 'RING' in upper_desc):
            attrs['ring_number'] = f"R{ring.group(1)}"

        # Electrode size
        elec_size = re.search(r'(\d+(?:\.\d+)?)\s*MM', upper_desc)
        if elec_size and ('ELECTRODE' in upper_desc or elec):
            attrs['electrode_diameter'] = f"{elec_size.group(1)} mm"

        # 3. Material Type Classification
        for m_type, keywords in self.material_types_map.items():
            for kw in keywords:
                if kw in upper_desc:
                    attrs['material_type'] = m_type
                    break
            if 'material_type' in attrs:
                break
                
        # 4. Category Classification
        lower_desc = raw_description.lower()
        if 'material_type' in attrs:
            for cat, keywords in self.categories_map.items():
                if any(kw in attrs['material_type'].lower() for kw in keywords):
                    attrs['category'] = cat
                    break
        if 'category' not in attrs:
            # check description
            for cat, keywords in self.categories_map.items():
                if 'transformer oil' in lower_desc and cat == 'Instrumentation':
                    attrs['category'] = cat
                    break
                if any(re.search(rf'\b{kw}\b', lower_desc) for kw in keywords):
                    # Filter out oil to consumables vs transformer oil
                    if kw == 'oil' and 'transformer' in lower_desc:
                        attrs['category'] = 'Instrumentation'
                    else:
                        attrs['category'] = cat
                    break

        return attrs

    def normalize_description(self, raw_description: str) -> dict:
        normalized = self.expand_abbreviations(raw_description)
        attributes = self.extract_attributes(raw_description)
        
        # Calculate confidence
        # A good extraction would have category + at least 2-3 specifics
        num_attrs = len(attributes)
        confidence = min(0.99, max(0.2, (num_attrs / 5.0) * 0.95))
        
        # Cap confidence if missing basic category
        if 'category' not in attributes:
            confidence = min(confidence, 0.4)
            
        return {
            'original': raw_description,
            'normalized': normalized,
            'attributes': attributes,
            'confidence': round(confidence, 2)
        }
