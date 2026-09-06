class MatchExplainer:
    def generate_explanation(self, material_a: dict, material_b: dict, match_result: dict) -> dict:
        reasons = []
        differences = []
        
        attrs_a = material_a.get('attributes', {})
        attrs_b = material_b.get('attributes', {})
        
        all_keys = set(attrs_a.keys()).union(set(attrs_b.keys()))
        
        for key in all_keys:
            val_a = attrs_a.get(key)
            val_b = attrs_b.get(key)
            
            pretty_key = key.replace('_', ' ').capitalize()
            
            if val_a and val_b:
                if str(val_a).lower() == str(val_b).lower():
                    if key == 'category':
                        reasons.append({'type': 'category_match', 'detail': f'Same material category: {val_a}', 'impact': 'positive'})
                    elif key == 'material_type':
                        reasons.append({'type': 'type_match', 'detail': f'Same material type: {val_a}', 'impact': 'positive'})
                    else:
                        reasons.append({'type': 'attribute_match', 'detail': f'Same {pretty_key.lower()}: {val_a}', 'impact': 'positive'})
                else:
                    if key == 'category':
                        differences.append({'type': 'category_mismatch', 'detail': f'Different categories: {val_a} vs {val_b}', 'impact': 'negative'})
                    else:
                        differences.append({'type': 'attribute_mismatch', 'detail': f'Different {pretty_key.lower()}: {val_a} vs {val_b}', 'impact': 'negative'})
            elif val_a:
                differences.append({'type': 'missing_info', 'detail': f'{pretty_key} not specified in Material B', 'impact': 'neutral'})
            elif val_b:
                differences.append({'type': 'missing_info', 'detail': f'{pretty_key} not specified in Material A', 'impact': 'neutral'})
                
        # Calculate summary and recommendation
        conf = match_result.get('confidence_score', 0)
        
        # Determine Phase 6 specific messages
        if len(attrs_a.keys()) < 2 or len(attrs_b.keys()) < 2:
            summary = "Insufficient information for reliable matching."
            recommendation = "Require more cataloging data before processing."
        elif conf < 60:
            summary = "No sufficiently similar material found."
            recommendation = "No mapping suggested."
        elif conf < 75:
            summary = "Manual review required."
            recommendation = "Review differences manually before assigning a common National Material Code."
        elif conf >= 85:
            summary = f"Materials are functionally equivalent with high confidence ({conf:.0f}%). All critical technical attributes match."
            if differences:
                summary += " Minor differences in naming conventions or missing descriptive fields do not affect functional equivalence."
            recommendation = f"Map both to Common National Material Code: {match_result.get('proposed_nmc', 'NMC-GENERIC-001')}"
        else:
            summary = f"Materials are potentially equivalent with moderate confidence ({conf:.0f}%)."
            recommendation = "Review differences manually before assigning a common National Material Code."
            
        # Determine technical conflicts for Why Not Merge
        matching_attrs = []
        conflicting_attrs = []
        missing_attrs = []
        
        critical_keys = {'pressure_class', 'voltage', 'current', 'power', 'material_grade', 'grade', 'temperature_rating', 'capacity', 'pressure_rating'}
        significant_keys = {'thread_size', 'length', 'size', 'diameter', 'bearing_number', 'schedule', 'dimensions', 'specification', 'standard'}
        
        for key in all_keys:
            val_a = attrs_a.get(key)
            val_b = attrs_b.get(key)
            pretty_key = key.replace('_', ' ').capitalize()
            
            if val_a and val_b:
                if str(val_a).lower() == str(val_b).lower():
                    matching_attrs.append({"name": pretty_key, "value": val_a})
                else:
                    severity = "MINOR"
                    if key in critical_keys:
                        severity = "CRITICAL"
                    elif key in significant_keys:
                        severity = "SIGNIFICANT"
                    conflicting_attrs.append({"name": pretty_key, "value_a": val_a, "value_b": val_b, "severity": severity})
            elif val_a:
                missing_attrs.append({"name": pretty_key})
            elif val_b:
                missing_attrs.append({"name": pretty_key})

        has_critical = any(c["severity"] == "CRITICAL" for c in conflicting_attrs)
        
        why_not_merge = None
        if conflicting_attrs or (conf < 75 and missing_attrs):
            why_not_merge = {
                "matching_attributes": matching_attrs,
                "conflicting_attributes": conflicting_attrs,
                "missing_attributes": missing_attrs,
                "decision": "DO NOT MERGE" if has_critical else "MANUAL REVIEW",
                "reason": "Critical technical specification differs." if has_critical else "Standard equivalence not verified or missing attributes."
            }

        return {
            'reasons': reasons,
            'differences': differences,
            'warnings': [],
            'summary': summary,
            'recommendation': recommendation,
            'why_not_merge': why_not_merge
        }
