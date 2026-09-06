import re

class NMCGenerator:
    def __init__(self):
        self.category_abbr = {
            'Fastener': 'BLT', # Simplification: Bolt
            'Valve': 'VLV',
            'Pipe': 'PIP',
            'Bearing': 'BRG',
            'Gasket': 'GSK',
            'Electrical': 'CBL',
            'Motor': 'MTR',
            'Plate': 'PLT',
            'Flange': 'FLG',
            'Filter': 'FLT',
            'Safety': 'SFT'
        }

    def get_abbreviation(self, category: str) -> str:
        return self.category_abbr.get(category, 'UNK')

    def format_spec_value(self, value_str: str) -> str:
        if not value_str or value_str == 'XXX':
            return 'XXX'
        
        # Clean up common units and spaces (e.g., "50 mm" -> "050")
        import re
        # Just extract digits and format to fixed width if numeric
        nums = re.findall(r'\d+(?:\.\d+)?', value_str)
        if nums:
            val = float(nums[0])
            if val.is_integer():
                return f"{int(val):03d}"
            else:
                return str(val).replace('.', 'P')
        
        # If no digits, just uppercase and strip spaces
        return re.sub(r'[^A-Z0-9]', '', value_str.upper())

    def format_grade(self, value_str: str) -> str:
        if not value_str or value_str == 'XXX':
            return 'XXX'
        return re.sub(r'[^A-Z0-9]', '', value_str.upper())

    def generate_code(self, attributes: dict) -> str:
        if not attributes:
            return "NMC-UNK-XXX-XXX-XXX"
            
        cat = attributes.get('category', 'Unknown')
        abbr = self.get_abbreviation(cat)
        
        parts = ['NMC', abbr]
        
        if cat == 'Fastener':
            grade = self.format_grade(attributes.get('grade', 'XXX'))
            thread = self.format_grade(attributes.get('thread_size', 'XXX'))
            length = self.format_spec_value(attributes.get('length', 'XXX'))
            parts.extend([grade, thread, length])
            
        elif cat == 'Valve':
            mat = self.format_grade(attributes.get('material', 'XXX'))
            size = self.format_spec_value(attributes.get('size', 'XXX'))
            rating = self.format_grade(attributes.get('pressure_rating', 'XXX'))
            parts.extend([mat, size, rating])
            
        elif cat == 'Pipe':
            mat = self.format_grade(attributes.get('material', 'XXX'))
            size = self.format_spec_value(attributes.get('size', 'XXX'))
            sch = self.format_grade(attributes.get('schedule', 'XXX'))
            parts.extend([mat, size, sch])
            
        elif cat == 'Bearing':
            num = self.format_grade(attributes.get('bearing_number', 'XXX'))
            parts.extend(['BRG', num, 'XXX'])
            
        elif cat == 'Motor':
            power = self.format_spec_value(attributes.get('power', 'XXX'))
            speed = self.format_spec_value(attributes.get('speed', 'XXX'))
            parts.extend(['MTR', power, speed])
            
        else:
            mat = self.format_grade(attributes.get('material', 'XXX'))
            type_attr = self.format_grade(attributes.get('material_type', 'XXX'))
            # Get the first specific dimension or feature if available
            spec = 'XXX'
            for k in ['size', 'thickness', 'width', 'weight']:
                if k in attributes:
                    spec = self.format_spec_value(attributes[k])
                    break
            parts.extend([mat, type_attr, spec])
            
        return '-'.join(parts)
