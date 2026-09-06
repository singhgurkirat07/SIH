import csv
import os
import random

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

CPSES = ["CPCL", "BHEL", "NTPC", "SAIL", "ONGC"]

# Base patterns for synthesis
# We'll generate combinations of these to reach 300+ materials

# 1. Fasteners (Bolts, Nuts, Washers, Screws)
fastener_bases = [
    {"type": "HEX BOLT", "sizes": ["M12", "M16", "M20", "M24"], "lengths": ["40", "50", "60", "75", "100"], "mats": ["SS304", "SS316", "CS", "MS", "HT"]},
    {"type": "STUD BOLT", "sizes": ["M16", "M20"], "lengths": ["100", "150", "200"], "mats": ["B7", "B8", "B8M", "L7"]},
    {"type": "NUT HEX", "sizes": ["M12", "M16", "M20", "M24"], "lengths": [""], "mats": ["SS304", "SS316", "CS", "2H", "GR8"]},
    {"type": "WASHER FLAT", "sizes": ["M12", "M16", "M20", "M24"], "lengths": [""], "mats": ["SS304", "MS", "SPRING STEEL"]},
]

# 2. Piping & Valves
piping_bases = [
    {"type": "PIPE SMLS", "sizes": ["2 INCH", "4 INCH", "6 INCH", "8 INCH"], "lengths": ["SCH40", "SCH80", "SCH160"], "mats": ["CS", "SS304", "SS316", "ALLOY STEEL"]},
    {"type": "ELBOW 90 DEG", "sizes": ["2 INCH", "4 INCH"], "lengths": ["SCH40", "SCH80"], "mats": ["CS", "SS304"]},
    {"type": "VALVE GATE", "sizes": ["2 INCH", "4 INCH", "6 INCH"], "lengths": ["150#", "300#", "600#"], "mats": ["CS", "SS316", "WCB"]},
    {"type": "VALVE BALL", "sizes": ["1 INCH", "2 INCH"], "lengths": ["150#", "800#"], "mats": ["SS316", "A105"]},
    {"type": "FLANGE WNRF", "sizes": ["2 INCH", "4 INCH", "6 INCH"], "lengths": ["150#", "300#"], "mats": ["CS", "SS304"]},
]

# 3. Electrical & Mechanical
elec_bases = [
    {"type": "CABLE POWER", "sizes": ["3C X 2.5 SQMM", "4C X 4 SQMM", "3.5C X 35 SQMM"], "lengths": [""], "mats": ["CU XLPE", "AL XLPE", "CU PVC"]},
    {"type": "MOTOR SQUIRREL CAGE", "sizes": ["5KW", "15KW", "22KW", "30KW"], "lengths": ["415V", "690V"], "mats": ["IP55", "IP65"]},
    {"type": "BEARING BALL", "sizes": ["6205", "6206", "6305", "6310"], "lengths": ["ZZ", "2RS", "OPEN"], "mats": [""]},
    {"type": "GASKET SPW", "sizes": ["2 INCH", "4 INCH", "6 INCH"], "lengths": ["150#", "300#"], "mats": ["SS316/GRAPHITE", "SS304/PTFE"]},
]

all_bases = fastener_bases + piping_bases + elec_bases

materials = []
id_counter = 1000

# Explicit demo cases requested by user
demo_cases = [
    # Demo 1: Identical meaning, different phrasing (Resolves to same NMC)
    {"cpse": "CPCL", "code": "CP-DEMO-1", "desc": "HEX BOLT M16 X 50 SS304"},
    {"cpse": "BHEL", "code": "BH-DEMO-1", "desc": "HEXAGONAL BOLT M16X50MM STAINLESS STEEL 304"},
    
    # Demo 2: Missing attributes vs full attributes (Near duplicate / Manual review)
    {"cpse": "NTPC", "code": "NT-DEMO-2", "desc": "BEARING 6205"},
    {"cpse": "ONGC", "code": "ON-DEMO-2", "desc": "BEARING BALL 6205 ZZ"},
    
    # Demo 3: Insufficient info
    {"cpse": "SAIL", "code": "SL-DEMO-3", "desc": "BOLT"},
    {"cpse": "CPCL", "code": "CP-DEMO-3", "desc": "VALVE"},
    
    # Demo 4: Spelling variations / typos
    {"cpse": "BHEL", "code": "BH-DEMO-4", "desc": "VAVLE GATE 4\" 150LB CS FLANGED"},
    {"cpse": "SAIL", "code": "SL-DEMO-4", "desc": "GATE VALVE 4 INCH 150# CARBON STEEL FLG"},
    
    # Demo 5: Functional equivalence (Different material grade, same application)
    {"cpse": "ONGC", "code": "ON-DEMO-5", "desc": "GASKET TEFLON 2 INCH 150#"},
    {"cpse": "NTPC", "code": "NT-DEMO-5", "desc": "GASKET PTFE 2\" CLASS 150"},
]

for dc in demo_cases:
    materials.append([dc["cpse"], dc["code"], dc["desc"]])

# Generate synthetic combinations
for base in all_bases:
    for size in base["sizes"]:
        for length in base["lengths"]:
            for mat in base["mats"]:
                
                # Base description
                desc_parts = [base["type"], size, length, mat]
                desc_clean = " ".join([p for p in desc_parts if p]).strip()
                
                # Generate 1-3 variations for different CPSEs
                num_vars = random.randint(1, 3)
                assigned_cpses = random.sample(CPSES, num_vars)
                
                for cpse in assigned_cpses:
                    id_counter += 1
                    code = f"{cpse}-{id_counter}"
                    
                    # Create variations
                    var_type = random.randint(1, 5)
                    mutated_desc = desc_clean
                    
                    if var_type == 1:
                        # Reorder
                        parts = mutated_desc.split()
                        if len(parts) > 2:
                            parts = parts[-2:] + parts[:-2]
                            mutated_desc = " ".join(parts)
                    elif var_type == 2:
                        # Abbreviate
                        mutated_desc = mutated_desc.replace("STAINLESS STEEL", "SS").replace("CARBON STEEL", "CS")
                        mutated_desc = mutated_desc.replace("INCH", '"').replace("MM", "")
                    elif var_type == 3:
                        # Missing attribute
                        parts = mutated_desc.split()
                        if len(parts) > 2:
                            mutated_desc = " ".join(parts[:-1]) # Drop last word
                    elif var_type == 4:
                        # Typo
                        if "VALVE" in mutated_desc: mutated_desc = mutated_desc.replace("VALVE", "VAVLE")
                        if "BOLT" in mutated_desc: mutated_desc = mutated_desc.replace("BOLT", "BLOT")
                    
                    materials.append([cpse, code, mutated_desc])

# Add a few completely random/nonsense to ensure it doesn't match
for i in range(10):
    cpse = random.choice(CPSES)
    id_counter += 1
    materials.append([cpse, f"UNK-{id_counter}", f"SPARE PART KIT FOR MACHINE {id_counter}"])

# Save to CSV
csv_path = os.path.join(DATA_DIR, "sample_materials.csv")
with open(csv_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(["cpse", "material_code", "description"])
    for row in materials:
        writer.writerow(row)

print(f"Generated {len(materials)} synthetic material records for Demo Dataset at {csv_path}")
