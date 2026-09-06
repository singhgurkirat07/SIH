from sklearn.linear_model import LogisticRegression
import numpy as np

class FeedbackReranker:
    def __init__(self):
        self.model = LogisticRegression()
        self.is_trained = False
        self.feedback_data = []
        self.min_required = 20

    def add_feedback(self, features: dict, prediction: str, decision: str):
        self.feedback_data.append({
            'features': features,
            'prediction': prediction,
            'decision': decision,
            'label': 1 if decision == 'approved' else 0
        })

    def has_enough_data(self, min_samples: int = 20) -> bool:
        return len(self.feedback_data) >= min_samples

    def train(self, feedback_data: list[dict] = None) -> dict:
        data_to_use = feedback_data if feedback_data is not None else self.feedback_data
        
        if len(data_to_use) < self.min_required:
            return {'status': 'error', 'message': 'Insufficient data'}
            
        X = []
        y = []
        for item in data_to_use:
            f = item['features']
            X.append([
                f.get('semantic_similarity', 0.0),
                f.get('attribute_similarity', 0.0),
                f.get('technical_similarity', 0.0),
                f.get('text_similarity', 0.0),
                f.get('category_similarity', 0.0)
            ])
            y.append(item['label'])
            
        try:
            self.model.fit(X, y)
            self.is_trained = True
            accuracy = self.model.score(X, y)
            return {'status': 'success', 'accuracy': accuracy}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def rerank(self, matches: list[dict]) -> list[dict]:
        if not self.is_trained:
            return sorted(matches, key=lambda x: x.get('confidence_score', 0), reverse=True)
            
        X = []
        for match in matches:
            X.append([
                match.get('semantic_similarity', 0.0),
                match.get('attribute_similarity', 0.0),
                match.get('technical_similarity', 0.0),
                match.get('text_similarity', 0.0),
                match.get('category_similarity', 0.0)
            ])
            
        try:
            probs = self.model.predict_proba(X)[:, 1]
            for i, match in enumerate(matches):
                match['reranked_score'] = float(probs[i] * 100)
                
            return sorted(matches, key=lambda x: x.get('reranked_score', x.get('confidence_score', 0)), reverse=True)
        except:
            return matches

    def get_status(self) -> dict:
        return {
            'trained': self.is_trained,
            'feedback_count': len(self.feedback_data),
            'min_required': self.min_required,
            'message': f'Ready.' if self.is_trained else f'Insufficient feedback data for retraining. {max(0, self.min_required - len(self.feedback_data))} more reviews needed.'
        }
