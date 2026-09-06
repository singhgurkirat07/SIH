from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, desc
import json
import csv
import io
import os
from datetime import datetime
from typing import Optional, List, Dict, Any

from .database import engine, get_db, Base
from . import models
from .engine.normalizer import MaterialNormalizer
from .engine.matcher import MaterialMatcher
from .engine.blocker import CandidateBlocker
from .engine.nmc_generator import NMCGenerator
from .engine.explainer import MatchExplainer
from .engine.reranker import FeedbackReranker

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="National Unified Material Master - API",
    version="1.0.0",
    description="AI-Driven Standardization and Harmonization of Material Codes Across CPSEs | SIH 2026 PS-26099"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Singletons
normalizer = MaterialNormalizer()
matcher = MaterialMatcher()
blocker = CandidateBlocker()
nmc_gen = NMCGenerator()
explainer = MatchExplainer()
reranker = FeedbackReranker()

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def log_audit(db: Session, action: str, entity_type: str, entity_id: int = None,
              details: dict = None, user: str = "system", material_ids: str = None):
    log = models.AuditLog(
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=json.dumps(details) if details else None,
        user=user,
        material_ids=material_ids,
        timestamp=datetime.utcnow()
    )
    db.add(log)


def material_to_dict(m, db: Session = None):
    """Convert a Material ORM object to a dict suitable for engine functions."""
    d = {}
    for c in m.__table__.columns:
        val = getattr(m, c.name)
        if isinstance(val, datetime):
            val = val.isoformat()
        d[c.name] = val

    if db:
        attrs = db.query(models.NormalizedAttribute).filter_by(material_id=m.id).all()
        d['attributes'] = {a.attribute_name: a.attribute_value for a in attrs}
    elif hasattr(m, 'attributes') and m.attributes:
        d['attributes'] = {a.attribute_name: a.attribute_value for a in m.attributes}
    else:
        d['attributes'] = {}

    # The engine functions expect 'original' key for description matching
    d['original'] = d.get('description', '')
    return d


# ─── Health ───────────────────────────────────────────────────────────────────

@app.get("/api/health", tags=["Health"])
def health_check():
    return {"status": "ok", "version": "1.0.0", "timestamp": datetime.utcnow().isoformat(),
            "project": "National Unified Material Master", "problem_statement": "SIH 2026 PS-26099"}


# ─── Materials ────────────────────────────────────────────────────────────────

