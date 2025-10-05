import json
import os
from datetime import datetime, timezone
from decimal import Decimal

from common.auth_lambda import get_user_id_from_event
from common.dynamodb import db

# Optional: ULID for sortable unique IDs; else fallback to uuid4
try:
    import ulid
    def new_id(prefix: str) -> str:
        return f"{prefix}-{ulid.new()}"
except Exception:
    import uuid
    def new_id(prefix: str) -> str:
        return f"{prefix}-{uuid.uuid4()}"

def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def _cors_headers(origin: str = "*"):
    # In prod you should reflect/whitelist exact origins
    return {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': origin,
        'Access-Control-Allow-Methods': 'GET, POST, PUT, PATCH, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-MTP-Dev-User'
    }

def _ok(body: dict, origin: str = "*", code: int = 200):
    return {'statusCode': code, 'headers': _cors_headers(origin), 'body': json.dumps(body, default=decimal_default)}

def _err(code: int, message: str, origin: str = "*"):
    return {'statusCode': code, 'headers': _cors_headers(origin), 'body': json.dumps({'message': message})}

def _get_origin(event: dict) -> str:
    # Optional: echo origin if you want stricter CORS later
    return (event.get('headers') or {}).get('origin') or '*'

def handler(event, context):
    try:
        http_method = event.get('httpMethod', event.get('requestContext', {}).get('http', {}).get('method', 'GET'))
        path = event.get('path', event.get('rawPath', '/'))
        origin = _get_origin(event)
        qs = event.get('queryStringParameters') or {}

        # Auth (prod-safe + dev override)
        try:
            user_id = get_user_id_from_event(event)
        except PermissionError:
            # Allow unauthenticated only for /v1/health
            if path == '/v1/health':
                return _ok({'message': 'API is healthy'}, origin)
            return _err(401, 'Unauthorized', origin)

        # ---- Health ----
        if path == '/v1/health' and http_method == 'GET':
            return _ok({'message': 'API is healthy'}, origin)
        
        # ---- Notes ----
        if path == '/v1/notes' and http_method == 'POST':
            body = json.loads(event.get('body') or '{}')
            note_id = new_id("note")
            item = db.create_note_item(user_id, note_id, body)
            db.put_item(item)
            return _ok({'message': 'Note created successfully', 'noteId': note_id}, origin, 201)
        
        if path == '/v1/notes' and http_method == 'GET':
            limit = int(qs.get('limit', '50'))
            lek = qs.get('lastKey')
            last_key = json.loads(lek) if lek else None
            resp = db.query_gsi1(gsi1pk=f'NOTE#{user_id}', limit=limit, last_evaluated_key=last_key)
            items = []
            for it in resp.get('Items', []):
                note = {
                    'noteId': it.get('noteId'),
                    'date': it.get('date'),
                    'text': it.get('text', ''),
                    'createdAt': it.get('createdAt'),
                    'updatedAt': it.get('updatedAt'),
                }
                for f in ["direction", "session", "risk", "win_amount", "strategyId", "hit_miss"]:
                    if f in it:
                        note[f] = it[f]
                items.append(note)
            out = {'notes': items}
            if 'LastEvaluatedKey' in resp:
                out['lastKey'] = resp['LastEvaluatedKey']
            return _ok(out, origin)
        
        # ---- Strategies ----
        if path == '/v1/strategies' and http_method == 'POST':
            body = json.loads(event.get('body') or '{}')
            strategy_id = new_id("strategy")
            item = db.create_strategy_item(user_id, strategy_id, body)
            db.put_item(item)
            return _ok({'message': 'Strategy created successfully', 'strategyId': strategy_id}, origin, 201)
        
        if path == '/v1/strategies' and http_method == 'GET':
            limit = int(qs.get('limit', '50'))
            lek = qs.get('lastKey')
            last_key = json.loads(lek) if lek else None
            resp = db.query_gsi1(gsi1pk=f'STRAT#{user_id}', limit=limit, last_evaluated_key=last_key)
            items = []
            for it in resp.get('Items', []):
                dsl = {}
                try:
                    # If stored as string
                    if isinstance(it.get('dsl'), str):
                        dsl = json.loads(it['dsl'])
                    elif isinstance(it.get('dsl'), dict):
                        dsl = it['dsl']
                except Exception:
                    dsl = {}
                items.append({
                    'strategyId': it.get('strategyId'),
                    'name': it.get('name'),
                    'market': it.get('market'),
                    'timeframe': it.get('timeframe'),
                    'dsl': dsl,
                    'createdAt': it.get('createdAt'),
                    'updatedAt': it.get('updatedAt')
                })
            out = {'strategies': items}
            if 'LastEvaluatedKey' in resp:
                out['lastKey'] = resp['LastEvaluatedKey']
            return _ok(out, origin)
        
        if path.startswith('/v1/strategies/') and http_method == 'GET':
            strategy_id = path.split('/')[-1]
            pk, sk = f'USER#{user_id}', f'STRAT#{strategy_id}'
            it = db.get_item(pk, sk)
            if not it:
                return _err(404, 'Strategy not found', origin)
            dsl = {}
            try:
                d = it.get('dsl')
                dsl = json.loads(d) if isinstance(d, str) else (d or {})
            except Exception:
                dsl = {}
            return _ok({
                'strategy': {
                    'strategyId': it.get('strategyId'),
                    'name': it.get('name'),
                    'market': it.get('market'),
                    'timeframe': it.get('timeframe'),
                    'dsl': dsl,
                    'createdAt': it.get('createdAt'),
                    'updatedAt': it.get('updatedAt'),
                }
            }, origin)
        
        if path.startswith('/v1/strategies/') and http_method in ('PUT', 'PATCH'):
            strategy_id = path.split('/')[-1]
            body = json.loads(event.get('body') or '{}')
            pk, sk = f'USER#{user_id}', f'STRAT#{strategy_id}'
            if not db.get_item(pk, sk):
                return _err(404, 'Strategy not found', origin)

            update_expression = "SET #updatedAt = :updatedAt"
            eav = {':updatedAt': _now_iso()}
            ean = {'#updatedAt': 'updatedAt'}

            for field in ["name", "market", "timeframe", "dsl"]:
                if field in body and body[field] not in (None, ""):
                    ean[f'#{field}'] = field
                    eav[f':{field}'] = json.dumps(body['dsl']) if field == 'dsl' and not isinstance(body['dsl'], str) else body[field]
                    update_expression += f", #{field} = :{field}"

            updated = db.update_item(pk, sk, update_expression, eav, ean)['Attributes']
            return _ok({'message': 'Strategy updated successfully'}, origin)
        
        if path.startswith('/v1/notes/') and http_method in ('PUT', 'PATCH'):
            note_id = path.split('/')[-1]
            body = json.loads(event.get('body') or '{}')

            # Ensure exists
            pk, sk = f'USER#{user_id}', f'NOTE#{note_id}'
            existing = db.get_item(pk, sk)
            if not existing:
                return _err(404, 'Note not found', origin)

            update_expression = "SET #updatedAt = :updatedAt"
            eav = {':updatedAt': _now_iso()}
            ean = {'#updatedAt': 'updatedAt'}

            for field in ["date", "text", "direction", "session", "risk", "win_amount", "strategyId", "hit_miss"]:
                if field in body and body[field] not in (None, ""):
                    ean[f'#{field}'] = field
                    eav[f':{field}'] = body[field]
                    update_expression += f", #{field} = :{field}"

            # If date changed, update GSI1SK
            if 'date' in body and body['date']:
                ean['#GSI1SK'] = 'GSI1SK'
                eav[':gsi1sk'] = f"{body['date']}#{note_id}"
                update_expression += ", #GSI1SK = :gsi1sk"

            updated = db.update_item(pk, sk, update_expression, eav, ean)['Attributes']

            # Build response
            resp_note = {
                'noteId': updated.get('noteId'),
                'date': updated.get('date'),
                'text': updated.get('text', ''),
                'createdAt': updated.get('createdAt'),
                'updatedAt': updated.get('updatedAt')
            }
            for f in ["direction", "session", "risk", "win_amount", "strategyId", "hit_miss"]:
                if f in updated:
                    resp_note[f] = updated[f]

            return _ok({'message': 'Note updated successfully', 'note': resp_note}, origin)
        
        if path.startswith('/v1/notes/') and http_method == 'DELETE':
            note_id = path.split('/')[-1]
            pk, sk = f'USER#{user_id}', f'NOTE#{note_id}'
            if not db.get_item(pk, sk):
                return _err(404, 'Note not found', origin)
            db.delete_item(pk, sk)
            return _ok({'message': 'Note deleted successfully'}, origin)
        
        if path.startswith('/v1/strategies/') and http_method == 'DELETE':
            strategy_id = path.split('/')[-1]
            pk, sk = f'USER#{user_id}', f'STRAT#{strategy_id}'
            if not db.get_item(pk, sk):
                return _err(404, 'Strategy not found', origin)
            db.delete_item(pk, sk)
            return _ok({'message': 'Strategy deleted successfully'}, origin)
        
        # ---- Reporting (simple evaluable feature) ----
        if path == '/v1/reports/notes-summary' and http_method == 'GET':
            # Optional date filtering (assumes client uses ISO)
            date_from = (qs.get('from') or "")
            date_to = (qs.get('to') or "")
            # We list from GSI1 (NOTE#{user}) and then filter dates if provided.
            resp = db.query_gsi1(f'NOTE#{user_id}', limit=int(qs.get('limit', '200')))
            notes = resp.get('Items', [])
            def in_range(d: str) -> bool:
                if not d: return True
                if date_from and d < date_from: return False
                if date_to and d > date_to: return False
                return True
            filtered = [n for n in notes if in_range(n.get('date', ''))]

            total = len(filtered)
            by_hit = {}
            by_session = {}
            win_sum, win_count = 0.0, 0
            for n in filtered:
                hm = n.get('hit_miss', 'UNKNOWN')
                by_hit[hm] = by_hit.get(hm, 0) + 1
                sess = n.get('session', 'UNKNOWN')
                by_session[sess] = by_session.get(sess, 0) + 1
                if 'win_amount' in n:
                    try:
                        win_sum += float(n['win_amount'])
                        win_count += 1
                    except Exception:
                        pass

            avg_win = (win_sum / win_count) if win_count else 0.0
            return _ok({
                'summary': {
                    'totalNotes': total,
                    'byHitMiss': by_hit,
                    'bySession': by_session,
                    'averageWinAmount': avg_win
                }
            }, origin)

        # ---- Fallback ----
        return _err(404, 'Not found', origin)
            
    except Exception as e:
        # Basic error path
        print(f"Error: {str(e)}")
        return _err(500, f'Internal server error: {str(e)}', _get_origin(event))