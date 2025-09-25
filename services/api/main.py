from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import uuid
from datetime import datetime
import json

from common.auth import get_user_id_from_request
from common.dynamodb import DynamoDBClient, create_note_item, create_strategy_item

app = FastAPI(title="MyTraderPal API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Will be tightened in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get DynamoDB client
def get_db():
    return DynamoDBClient()

# Pydantic models
class NoteCreate(BaseModel):
    date: str = Field(..., description="ISO date string")
    text: str = Field(..., description="Note text")
    direction: Optional[str] = Field(None, description="Trade direction")
    session: Optional[str] = Field(None, description="Trading session")
    risk: Optional[float] = Field(None, description="Risk amount")
    win_amount: Optional[float] = Field(None, description="Win amount")
    tags: Optional[List[str]] = Field(None, description="Tags")
    strategyId: Optional[str] = Field(None, description="Associated strategy ID")

class NoteUpdate(BaseModel):
    date: Optional[str] = None
    text: Optional[str] = None
    direction: Optional[str] = None
    session: Optional[str] = None
    risk: Optional[float] = None
    win_amount: Optional[float] = None
    tags: Optional[List[str]] = None
    strategyId: Optional[str] = None

class StrategyCreate(BaseModel):
    name: str = Field(..., description="Strategy name")
    market: str = Field(..., description="Market (e.g., forex, stocks)")
    timeframe: str = Field(..., description="Timeframe (e.g., 1h, 4h, 1d)")
    dsl: Optional[Dict[str, Any]] = Field(None, description="Strategy DSL as JSON")

class StrategyUpdate(BaseModel):
    name: Optional[str] = None
    market: Optional[str] = None
    timeframe: Optional[str] = None
    dsl: Optional[Dict[str, Any]] = None

class NoteResponse(BaseModel):
    noteId: str
    userId: str
    date: str
    text: str
    direction: Optional[str] = None
    session: Optional[str] = None
    risk: Optional[float] = None
    win_amount: Optional[float] = None
    tags: Optional[List[str]] = None
    strategyId: Optional[str] = None
    createdAt: str
    updatedAt: str

class StrategyResponse(BaseModel):
    strategyId: str
    userId: str
    name: str
    market: str
    timeframe: str
    dsl: Optional[Dict[str, Any]] = None
    createdAt: str
    updatedAt: str

class ListResponse(BaseModel):
    items: List[Any]
    lastEvaluatedKey: Optional[Dict[str, Any]] = None

# Notes endpoints
@app.post("/notes", response_model=NoteResponse)
async def create_note(
    note_data: NoteCreate,
    request: Request,
    db: DynamoDBClient = Depends(get_db)
):
    """Create a new note."""
    user_id = get_user_id_from_request(request)
    note_id = str(uuid.uuid4())
    
    note_item = create_note_item(user_id, note_id, note_data.dict())
    db.put_item(note_item)
    
    return NoteResponse(**note_item)

@app.get("/notes", response_model=ListResponse)
async def list_notes(
    request: Request,
    limit: Optional[int] = 20,
    cursor: Optional[str] = None,
    db: DynamoDBClient = Depends(get_db)
):
    """List notes for the user."""
    user_id = get_user_id_from_request(request)
    
    last_evaluated_key = None
    if cursor:
        try:
            last_evaluated_key = json.loads(cursor)
        except:
            raise HTTPException(status_code=400, detail="Invalid cursor format")
    
    response = db.query_gsi1(f'NOTE#{user_id}', limit=limit, last_evaluated_key=last_evaluated_key)
    
    # Convert cursor back to string
    cursor_str = None
    if 'LastEvaluatedKey' in response:
        cursor_str = json.dumps(response['LastEvaluatedKey'])
    
    return ListResponse(
        items=response.get('Items', []),
        lastEvaluatedKey=cursor_str
    )

@app.get("/notes/{note_id}", response_model=NoteResponse)
async def get_note(
    note_id: str,
    request: Request,
    db: DynamoDBClient = Depends(get_db)
):
    """Get a specific note."""
    user_id = get_user_id_from_request(request)
    
    note = db.get_item(f'USER#{user_id}', f'NOTE#{note_id}')
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    return NoteResponse(**note)

@app.put("/notes/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: str,
    note_data: NoteUpdate,
    request: Request,
    db: DynamoDBClient = Depends(get_db)
):
    """Update a note."""
    user_id = get_user_id_from_request(request)
    
    # Check if note exists
    note = db.get_item(f'USER#{user_id}', f'NOTE#{note_id}')
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Build update expression
    update_data = note_data.dict(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    update_data['updatedAt'] = datetime.utcnow().isoformat()
    
    # Update GSI1SK if date changed
    if 'date' in update_data:
        update_data['GSI1SK'] = f"{update_data['date']}#{note_id}"
    
    update_expression = "SET " + ", ".join([f"{k} = :{k}" for k in update_data.keys()])
    expression_values = {f":{k}": v for k, v in update_data.items()}
    
    db.update_item(f'USER#{user_id}', f'NOTE#{note_id}', update_expression, expression_values)
    
    # Return updated note
    updated_note = db.get_item(f'USER#{user_id}', f'NOTE#{note_id}')
    return NoteResponse(**updated_note)

@app.delete("/notes/{note_id}")
async def delete_note(
    note_id: str,
    request: Request,
    db: DynamoDBClient = Depends(get_db)
):
    """Delete a note."""
    user_id = get_user_id_from_request(request)
    
    # Check if note exists
    note = db.get_item(f'USER#{user_id}', f'NOTE#{note_id}')
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    db.delete_item(f'USER#{user_id}', f'NOTE#{note_id}')
    return {"message": "Note deleted successfully"}

# Strategies endpoints
@app.post("/strategies", response_model=StrategyResponse)
async def create_strategy(
    strategy_data: StrategyCreate,
    request: Request,
    db: DynamoDBClient = Depends(get_db)
):
    """Create a new strategy."""
    user_id = get_user_id_from_request(request)
    strategy_id = str(uuid.uuid4())
    
    strategy_item = create_strategy_item(user_id, strategy_id, strategy_data.dict())
    db.put_item(strategy_item)
    
    return StrategyResponse(**strategy_item)

@app.get("/strategies", response_model=ListResponse)
async def list_strategies(
    request: Request,
    limit: Optional[int] = 20,
    cursor: Optional[str] = None,
    db: DynamoDBClient = Depends(get_db)
):
    """List strategies for the user."""
    user_id = get_user_id_from_request(request)
    
    last_evaluated_key = None
    if cursor:
        try:
            last_evaluated_key = json.loads(cursor)
        except:
            raise HTTPException(status_code=400, detail="Invalid cursor format")
    
    response = db.query_gsi1(f'STRAT#{user_id}', limit=limit, last_evaluated_key=last_evaluated_key)
    
    # Convert cursor back to string
    cursor_str = None
    if 'LastEvaluatedKey' in response:
        cursor_str = json.dumps(response['LastEvaluatedKey'])
    
    return ListResponse(
        items=response.get('Items', []),
        lastEvaluatedKey=cursor_str
    )

@app.get("/strategies/{strategy_id}", response_model=StrategyResponse)
async def get_strategy(
    strategy_id: str,
    request: Request,
    db: DynamoDBClient = Depends(get_db)
):
    """Get a specific strategy."""
    user_id = get_user_id_from_request(request)
    
    strategy = db.get_item(f'USER#{user_id}', f'STRAT#{strategy_id}')
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    return StrategyResponse(**strategy)

@app.put("/strategies/{strategy_id}", response_model=StrategyResponse)
async def update_strategy(
    strategy_id: str,
    strategy_data: StrategyUpdate,
    request: Request,
    db: DynamoDBClient = Depends(get_db)
):
    """Update a strategy."""
    user_id = get_user_id_from_request(request)
    
    # Check if strategy exists
    strategy = db.get_item(f'USER#{user_id}', f'STRAT#{strategy_id}')
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    # Build update expression
    update_data = strategy_data.dict(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    update_data['updatedAt'] = datetime.utcnow().isoformat()
    
    update_expression = "SET " + ", ".join([f"{k} = :{k}" for k in update_data.keys()])
    expression_values = {f":{k}": v for k, v in update_data.items()}
    
    db.update_item(f'USER#{user_id}', f'STRAT#{strategy_id}', update_expression, expression_values)
    
    # Return updated strategy
    updated_strategy = db.get_item(f'USER#{user_id}', f'STRAT#{strategy_id}')
    return StrategyResponse(**updated_strategy)

@app.delete("/strategies/{strategy_id}")
async def delete_strategy(
    strategy_id: str,
    request: Request,
    db: DynamoDBClient = Depends(get_db)
):
    """Delete a strategy."""
    user_id = get_user_id_from_request(request)
    
    # Check if strategy exists
    strategy = db.get_item(f'USER#{user_id}', f'STRAT#{strategy_id}')
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    db.delete_item(f'USER#{user_id}', f'STRAT#{strategy_id}')
    return {"message": "Strategy deleted successfully"}

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

# Lambda handler
from mangum import Mangum
handler = Mangum(app)
