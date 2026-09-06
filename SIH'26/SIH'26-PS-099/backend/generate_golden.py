import csv
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

golden_set = [
    # IDENTICAL
    ("HEX BOLT M16 X 50 MM SS304", "Bolt Hex M16x50 Stainless Steel 304", "CPCL", "BHEL", "IDENTICAL"),
    ("VALVE GATE 2 INCH 150# CS FLANGED", "Gate Valve 2\" Class 150 Carbon Steel Flg", "ONGC", "NTPC", "IDENTICAL"),
    ("PIPE SMLS 4 INCH SCH40 CS", "Seamless Pipe 4\" Schedule 40 Carbon Steel", "BHEL", "CPCL", "IDENTICAL"),
    ("BEARING BALL 6205 ZZ", "Ball Bearing 6205-ZZ", "NTPC", "ONGC", "IDENTICAL"),
    ("MOTOR SQUIRREL CAGE 15KW 415V", "Electric Motor 15KW 415V SCIM", "SAIL", "BHEL", "IDENTICAL"),
    
    # DUPLICATE (Slightly different phrasing but same item)
    ("O-RING VITON 50MM ID X 3MM", "Viton O-Ring ID 50 x 3 mm THK", "CPCL", "ONGC", "DUPLICATE"),
    ("GASKET SPW 4 INCH 150# SS316", "Spiral Wound Gasket 4\" 150# SS316/Graphite", "NTPC", "CPCL", "DUPLICATE"),
    ("CABLE POWER 3C X 2.5 SQMM CU XLPE", "3 Core 2.5 Sq.mm Copper XLPE Cable", "BHEL", "SAIL", "DUPLICATE"),
    ("PUMP CENTRIFUGAL 50M3/HR 30M HEAD", "Centrifugal Water Pump 50 m3/h, 30m HD", "ONGC", "BHEL", "DUPLICATE"),
    ("FLANGE WNRF 6 INCH 300# CS", "Weld Neck Flange RF 6\" 300# Carbon Steel", "CPCL", "NTPC", "DUPLICATE"),

    # NEAR_DUPLICATE (Matches on primary but small missing/diff minor specs)
    ("HEX BOLT M16 X 50 MM SS304", "HEX BOLT M16 X 50 MM SS", "CPCL", "BHEL", "NEAR_DUPLICATE"),
    ("VALVE BALL 1 INCH 800# SS", "Ball Valve 1\" 800# SS316", "ONGC", "NTPC", "NEAR_DUPLICATE"),
    ("PIPE ERW 2 INCH SCH40 CS", "PIPE 2 INCH SCH40 CS", "BHEL", "CPCL", "NEAR_DUPLICATE"),
    ("BEARING ROLLER 22213", "Spherical Roller Bearing 22213 EK", "NTPC", "ONGC", "NEAR_DUPLICATE"),
    ("GASKET TEFLON 2 INCH 150#", "PTFE Gasket 2\" 150# 3mm THK", "SAIL", "BHEL", "NEAR_DUPLICATE"),

    # FUNCTIONALLY_EQUIVALENT (Different materials or slightly different ratings, but can be substituted often)
    ("HEX BOLT M16 X 50 MM MS", "HEX BOLT M16 X 50 MM HT", "CPCL", "BHEL", "FUNCTIONALLY_EQUIVALENT"),
    ("VALVE GATE 2 INCH 150# CS FLANGED", "VALVE GATE 2 INCH 150# SS FLANGED", "ONGC", "NTPC", "FUNCTIONALLY_EQUIVALENT"),
    ("CABLE POWER 3C X 2.5 SQMM CU", "CABLE POWER 3C X 2.5 SQMM AL", "BHEL", "CPCL", "FUNCTIONALLY_EQUIVALENT"),
    ("O-RING NITRILE 50MM ID X 3MM", "O-RING VITON 50MM ID X 3MM", "NTPC", "ONGC", "FUNCTIONALLY_EQUIVALENT"),
    ("GASKET CAF 4 INCH 150#", "GASKET NON-ASBESTOS 4 INCH 150#", "SAIL", "BHEL", "FUNCTIONALLY_EQUIVALENT"),

    # DIFFERENT (Strictly different technical specs)
    ("HEX BOLT M16 X 50 MM SS304", "HEX BOLT M16 X 60 MM SS304", "CPCL", "BHEL", "DIFFERENT"),
    ("HEX BOLT M16 X 50 MM SS304", "HEX BOLT M20 X 50 MM SS304", "CPCL", "ONGC", "DIFFERENT"),
    ("VALVE GATE 2 INCH 150# CS FLANGED", "VALVE GATE 3 INCH 150# CS FLANGED", "ONGC", "NTPC", "DIFFERENT"),
    ("PIPE SMLS 4 INCH SCH40 CS", "PIPE SMLS 4 INCH SCH80 CS", "BHEL", "CPCL", "DIFFERENT"),
    ("BEARING BALL 6205 ZZ", "BEARING BALL 6206 ZZ", "NTPC", "ONGC", "DIFFERENT"),
    ("MOTOR 15KW 415V", "MOTOR 22KW 415V", "SAIL", "BHEL", "DIFFERENT"),
    ("FLANGE WNRF 6 INCH 300# CS", "FLANGE WNRF 6 INCH 150# CS", "CPCL", "NTPC", "DIFFERENT"),
    ("CABLE 3C X 2.5 SQMM CU", "CABLE 4C X 2.5 SQMM CU", "BHEL", "SAIL", "DIFFERENT"),
    ("GASKET SPW 4 INCH 150# SS316", "GASKET SPW 4 INCH 300# SS316", "NTPC", "CPCL", "DIFFERENT"),
    ("O-RING 50MM ID X 3MM", "O-RING 60MM ID X 3MM", "CPCL", "ONGC", "DIFFERENT"),
    
    # 20 more distinct DIFFERENT ones to ensure it rejects things that are totally unrelated
    ("HEX BOLT M16 X 50 MM SS304", "VALVE GATE 2 INCH 150# CS", "CPCL", "BHEL", "DIFFERENT"),
    ("PIPE SMLS 4 INCH", "BEARING BALL 6205", "BHEL", "CPCL", "DIFFERENT"),
    ("MOTOR 15KW", "CABLE 3C X 2.5", "NTPC", "ONGC", "DIFFERENT"),
    ("FLANGE 6 INCH", "O-RING 50MM", "SAIL", "BHEL", "DIFFERENT"),
    ("GASKET 4 INCH", "PUMP CENTRIFUGAL 50M3/HR", "CPCL", "NTPC", "DIFFERENT"),
    
    # Adding 15 more to hit the 50 range requirement
    ("SCREW COUNTERSUNK M8 X 20 SS", "CSK Screw M8 x 20mm Stainless Steel", "ONGC", "CPCL", "IDENTICAL"),
    ("SCREW COUNTERSUNK M8 X 20 SS", "CSK Screw M8 x 20mm SS304", "ONGC", "CPCL", "NEAR_DUPLICATE"),
    ("SCREW COUNTERSUNK M8 X 20 SS", "CSK Screw M8 x 25mm SS", "ONGC", "CPCL", "DIFFERENT"),
    ("WASHER SPRING M16 MS", "Spring Washer for M16 Mild Steel", "NTPC", "BHEL", "IDENTICAL"),
    ("WASHER FLAT M16 MS", "WASHER SPRING M16 MS", "NTPC", "BHEL", "DIFFERENT"),
    ("ELBOW 90 DEG 2 INCH SCH40 CS", "90 Degree Elbow 2\" SCH40 Carbon Steel", "SAIL", "NTPC", "IDENTICAL"),
    ("ELBOW 90 DEG 2 INCH SCH40 CS", "ELBOW 45 DEG 2 INCH SCH40 CS", "SAIL", "NTPC", "DIFFERENT"),
    ("TEE EQUAL 4 INCH SCH80 SS316", "Equal Tee 4\" Sch 80 SS316", "CPCL", "ONGC", "IDENTICAL"),
    ("TEE EQUAL 4 INCH SCH80 SS316", "TEE REDUCING 4 X 3 INCH SCH80 SS316", "CPCL", "ONGC", "DIFFERENT"),
    ("GLOBE VALVE 1 INCH 300# CS", "Valve Globe 1\" 300# Carbon Steel Flg", "BHEL", "SAIL", "IDENTICAL"),
    ("GLOBE VALVE 1 INCH 300# CS", "GATE VALVE 1 INCH 300# CS", "BHEL", "SAIL", "DIFFERENT"),
    ("CHECK VALVE 6 INCH 150# SS304", "Non Return Valve 6\" 150# SS304", "NTPC", "CPCL", "IDENTICAL"),
    ("CHECK VALVE 6 INCH 150# SS304", "CHECK VALVE 6 INCH 300# SS304", "NTPC", "CPCL", "DIFFERENT"),
    ("ANCHOR BOLT M20 X 200 MM HT", "Anchor Bolt M20x200mm High Tensile", "ONGC", "BHEL", "IDENTICAL"),
    ("ANCHOR BOLT M20 X 200 MM HT", "ANCHOR BOLT M20 X 250 MM HT", "ONGC", "BHEL", "DIFFERENT"),
]

golden_csv_path = os.path.join(DATA_DIR, "golden_test_set.csv")
with open(golden_csv_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(["material_a_description", "material_b_description", "material_a_cpse", "material_b_cpse", "expected_label"])
    for row in golden_set:
        writer.writerow(row)

print(f"Generated {len(golden_set)} golden test pairs in {golden_csv_path}")