@app.post("/api/materials/upload", tags=["Materials"])
def upload_materials(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    content = file.file.read().decode('utf-8-sig')
    csv_reader = csv.DictReader(io.StringIO(content))

    # Basic check for required columns in header
    required_cols = {'cpse', 'material_code', 'description'}
    if not required_cols.issubset(set(csv_reader.fieldnames or [])):
        missing = required_cols - set(csv_reader.fieldnames or [])
        return {"status": "error", "message": f"Missing required columns in CSV header: {', '.join(missing)}", "added": 0, "skipped": 0, "errors": []}

    count_added = 0
    count_skipped = 0
    errors = []

    for idx, row in enumerate(csv_reader):
        try:
            cpse = (row.get('cpse') or '').strip()
            material_code = (row.get('material_code') or '').strip()
            description = (row.get('description') or '').strip()

            if not cpse or not material_code or not description:
                errors.append({"row": idx + 2, "error": "Missing required field (cpse, material_code, or description)"})
                count_skipped += 1
                continue

            existing = db.query(models.Material).filter_by(cpse=cpse, material_code=material_code).first()
            if existing:
                errors.append({"row": idx + 2, "error": f"Duplicate material code: {material_code} for CPSE: {cpse}"})
                count_skipped += 1
                continue

            norm_result = normalizer.normalize_description(description)
            attrs = norm_result.get('attributes', {})

            material = models.Material(
                cpse=cpse,
                material_code=material_code,
                description=description,
                original_description=description,
                normalized_description=norm_result.get('normalized'),
                category=attrs.get('category') or (row.get('category') or '').strip() or None,
                material_type=attrs.get('material_type') or (row.get('material_type') or '').strip() or None,
                unit=(row.get('unit') or '').strip() or None,
                specification=(row.get('specification') or '').strip() or None,
                extracted_attributes=json.dumps(attrs) if attrs else None,
                manufacturer=(row.get('manufacturer') or '').strip() or None,
                historical_quantity=float(row.get('historical_quantity') or 0),
                historical_cost=float(row.get('historical_cost') or 0),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(material)
            db.flush()

            for k, v in attrs.items():
                attr = models.NormalizedAttribute(
                    material_id=material.id,
                    attribute_name=k,
                    attribute_value=str(v),
                    confidence=norm_result.get('confidence', 0.5)
                )
                db.add(attr)

            count_added += 1
        except Exception as e:
            errors.append({"row": idx + 2, "error": f"Malformed record: {str(e)}"})
            count_skipped += 1

    if count_added > 0:
        log_audit(db, "materials_uploaded", "material", details={"count": count_added})
        db.commit()

    db.commit()
    return {
        "message": f"Upload complete. {count_added} materials added, {count_skipped} skipped.",
        "total_records": count_added + count_skipped,
        "successful_records": count_added,
        "failed_records": count_skipped,
        "errors": errors if errors else None
    }


@app.get("/api/materials/sample-csv", tags=["Materials"])
def get_sample_csv():
    file_path = os.path.join(DATA_DIR, "sample_materials.csv")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Sample CSV not found")
    return FileResponse(file_path, media_type="text/csv", filename="sample_materials.csv")


@app.get("/api/materials", tags=["Materials"])
def list_materials(
    skip: int = 0, limit: int = 100,
    cpse: Optional[str] = None, category: Optional[str] = None,
    search: Optional[str] = None, db: Session = Depends(get_db)
):
    q = db.query(models.Material)
    if cpse:
        q = q.filter(models.Material.cpse == cpse)
    if category:
        q = q.filter(models.Material.category == category)
    if search:
        q = q.filter(or_(
            models.Material.description.ilike(f"%{search}%"),
            models.Material.material_code.ilike(f"%{search}%"),
            models.Material.normalized_description.ilike(f"%{search}%")
        ))

    total = q.count()
    items = q.order_by(models.Material.id).offset(skip).limit(limit).all()

    result = []
    for item in items:
        d = material_to_dict(item)
        # Also fetch NMC code if mapped
        nmc_map = db.query(models.NMCMapping).filter_by(material_id=item.id).first()
        if nmc_map:
            nmc = db.query(models.CommonNationalCode).filter_by(id=nmc_map.nmc_id).first()
            d['nmc_code'] = nmc.nmc_code if nmc else None
        else:
            d['nmc_code'] = None
        result.append(d)

    return {"total": total, "items": result}


@app.get("/api/materials/{id}", tags=["Materials"])
def get_material(id: int, db: Session = Depends(get_db)):
    material = db.query(models.Material).filter(models.Material.id == id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")

    d = material_to_dict(material, db)

    # Matches involving this material
    matches = db.query(models.MatchResult).filter(
        or_(models.MatchResult.material_a_id == id, models.MatchResult.material_b_id == id)
    ).all()
    match_list = []
    for m in matches:
        md = {c.name: getattr(m, c.name) for c in m.__table__.columns}
        for k, v in md.items():
            if isinstance(v, datetime):
                md[k] = v.isoformat()
        # Add the other material's info
        other_id = m.material_b_id if m.material_a_id == id else m.material_a_id
        other = db.query(models.Material).filter_by(id=other_id).first()
        if other:
            md['other_material'] = {
                'id': other.id, 'cpse': other.cpse,
                'material_code': other.material_code, 'description': other.description
            }
        match_list.append(md)
    d['matches'] = match_list

    # NMC Mappings
    mappings = db.query(models.NMCMapping).filter_by(material_id=id).all()
    nmc_list = []
    for mp in mappings:
        nmc = db.query(models.CommonNationalCode).filter_by(id=mp.nmc_id).first()
        nmc_info = {
            'nmc_code': nmc.nmc_code if nmc else None,
            'category': nmc.category if nmc else None,
            'status': mp.status
        }
        # Get all materials mapped to this NMC
        if nmc:
            all_maps = db.query(models.NMCMapping).filter_by(nmc_id=nmc.id).all()
            siblings = []
            for am in all_maps:
                sib_mat = db.query(models.Material).filter_by(id=am.material_id).first()
                if sib_mat:
                    siblings.append({
                        'id': sib_mat.id, 'cpse': sib_mat.cpse,
                        'material_code': sib_mat.material_code, 'description': sib_mat.description
                    })
            nmc_info['mapped_materials'] = siblings
        nmc_list.append(nmc_info)
    d['nmc_mappings'] = nmc_list

    # Audit logs
    logs = db.query(models.AuditLog).filter(
        or_(
            models.AuditLog.entity_id == id,
            models.AuditLog.material_ids.like(f"%{id}%")
        )
    ).order_by(desc(models.AuditLog.timestamp)).limit(20).all()
    d['audit_logs'] = []
    for l in logs:
        ld = {c.name: getattr(l, c.name) for c in l.__table__.columns}
        if isinstance(ld.get('timestamp'), datetime):
            ld['timestamp'] = ld['timestamp'].isoformat()
        d['audit_logs'].append(ld)

    return d


# ─── Matching ─────────────────────────────────────────────────────────────────

@app.post("/api/match", tags=["Matching"])
def run_matching(db: Session = Depends(get_db)):
    materials = db.query(models.Material).all()
    if not materials:
        raise HTTPException(status_code=400, detail="No materials in database. Upload materials first.")

    # Normalize any materials that don't have normalized attributes yet
    for m in materials:
        if not m.normalized_description:
            norm = normalizer.normalize_description(m.description)
            m.normalized_description = norm.get('normalized')
            m.updated_at = datetime.utcnow()

            # Store attributes
            existing_attrs = db.query(models.NormalizedAttribute).filter_by(material_id=m.id).count()
            if existing_attrs == 0:
                for k, v in norm.get('attributes', {}).items():
                    db.add(models.NormalizedAttribute(
                        material_id=m.id, attribute_name=k,
                        attribute_value=str(v), confidence=norm.get('confidence', 0.5)
                    ))
    db.flush()

    # Build material dicts for engine
    mat_dicts = []
    for m in materials:
        d = material_to_dict(m, db)
        mat_dicts.append(d)

    # Build candidate blocks and generate pairs
    blocker_instance = CandidateBlocker()
    pairs_to_evaluate = blocker_instance.generate_all_pairs(mat_dicts, top_k=10)

    matches_found = 0
    total_pairs = 0

    for m1, m2 in pairs_to_evaluate:
        # Skip same CPSE same material code (self)
        if m1['cpse'] == m2['cpse'] and m1['material_code'] == m2['material_code']:
            continue

        # Skip if match already exists
        id_a, id_b = min(m1['id'], m2['id']), max(m1['id'], m2['id'])
        existing = db.query(models.MatchResult).filter_by(
            material_a_id=id_a, material_b_id=id_b
        ).first()
        if existing:
            continue

        total_pairs += 1

        # Run matching
        match_res = matcher.match_materials(m1, m2)
        confidence = match_res.get('confidence_score', 0)

        if confidence < 30:
            continue  # Too low to even record

        # Generate NMC code
        attrs_for_nmc = m1.get('attributes', {}).copy()
        proposed_nmc = nmc_gen.generate_code(attrs_for_nmc)
        match_res['proposed_nmc'] = proposed_nmc

        # Generate explanation
        expl = explainer.generate_explanation(m1, m2, match_res)

        # Store match result
        mr = models.MatchResult(
            material_a_id=id_a,
            material_b_id=id_b,
            match_type=match_res.get('match_type', 'DIFFERENT'),
            confidence_score=confidence,
            semantic_similarity=match_res.get('semantic_similarity', 0.0),
            attribute_similarity=match_res.get('attribute_similarity', 0.0),
            technical_similarity=match_res.get('technical_similarity', 0.0),
            text_similarity=match_res.get('text_similarity', 0.0),
            category_similarity=match_res.get('category_similarity', 0.0),
            explanation=json.dumps(expl),
            status='pending',
            common_national_code=proposed_nmc,
            created_at=datetime.utcnow()
        )
        db.add(mr)
        db.flush()

        # Create NMC registry entry and mappings for good matches
        if confidence >= 60 and match_res.get('match_type') != 'DIFFERENT':
            nmc_record = db.query(models.CommonNationalCode).filter_by(nmc_code=proposed_nmc).first()
            if not nmc_record:
                cat = m1.get('attributes', {}).get('category', 'Unknown')
                nmc_record = models.CommonNationalCode(
                    nmc_code=proposed_nmc,
                    category=cat,
                    description=m1.get('description', ''),
                    normalized_attributes=json.dumps(attrs_for_nmc),
                    created_at=datetime.utcnow()
                )
                db.add(nmc_record)
                db.flush()

            for mid in [id_a, id_b]:
                mat = db.query(models.Material).filter_by(id=mid).first()
                if not db.query(models.NMCMapping).filter_by(material_id=mid, nmc_id=nmc_record.id).first():
                    db.add(models.NMCMapping(
                        nmc_id=nmc_record.id,
                        material_id=mid,
                        cpse=mat.cpse if mat else '',
                        original_code=mat.material_code if mat else '',
                        status='proposed',
                        created_at=datetime.utcnow()
                    ))

        log_audit(db, "match_created", "match", entity_id=mr.id,
                 details={"type": mr.match_type, "confidence": confidence},
                 material_ids=f"{id_a},{id_b}")
        matches_found += 1
    db.commit()

    return {
        "status": "success",
        "matches_found": matches_found,
        "total_pairs_evaluated": total_pairs,
        "message": f"Matching pipeline complete. {matches_found} matches found from {total_pairs} candidate pairs."
    }


@app.get("/api/matches", tags=["Matching"])
def list_matches(
    skip: int = 0, limit: int = 100,
    status: Optional[str] = None, match_type: Optional[str] = None,
    min_confidence: Optional[float] = None, db: Session = Depends(get_db)
):
    q = db.query(models.MatchResult)
    if status:
        q = q.filter(models.MatchResult.status == status)
    if match_type:
        q = q.filter(models.MatchResult.match_type == match_type)
    if min_confidence is not None:
        q = q.filter(models.MatchResult.confidence_score >= min_confidence)

    total = q.count()
    matches = q.order_by(desc(models.MatchResult.confidence_score)).offset(skip).limit(limit).all()

    result = []
    for m in matches:
        d = {c.name: getattr(m, c.name) for c in m.__table__.columns}
        for k, v in d.items():
            if isinstance(v, datetime):
                d[k] = v.isoformat()

        # Include material info
        ma = db.query(models.Material).filter_by(id=m.material_a_id).first()
        mb = db.query(models.Material).filter_by(id=m.material_b_id).first()
        d['material_a'] = {
            'id': ma.id, 'cpse': ma.cpse, 'material_code': ma.material_code,
            'description': ma.description, 'category': ma.category
        } if ma else None
        d['material_b'] = {
            'id': mb.id, 'cpse': mb.cpse, 'material_code': mb.material_code,
            'description': mb.description, 'category': mb.category
        } if mb else None

        result.append(d)
    return {"total": total, "items": result}


@app.get("/api/matches/{id}", tags=["Matching"])
def get_match(id: int, db: Session = Depends(get_db)):
    match = db.query(models.MatchResult).filter(models.MatchResult.id == id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    d = {c.name: getattr(match, c.name) for c in match.__table__.columns}
    for k, v in d.items():
        if isinstance(v, datetime):
            d[k] = v.isoformat()

    ma = db.query(models.Material).filter_by(id=match.material_a_id).first()
    mb = db.query(models.Material).filter_by(id=match.material_b_id).first()
    d['material_a'] = material_to_dict(ma, db) if ma else None
    d['material_b'] = material_to_dict(mb, db) if mb else None

    return d


@app.post("/api/matches/{id}/approve", tags=["Matching"])
def approve_match(id: int, payload: dict = None, db: Session = Depends(get_db)):
    payload = payload or {}
    match = db.query(models.MatchResult).filter(models.MatchResult.id == id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    old_status = match.status
    match.status = 'approved'
    match.reviewed_by = payload.get('reviewer', 'reviewer')
    match.reviewed_at = datetime.utcnow()

    # Store reviewer feedback for reranker
    fb = models.ReviewerFeedback(
        match_id=id,
        decision='approved',
        semantic_similarity=match.semantic_similarity,
        attribute_similarity=match.attribute_similarity,
        technical_similarity=match.technical_similarity,
        text_similarity=match.text_similarity,
        category_similarity=match.category_similarity,
        predicted_match_type=match.match_type,
        created_at=datetime.utcnow()
    )
    db.add(fb)

    log_audit(db, "match_approved", "match", entity_id=id,
             details={"old_status": old_status, "reason": payload.get('reason', ''),
                       "confidence": match.confidence_score, "match_type": match.match_type},
             user=match.reviewed_by,
             material_ids=f"{match.material_a_id},{match.material_b_id}")

    # Update NMC mappings to approved
    if match.common_national_code:
        nmc = db.query(models.CommonNationalCode).filter_by(nmc_code=match.common_national_code).first()
        if nmc:
            mappings = db.query(models.NMCMapping).filter_by(nmc_id=nmc.id).filter(
                models.NMCMapping.material_id.in_([match.material_a_id, match.material_b_id])
            ).all()
            for mapping in mappings:
                mapping.status = 'approved'
                mapping.updated_at = datetime.utcnow()

    # Feed to reranker
    reranker.add_feedback(
        features={
            'semantic_similarity': match.semantic_similarity,
            'attribute_similarity': match.attribute_similarity,
            'technical_similarity': match.technical_similarity,
            'text_similarity': match.text_similarity,
            'category_similarity': match.category_similarity
        },
        prediction=match.match_type,
        decision='approved'
    )

    db.commit()
    return {"status": "success", "id": id, "new_status": "approved"}


@app.post("/api/matches/{id}/reject", tags=["Matching"])
def reject_match(id: int, payload: dict = None, db: Session = Depends(get_db)):
    payload = payload or {}
    match = db.query(models.MatchResult).filter(models.MatchResult.id == id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    old_status = match.status
    match.status = 'rejected'
    match.reviewed_by = payload.get('reviewer', 'reviewer')
    match.reviewed_at = datetime.utcnow()

    fb = models.ReviewerFeedback(
        match_id=id,
        decision='rejected',
        semantic_similarity=match.semantic_similarity,
        attribute_similarity=match.attribute_similarity,
        technical_similarity=match.technical_similarity,
        text_similarity=match.text_similarity,
        category_similarity=match.category_similarity,
        predicted_match_type=match.match_type,
        created_at=datetime.utcnow()
    )
    db.add(fb)

    log_audit(db, "match_rejected", "match", entity_id=id,
             details={"old_status": old_status, "reason": payload.get('reason', ''),
                       "confidence": match.confidence_score, "match_type": match.match_type},
             user=match.reviewed_by,
             material_ids=f"{match.material_a_id},{match.material_b_id}")

    # Prevent automatic mapping / Update to rejected
    if match.common_national_code:
        nmc = db.query(models.CommonNationalCode).filter_by(nmc_code=match.common_national_code).first()
        if nmc:
            mappings = db.query(models.NMCMapping).filter_by(nmc_id=nmc.id).filter(
                models.NMCMapping.material_id.in_([match.material_a_id, match.material_b_id])
            ).all()
            for mapping in mappings:
                mapping.status = 'rejected'
                mapping.updated_at = datetime.utcnow()

    reranker.add_feedback(
        features={
            'semantic_similarity': match.semantic_similarity,
            'attribute_similarity': match.attribute_similarity,
            'technical_similarity': match.technical_similarity,
            'text_similarity': match.text_similarity,
            'category_similarity': match.category_similarity
        },
        prediction=match.match_type,
        decision='rejected'
    )

    db.commit()
    return {"status": "success", "id": id, "new_status": "rejected"}


# ─── Dashboard ────────────────────────────────────────────────────────────────

@app.get("/api/dashboard", tags=["Dashboard"])
def get_dashboard(db: Session = Depends(get_db)):
    total_materials = db.query(models.Material).count()

    dup_types = ['IDENTICAL', 'DUPLICATE', 'NEAR_DUPLICATE']
    duplicates_detected = db.query(models.MatchResult).filter(
        models.MatchResult.match_type.in_(dup_types)).count()
    potential_equivalences = db.query(models.MatchResult).filter(
        models.MatchResult.match_type == 'FUNCTIONALLY_EQUIVALENT').count()
    high_conf = db.query(models.MatchResult).filter(
        models.MatchResult.confidence_score >= 90).count()

    pending = db.query(models.MatchResult).filter_by(status='pending').count()
    approved = db.query(models.MatchResult).filter_by(status='approved').count()
    rejected = db.query(models.MatchResult).filter_by(status='rejected').count()

    total_nmc = db.query(models.CommonNationalCode).count()
    avg_conf = db.query(func.avg(models.MatchResult.confidence_score)).scalar() or 0.0

    # Savings estimation from historical costs of duplicate materials
    dup_matches = db.query(models.MatchResult).filter(
        models.MatchResult.match_type.in_(dup_types)).all()
    dup_mat_ids = set()
    for m in dup_matches:
        dup_mat_ids.add(m.material_a_id)
        dup_mat_ids.add(m.material_b_id)

    total_hist_cost = 0
    if dup_mat_ids:
        cost_res = db.query(func.sum(models.Material.historical_cost)).filter(
            models.Material.id.in_(list(dup_mat_ids))).scalar()
        total_hist_cost = cost_res or 0
    est_savings = total_hist_cost * 0.20

    # CPSE counts
    cpse_rows = db.query(models.Material.cpse, func.count(models.Material.id)).group_by(
        models.Material.cpse).all()
    cpse_counts = {r[0]: r[1] for r in cpse_rows if r[0]}

    # Category counts
    cat_rows = db.query(models.Material.category, func.count(models.Material.id)).group_by(
        models.Material.category).all()
    category_counts = {(r[0] or 'Uncategorized'): r[1] for r in cat_rows}

    # Match type distribution
    type_rows = db.query(models.MatchResult.match_type, func.count(models.MatchResult.id)).group_by(
        models.MatchResult.match_type).all()
    match_type_distribution = {r[0]: r[1] for r in type_rows if r[0]}

    med_conf = db.query(models.MatchResult).filter(
        models.MatchResult.confidence_score >= 75,
        models.MatchResult.confidence_score < 90).count()
    low_conf = db.query(models.MatchResult).filter(
        models.MatchResult.confidence_score < 75).count()

    # Recent activity
    logs = db.query(models.AuditLog).order_by(desc(models.AuditLog.timestamp)).limit(10).all()
    recent_activity = []
    for l in logs:
        ld = {c.name: getattr(l, c.name) for c in l.__table__.columns}
        if isinstance(ld.get('timestamp'), datetime):
            ld['timestamp'] = ld['timestamp'].isoformat()
        recent_activity.append(ld)

    # Fetch evaluation metrics
    eval_metrics = get_evaluation_metrics(db)

    return {
        'total_materials': total_materials,
        'duplicates_detected': duplicates_detected,
        'potential_equivalences': potential_equivalences,
        'high_confidence_matches': high_conf,
        'pending_reviews': pending,
        'approved_matches': approved,
        'rejected_matches': rejected,
        'estimated_savings': est_savings,
        'total_nmc_generated': total_nmc,
        'average_confidence': round(float(avg_conf), 1),
        'cpse_distribution': cpse_counts,
        'category_distribution': category_counts,
        'match_type_distribution': match_type_distribution,
        'confidence_distribution': {'high': high_conf, 'medium': med_conf, 'low': low_conf},
        'recent_activity': recent_activity,
        'evaluation_metrics': eval_metrics
    }


# ─── NMC Registry ────────────────────────────────────────────────────────────

@app.get("/api/analytics/savings-trend", tags=["Dashboard"])
def get_savings_trend(db: Session = Depends(get_db)):
    dup_types = ['IDENTICAL', 'DUPLICATE', 'NEAR_DUPLICATE']
    dup_matches = db.query(models.MatchResult).filter(
        models.MatchResult.match_type.in_(dup_types)).all()
    
    from collections import defaultdict
    import calendar
    trend_dict = defaultdict(float)
    
    for m in dup_matches:
        if m.created_at:
            month_abbr = calendar.month_abbr[m.created_at.month]
            mat = db.query(models.Material).filter_by(id=m.material_a_id).first()
            if mat and mat.historical_cost:
                trend_dict[month_abbr] += (mat.historical_cost * 0.20)
                
    if len(trend_dict) < 2:
        return []
        
    result = []
    for month in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']:
        if month in trend_dict:
            result.append({"name": month, "value": round(trend_dict[month], 2)})
            
    return result


@app.get("/api/nmc", tags=["NMC Registry"])
def list_nmc(db: Session = Depends(get_db)):
    codes = db.query(models.CommonNationalCode).all()
    result = []
    for c in codes:
        d = {col.name: getattr(c, col.name) for col in c.__table__.columns}
        if isinstance(d.get('created_at'), datetime):
            d['created_at'] = d['created_at'].isoformat()

        maps = db.query(models.NMCMapping).filter_by(nmc_id=c.id).all()
        mappings = []
        for mp in maps:
            mat = db.query(models.Material).filter_by(id=mp.material_id).first()
            mappings.append({
                'id': mp.id, 'cpse': mp.cpse, 'original_code': mp.original_code,
                'status': mp.status, 'material_id': mp.material_id,
                'description': mat.description if mat else ''
            })
        d['mappings'] = mappings
        d['mapping_count'] = len(mappings)
        result.append(d)
    return {"items": result}


@app.get("/api/nmc/{id}", tags=["NMC Registry"])
def get_nmc(id: int, db: Session = Depends(get_db)):
    c = db.query(models.CommonNationalCode).filter_by(id=id).first()
    if not c:
        raise HTTPException(status_code=404, detail="NMC not found")

    d = {col.name: getattr(c, col.name) for col in c.__table__.columns}
    if isinstance(d.get('created_at'), datetime):
        d['created_at'] = d['created_at'].isoformat()

    maps = db.query(models.NMCMapping).filter_by(nmc_id=id).all()
    materials = []
    for mp in maps:
        mat = db.query(models.Material).filter_by(id=mp.material_id).first()
        if mat:
            materials.append(material_to_dict(mat, db))
    d['materials'] = materials
    return d


# ─── Audit Trail ──────────────────────────────────────────────────────────────

@app.get("/api/audit", tags=["Audit Trail"])
def list_audit_logs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    total = db.query(models.AuditLog).count()
    logs = db.query(models.AuditLog).order_by(desc(models.AuditLog.timestamp)).offset(skip).limit(limit).all()
    result = []
    for l in logs:
        d = {c.name: getattr(l, c.name) for c in l.__table__.columns}
        if isinstance(d.get('timestamp'), datetime):
            d['timestamp'] = d['timestamp'].isoformat()
        result.append(d)
    return {"total": total, "items": result}


# ─── Search ───────────────────────────────────────────────────────────────────

@app.get("/api/search", tags=["Search"])
def global_search(q: str = "", db: Session = Depends(get_db)):
    if not q or len(q) < 2:
        return {"items": []}

    mats = db.query(models.Material).filter(or_(
        models.Material.material_code.ilike(f"%{q}%"),
        models.Material.description.ilike(f"%{q}%"),
        models.Material.normalized_description.ilike(f"%{q}%"),
        models.Material.cpse.ilike(f"%{q}%"),
        models.Material.category.ilike(f"%{q}%")
    )).limit(50).all()

    result = []
    for m in mats:
        d = material_to_dict(m, db)
        # NMC
        nmc_map = db.query(models.NMCMapping).filter_by(material_id=m.id).first()
        if nmc_map:
            nmc = db.query(models.CommonNationalCode).filter_by(id=nmc_map.nmc_id).first()
            d['nmc_code'] = nmc.nmc_code if nmc else None
        else:
            d['nmc_code'] = None
        # Match count
        match_count = db.query(models.MatchResult).filter(or_(
            models.MatchResult.material_a_id == m.id,
            models.MatchResult.material_b_id == m.id
        )).count()
        d['match_count'] = match_count
        result.append(d)

    return {"items": result}


# ─── Export ───────────────────────────────────────────────────────────────────

@app.get("/api/export", tags=["Export"])
def export_data(db: Session = Depends(get_db)):
    mats = db.query(models.Material).all()
    result = []
    for m in mats:
        d = material_to_dict(m, db)
        nmc_map = db.query(models.NMCMapping).filter_by(material_id=m.id).first()
        if nmc_map:
            nmc = db.query(models.CommonNationalCode).filter_by(id=nmc_map.nmc_id).first()
            d['nmc_code'] = nmc.nmc_code if nmc else None
        else:
            d['nmc_code'] = None
        result.append(d)

    matches = db.query(models.MatchResult).all()
    match_list = []
    for m in matches:
        md = {c.name: getattr(m, c.name) for c in m.__table__.columns}
        for k, v in md.items():
            if isinstance(v, datetime):
                md[k] = v.isoformat()
        match_list.append(md)

    return {"materials": result, "matches": match_list, "exported_at": datetime.utcnow().isoformat()}


# Deprecated mocked block removed.


# ─── Evaluation ───────────────────────────────────────────────────────────────

@app.post("/api/golden-test/run", tags=["Evaluation"])
def evaluate_model(db: Session = Depends(get_db)):
    import csv, os
    from sklearn.metrics import accuracy_score, precision_recall_fscore_support
    from .engine.normalizer import MaterialNormalizer
    from .engine.matcher import MaterialMatcher
    
    normalizer = MaterialNormalizer()
    matcher = MaterialMatcher()
    
    # Load dataset
    golden_csv = os.path.join(os.path.dirname(__file__), "..", "data", "golden_test_set.csv")
    if not os.path.exists(golden_csv):
        raise HTTPException(status_code=404, detail="Golden test set not found.")
        
    db.query(models.GoldenTestPair).delete()
    
    y_true = []
    y_pred = []
    
    pairs = []
    with open(golden_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            mat_a_dict = normalizer.normalize_description(row['material_a_description'])
            mat_b_dict = normalizer.normalize_description(row['material_b_description'])
            
            # Predict
            match_res = matcher.match_materials(mat_a_dict, mat_b_dict)
            pred_label = match_res['match_type']
            
            # DB entry
            pair = models.GoldenTestPair(
                material_a_description=row['material_a_description'],
                material_b_description=row['material_b_description'],
                material_a_cpse=row['material_a_cpse'],
                material_b_cpse=row['material_b_cpse'],
                expected_label=row['expected_label'],
                predicted_label=pred_label,
                predicted_confidence=match_res.get('confidence_score', 0),
                is_correct=(pred_label == row['expected_label']),
                evaluated_at=datetime.utcnow()
            )
            pairs.append(pair)
            
            y_true.append(row['expected_label'])
            y_pred.append(pred_label)
            
    db.add_all(pairs)
    db.commit()
    
    # Calc metrics
    acc = accuracy_score(y_true, y_pred)
    prec, rec, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='weighted', zero_division=0)
    
    return {
        "accuracy": float(acc),
        "precision": float(prec),
        "recall": float(rec),
        "f1": float(f1),
        "samples": len(y_true),
        "evaluated_at": datetime.utcnow().isoformat()
    }


@app.get("/api/golden-test/results", tags=["Evaluation"])
def get_evaluation_metrics(db: Session = Depends(get_db)):
    from sklearn.metrics import accuracy_score, precision_recall_fscore_support
    pairs = db.query(models.GoldenTestPair).all()
    if not pairs:
        return {"accuracy": 0, "precision": 0, "recall": 0, "f1": 0, "samples": 0, "evaluated_at": None}
        
    y_true = [p.expected_label for p in pairs]
    y_pred = [p.predicted_label for p in pairs]
    
    acc = accuracy_score(y_true, y_pred)
    prec, rec, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='weighted', zero_division=0)
    
    return {
        "accuracy": float(acc),
        "precision": float(prec),
        "recall": float(rec),
        "f1": float(f1),
        "samples": len(y_true),
        "evaluated_at": pairs[0].evaluated_at.isoformat() if pairs[0].evaluated_at else None
    }

@app.get("/api/reranker/status", tags=["Reranker"])
def get_reranker_status(db: Session = Depends(get_db)):
    db_count = db.query(models.ReviewerFeedback).count()
    status = reranker.get_status()
    status['feedback_count'] = db_count
    if not status['trained']:
        status['message'] = f'Insufficient feedback data for retraining. {max(0, status["min_required"] - db_count)} more reviews needed.' if db_count < status["min_required"] else 'Ready to train. Hit the endpoint.'
    return status


@app.post("/api/reranker/train", tags=["Reranker"])
def train_reranker_endpoint(db: Session = Depends(get_db)):
    feedback_rows = db.query(models.ReviewerFeedback).all()
    feedback_data = []
    for row in feedback_rows:
        feedback_data.append({
            'features': {
                'semantic_similarity': row.semantic_similarity,
                'attribute_similarity': row.attribute_similarity,
                'technical_similarity': row.technical_similarity,
                'text_similarity': row.text_similarity,
                'category_similarity': row.category_similarity
            },
            'prediction': row.predicted_match_type,
            'decision': row.decision,
            'label': 1 if row.decision == 'approved' else 0
        })
        
    result = reranker.train(feedback_data)
    return {"status": "success", "result": result, "feedback_count": len(feedback_data)}


# ─── National Rationalization & Families ──────────────────────────────────────

@app.get("/api/material-families", tags=["National Rationalization"])
def get_material_families(db: Session = Depends(get_db)):
    codes = db.query(models.CommonNationalCode).all()
    families = []
    for c in codes:
        # get mapped materials
        maps = db.query(models.NMCMapping).filter_by(nmc_id=c.id).all()
        member_materials = []
        cpses = set()
        local_codes = set()
        
        for mp in maps:
            mat = db.query(models.Material).filter_by(id=mp.material_id).first()
            if mat:
                member_materials.append(material_to_dict(mat, db))
                cpses.add(mat.cpse)
                local_codes.add(f"{mat.cpse}/{mat.material_code}")
                
        # canonical description
        attrs = json.loads(c.normalized_attributes) if c.normalized_attributes else {}
        canonical = "Canonical description unavailable: insufficient technical attributes"
        if len(attrs) >= 2:
            parts = []
            if 'category' in attrs:
                parts.append(f"{str(attrs['category']).upper()}")
            # Build string from other keys
            other_parts = []
            for k, v in attrs.items():
                if k != 'category':
                    other_parts.append(f"{k.upper().replace('_', ' ')} {v}")
            if other_parts:
                parts.append(", ".join(other_parts))
            canonical = ", ".join(parts)

        families.append({
            "id": c.id,
            "nmc_code": c.nmc_code,
            "category": c.category,
            "canonical_description": canonical,
            "cpse_count": len(cpses),
            "local_code_count": len(local_codes),
            "cpses": list(cpses),
            "local_codes": list(local_codes),
            "common_attributes": attrs,
            "conflicting_attributes": {},
            "member_materials": member_materials,
            "status": "Active"
        })
    return {"families": families}

@app.get("/api/rationalization/summary", tags=["National Rationalization"])
def get_rationalization_summary(db: Session = Depends(get_db)):
    total_materials = db.query(models.Material).count()
    unique_cpses = db.query(func.count(func.distinct(models.Material.cpse))).scalar()
    
    nmcs = db.query(models.CommonNationalCode).all()
    total_families = len(nmcs)
    
    potential_consolidation = 0
    for c in nmcs:
        count = db.query(models.NMCMapping).filter_by(nmc_id=c.id).count()
        if count > 1:
            potential_consolidation += (count - 1)
            
    dup_types = ['IDENTICAL', 'DUPLICATE', 'NEAR_DUPLICATE']
    dup_matches = db.query(models.MatchResult).filter(
        models.MatchResult.match_type.in_(dup_types)).all()
    dup_mat_ids = set()
    for m in dup_matches:
        dup_mat_ids.add(m.material_a_id)
        dup_mat_ids.add(m.material_b_id)

    total_hist_cost = 0
    if dup_mat_ids:
        cost_res = db.query(func.sum(models.Material.historical_cost)).filter(
            models.Material.id.in_(list(dup_mat_ids))).scalar()
        total_hist_cost = cost_res or 0
    indicative_savings = total_hist_cost * 0.20
    
    return {
        "materials_analyzed": total_materials,
        "unique_cpses": unique_cpses,
        "current_local_codes": total_materials,
        "material_families": total_families,
        "proposed_nmcs": total_families,
        "potential_consolidation": potential_consolidation,
        "indicative_savings": indicative_savings
    }

@app.get("/api/rationalization/opportunities", tags=["National Rationalization"])
def get_rationalization_opportunities(db: Session = Depends(get_db)):
    codes = db.query(models.CommonNationalCode).all()
    opps = []
    for c in codes:
        maps = db.query(models.NMCMapping).filter_by(nmc_id=c.id).all()
        if len(maps) > 1:
            cpses = set([mp.cpse for mp in maps])
            opps.append({
                "nmc_code": c.nmc_code,
                "category": c.category,
                "description": c.description,
                "cpse_count": len(cpses),
                "local_code_count": len(maps),
                "potential_consolidation": len(maps) - 1
            })
            
    opps.sort(key=lambda x: x["potential_consolidation"], reverse=True)
    return {"opportunities": opps[:10]}

@app.get("/api/rationalization/cpse-comparison", tags=["National Rationalization"])
def get_cpse_comparison(db: Session = Depends(get_db)):
    cpses = db.query(models.Material.cpse).distinct().all()
    cpses = [c[0] for c in cpses if c[0]]
    
    result = []
    for cpse in cpses:
        mats = db.query(models.Material).filter_by(cpse=cpse).all()
        mat_count = len(mats)
        
        complete_mats = 0
        for m in mats:
            if m.extracted_attributes:
                try:
                    attrs = json.loads(m.extracted_attributes)
                    if len(attrs) >= 2:
                        complete_mats += 1
                except:
                    pass
        
        data_quality = (complete_mats / mat_count * 100) if mat_count > 0 else 0
        
        mat_ids = [m.id for m in mats]
        if mat_ids:
            maps = db.query(models.NMCMapping).filter(
                models.NMCMapping.cpse == cpse,
                models.NMCMapping.material_id.in_(mat_ids)
            ).all()
            families_count = len(set([mp.nmc_id for mp in maps]))
            
            dup_types = ['IDENTICAL', 'DUPLICATE', 'NEAR_DUPLICATE']
            duplicates = db.query(models.MatchResult).filter(
                or_(
                    models.MatchResult.material_a_id.in_(mat_ids),
                    models.MatchResult.material_b_id.in_(mat_ids)
                ),
                models.MatchResult.match_type.in_(dup_types)
            ).count()
        else:
            families_count = 0
            duplicates = 0
            
        result.append({
            "cpse": cpse,
            "materials": mat_count,
            "potential_duplicates": duplicates,
            "families": families_count,
            "data_completeness": data_quality
        })
        
    return {"comparison": result}

# ─── Seed Data ────────────────────────────────────────────────────────────────

@app.post("/api/seed", tags=["Seed Data"])
def seed_data(db: Session = Depends(get_db)):
    sample_csv = os.path.join(DATA_DIR, "sample_materials.csv")
    golden_csv = os.path.join(DATA_DIR, "golden_test_set.csv")

    materials_added = 0
    golden_added = 0
    messages = []

    # Load sample materials
    if os.path.exists(sample_csv):
        with open(sample_csv, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cpse = (row.get('cpse') or '').strip()
                code = (row.get('material_code') or '').strip()
                desc = (row.get('description') or '').strip()

                if not cpse or not code:
                    continue

                if db.query(models.Material).filter_by(cpse=cpse, material_code=code).first():
                    continue

                norm = normalizer.normalize_description(desc)
                attrs = norm.get('attributes', {})

                m = models.Material(
                    cpse=cpse,
                    material_code=code,
                    description=desc,
                    normalized_description=norm.get('normalized'),
                    category=attrs.get('category') or (row.get('category') or '').strip() or None,
                    material_type=attrs.get('material_type') or (row.get('material_type') or '').strip() or None,
                    unit=(row.get('unit') or '').strip() or None,
                    specification=(row.get('specification') or '').strip() or None,
                    manufacturer=(row.get('manufacturer') or '').strip() or None,
                    historical_quantity=float(row.get('historical_quantity') or 0),
                    historical_cost=float(row.get('historical_cost') or 0),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(m)
                db.flush()

                for k, v in attrs.items():
                    db.add(models.NormalizedAttribute(
                        material_id=m.id, attribute_name=k,
                        attribute_value=str(v), confidence=norm.get('confidence', 0.5)
                    ))

                materials_added += 1

        messages.append(f"{materials_added} sample materials loaded.")
    else:
        messages.append("Sample CSV not found.")

    # Load golden test pairs
    if os.path.exists(golden_csv):
        with open(golden_csv, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                desc_a = (row.get('material_a_description') or '').strip()
                desc_b = (row.get('material_b_description') or '').strip()
                expected = (row.get('expected_label') or '').strip()

                if not desc_a or not desc_b or not expected:
                    continue

                # Check if pair already exists
                existing = db.query(models.GoldenTestPair).filter_by(
                    material_a_description=desc_a, material_b_description=desc_b
                ).first()
                if existing:
                    continue

                g = models.GoldenTestPair(
                    material_a_description=desc_a,
                    material_b_description=desc_b,
                    material_a_cpse=(row.get('material_a_cpse') or '').strip(),
                    material_b_cpse=(row.get('material_b_cpse') or '').strip(),
                    expected_label=expected
                )
                db.add(g)
                golden_added += 1

        messages.append(f"{golden_added} golden test pairs loaded.")
    else:
        messages.append("Golden test CSV not found.")

    if materials_added > 0:
        log_audit(db, "data_seeded", "system", details={
            "materials": materials_added, "golden_pairs": golden_added
        })

    db.commit()

    return {
        "status": "success",
        "materials_added": materials_added,
        "golden_pairs_added": golden_added,
        "messages": messages
    }
