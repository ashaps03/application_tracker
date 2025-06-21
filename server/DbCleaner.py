from db import db
from model import UserJobData

def clean_db(firebase_uid):
    entries = UserJobData.query.filter_by(firebase_uid=firebase_uid).all()
    seen = {}

    for entry in entries:
        company = (entry.company or "").strip()
        position = (entry.position or "").strip()

        company_first = company.split()[0].lower() if company else "unknown"
        position_first = position.split()[0].lower() if position else "unknown"
        key = (company_first, position_first)

        # ❌ Rule 1: If both company and position are Unknown → delete immediately
        if company.lower() == "unknown" and position.lower() == "unknown":
            db.session.delete(entry)
            continue

        # Check for conflicting entries with same company
        conflicting_keys = [k for k in seen if k[0] == company_first]

        should_add = True

        for existing_key in conflicting_keys:
            existing = seen[existing_key]

            # ✅ Rule 2: If company is Unknown, but position differs → keep both
            if company.lower() == "unknown" and existing.position != position:
                continue

            # Same position → de-duplication logic
            if existing_key[1] == position_first:
                if entry.position == "Unknown" and existing.position != "Unknown":
                    db.session.delete(entry)
                    should_add = False
                elif existing.position == "Unknown" and entry.position != "Unknown":
                    db.session.delete(existing)
                    seen.pop(existing_key)
                    seen[key] = entry
                    should_add = False
                else:
                    prefer_existing = existing.status in ["Interviewing", "Offer", "Rejected"]
                    prefer_current = entry.status in ["Interviewing", "Offer", "Rejected"]

                    if prefer_current and not prefer_existing:
                        db.session.delete(existing)
                        seen.pop(existing_key)
                        seen[key] = entry
                    else:
                        db.session.delete(entry)
                    should_add = False
                break

            # Same company, one has Unknown position
            elif (
                entry.position == "Unknown" and existing.position != "Unknown"
            ):
                db.session.delete(entry)
                should_add = False
                break
            elif (
                existing.position == "Unknown" and entry.position != "Unknown"
            ):
                db.session.delete(existing)
                seen.pop(existing_key)
                seen[key] = entry
                should_add = False
                break

        if should_add:
            seen[key] = entry

    db.session.commit()
    print(f"✅ Cleaned DB for UID {firebase_uid}, reduced to {len(seen)} cleaned entries.")
