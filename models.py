from typing import Optional, Dict, Any, List
from pydantic import BaseModel


class DatabaseConfig(BaseModel):
    host: str
    port: int
    user: str
    password: str
    database: str


class QueryRequest(BaseModel):
    question: str
    database_config: Optional[DatabaseConfig] = None


class QueryResponse(BaseModel):
    sql: str
    results: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None


class TrainingRequest(BaseModel):
    ddl: Optional[str] = None
    documentation: Optional[str] = None
    sql: Optional[List[str]] = None
    question: Optional[List[str]] = None
