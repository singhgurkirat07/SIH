from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class CandidateBlocker:
    def __init__(self):
        self.blocks = {}
        self.vectorizer = TfidfVectorizer(stop_words='english')

    def build_blocks(self, materials: list[dict]) -> dict:
        self.blocks = {}
        for idx, material in enumerate(materials):
            attrs = material.get('attributes', {})
            cat = attrs.get('category', 'Unknown')
            mat_type = attrs.get('material_type', 'Unknown')
            
            # Composite key for tighter blocking
            block_key = f"{cat}::{mat_type}"
            
            if block_key not in self.blocks:
                self.blocks[block_key] = []
            
            self.blocks[block_key].append({
                'index': idx,
                'material': material
            })
            
        return self.blocks

    def get_candidates(self, material: dict, all_materials: list[dict], top_k: int = 10) -> list:
        if not self.blocks:
            self.build_blocks(all_materials)
            
        attrs = material.get('attributes', {})
        cat = attrs.get('category', 'Unknown')
        mat_type = attrs.get('material_type', 'Unknown')
        block_key = f"{cat}::{mat_type}"
        
        candidates = self.blocks.get(block_key, [])
        if not candidates:
            return []
            
        # Use TF-IDF to find top_k within the category
        desc = material.get('original', '')
        docs = [desc] + [c['material'].get('original', '') for c in candidates]
        
        try:
            tfidf_matrix = self.vectorizer.fit_transform(docs)
            cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
            
            # Sort by similarity
            sim_indices = np.argsort(cosine_sim)[::-1]
            
            ranked_candidates = []
            for i in sim_indices:
                if len(ranked_candidates) >= top_k:
                    break
                candidate_material = candidates[i]['material']
                if candidate_material.get('original') != material.get('original'): # Exclude self if exact match string
                    ranked_candidates.append(candidate_material)
                    
            return ranked_candidates
        except:
            return [c['material'] for c in candidates[:top_k]]

    def generate_all_pairs(self, materials: list[dict], top_k: int = 10) -> list[tuple]:
        self.build_blocks(materials)
        seen = set()
        pairs = []
        
        for material in materials:
            candidates = self.get_candidates(material, materials, top_k)
            for cand in candidates:
                id1 = material.get('id')
                id2 = cand.get('id')
                
                # Make sure we don't compare the same item, and create deterministic tuple
                if id1 and id2 and id1 != id2:
                    pair_key = tuple(sorted([id1, id2]))
                    if pair_key not in seen:
                        seen.add(pair_key)
                        pairs.append((material, cand))
                    
        return pairs
