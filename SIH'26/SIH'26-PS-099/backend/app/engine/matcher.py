import json
from rapidfuzz import fuzz
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class MaterialMatcher:
    def __init__(self):
        self.DEFAULT_WEIGHTS = {
            'semantic_similarity': 0.35,
            'attribute_match': 0.30,
            'technical_similarity': 0.20,
            'text_similarity': 0.10,
            'category_match': 0.05
        }
        self.vectorizer = TfidfVectorizer(stop_words='english')
        
    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        if not text1 or not text2:
            return 0.0
        return fuzz.ratio(text1.lower(), text2.lower()) / 100.0
        
    def calculate_attribute_similarity(self, attrs1: dict, attrs2: dict) -> float:
        if not attrs1 or not attrs2:
            return 0.0
            
        keys_to_compare = set(attrs1.keys()).union(attrs2.keys())
        if not keys_to_compare:
            return 0.0
            
        matches = 0
        total_weight = 0
        
        weights = {
            'thread_size': 2.0,
            'grade': 2.0,
            'material': 2.0,
            'material_type': 1.5,
            'shape': 1.0,
            'category': 1.0
        }
        
        for key in keys_to_compare:
            w = weights.get(key, 1.0)
            total_weight += w
            
            val1 = attrs1.get(key)
            val2 = attrs2.get(key)
            
            if val1 == val2 and val1 is not None:
                matches += w
            elif isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                if abs(val1 - val2) < 1e-5:
                    matches += w
                else:
                    # Partial score for numerical closeness
                    diff = abs(val1 - val2) / max(abs(val1), abs(val2))
                    if diff < 0.1:
                        matches += w * (1 - diff*10)
                        
        return matches / total_weight if total_weight > 0 else 0.0

    def calculate_technical_similarity(self, specs1: list, specs2: list) -> float:
        if not specs1 or not specs2:
            return 0.0
            
        # Simplified technical matching logic
        matches = 0
        comparisons = 0
        
        for s1 in specs1:
            for s2 in specs2:
                if s1.get('context') == s2.get('context') and s1.get('unit') == s2.get('unit'):
                    comparisons += 1
                    v1 = s1.get('value', 0)
                    v2 = s2.get('value', 0)
                    if v1 == v2:
                        matches += 1.0
                    else:
                        diff = abs(v1 - v2) / max(abs(v1), abs(v2)) if max(abs(v1), abs(v2)) > 0 else 1.0
                        if diff < 0.1:
                            matches += (1.0 - diff*10)
                            
        return matches / comparisons if comparisons > 0 else 0.0

    def calculate_semantic_similarity(self, desc1: str, desc2: str) -> float:
        if not desc1 or not desc2:
            return 0.0
        try:
            tfidf_matrix = self.vectorizer.fit_transform([desc1, desc2])
            sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(sim)
        except:
            return 0.0

    def calculate_category_similarity(self, cat1: str, cat2: str) -> float:
        if not cat1 or not cat2:
            return 0.0
        if cat1.lower() == cat2.lower():
            return 1.0
        return 0.0

    def match_materials(self, material_a: dict, material_b: dict, weights: dict = None) -> dict:
        w = weights or self.DEFAULT_WEIGHTS
        
        desc1 = material_a.get('normalized', material_a.get('original', ''))
        desc2 = material_b.get('normalized', material_b.get('original', ''))
        
        attrs1 = material_a.get('attributes', {})
        attrs2 = material_b.get('attributes', {})
        
        cat1 = attrs1.get('category', '')
        cat2 = attrs2.get('category', '')
        
        # Calculate individual similarities
        text_sim = self.calculate_text_similarity(desc1, desc2)
        attr_sim = self.calculate_attribute_similarity(attrs1, attrs2)
        sem_sim = self.calculate_semantic_similarity(desc1, desc2)
        cat_sim = self.calculate_category_similarity(cat1, cat2)
        
        # We don't have specs directly in material dict, assume technical is 1.0 if attrs match well
        tech_sim = attr_sim
        
        confidence = (
            text_sim * w['text_similarity'] +
            attr_sim * w['attribute_match'] +
            tech_sim * w['technical_similarity'] +
            sem_sim * w['semantic_similarity'] +
            cat_sim * w['category_match']
        ) * 100

        # CRITICAL TECHNICAL CHECK
        # If specific key attributes clash (e.g. M16 vs M20, 50mm vs 60mm), cap confidence very low
        critical_keys = ['pressure_class', 'voltage', 'current', 'power', 'material_grade', 'grade', 'temperature_rating', 'capacity', 'thread_size', 'length', 'size', 'diameter', 'bearing_number', 'schedule', 'pressure_rating']
        clashing_attributes = []
        for key in critical_keys:
            if key in attrs1 and key in attrs2:
                if str(attrs1[key]).lower() != str(attrs2[key]).lower():
                    clashing_attributes.append(key)
        
        if clashing_attributes:
            confidence = min(confidence, 55.0) # Force DIFFERENT category

        match_type = self.classify_match_type(confidence)
        
        reasons = []
        if cat_sim == 1.0: reasons.append(f"Same material category: {cat1}")
        if attr_sim > 0.9: reasons.append("Attributes match highly")
        if sem_sim > 0.9: reasons.append(f"Description semantic similarity: {int(sem_sim*100)}%")
        
        differences = []
        if clashing_attributes:
            for key in clashing_attributes:
                differences.append(f"Different {key}: {attrs1.get(key)} vs {attrs2.get(key)}")
        elif confidence < 95:
            differences.append('Names or specific details differ slightly')
        else:
            differences.append('None')
            
        message = ""
        # Check for insufficient information
        # e.g., missing essential attributes (very short strings or no extracted parameters)
        if len(attrs1.keys()) < 2 or len(attrs2.keys()) < 2:
            match_type = 'DIFFERENT'
            confidence = min(confidence, 40.0)
            message = "Insufficient information for reliable matching."
        elif confidence < 60:
            match_type = 'DIFFERENT'
            message = "No sufficiently similar material found."
        elif confidence < 75:
            message = "Manual review required."

        return {
            'match_type': match_type,
            'confidence_score': round(confidence, 2),
            'semantic_similarity': round(sem_sim, 2),
            'attribute_similarity': round(attr_sim, 2),
            'technical_similarity': round(tech_sim, 2),
            'text_similarity': round(text_sim, 2),
            'category_similarity': round(cat_sim, 2),
            'reasons': reasons,
            'differences': differences,
            'message': message,
            'proposed_nmc': None
        }
        
    def classify_match_type(self, confidence: float) -> str:
        if confidence >= 95: return 'IDENTICAL'
        if confidence >= 85: return 'DUPLICATE'
        if confidence >= 75: return 'NEAR_DUPLICATE'
        if confidence >= 60: return 'FUNCTIONALLY_EQUIVALENT'
        return 'DIFFERENT'
