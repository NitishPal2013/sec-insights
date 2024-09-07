from typing import List, Optional
import logging
from fastapi import Depends, APIRouter, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.api.deps import get_db
from app.api import crud
from app import schema

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/")
async def get_documents(
    document_ids: Optional[List[UUID]] = Query(None),
    db: AsyncSession = Depends(get_db),
) -> List[schema.Document]:
    """
    Get all documents or documents by their ids
    """
    if document_ids is None:
        # If no ids provided, fetch all documents
        docs = await crud.fetch_documents(db)
    else:
        # If ids are provided, fetch documents by ids
        docs = await crud.fetch_documents(db, ids=document_ids)

    if len(docs) == 0:
        raise HTTPException(status_code=404, detail="Document(s) not found")

    return docs

from app.schema import Document
from app.api.crud import upsert_document_by_url
from app.db.session import SessionLocal


@router.post("/upsert")
async def upsert_document(url: str) -> UUID:
    """
    Upsert a document by URL
    """
    doc = Document(url=url, metadata_map={})
    
    try:
        async with SessionLocal() as db:
            document = await upsert_document_by_url(db, doc)
            print(f"Upserted document. Database ID:\n{document.id}")
            return document.id
    except Exception as e:
        logger.error(f"Error upserting document: {str(e)}")
        raise HTTPException(status_code=500, detail="Error upserting document")



@router.get("/{document_id}")
async def get_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> schema.Document:
    """
    Get all documents
    """
    docs = await crud.fetch_documents(db, id=document_id)
    if len(docs) == 0:
        raise HTTPException(status_code=404, detail="Document not found")

    return docs[0]
