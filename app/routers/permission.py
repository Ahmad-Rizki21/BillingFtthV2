# app/routers/permission.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from ..models.permission import Permission as PermissionModel
from ..database import get_db
from ..schemas.permission import Permission as PermissionSchema
# --- PERBAIKAN DI SINI ---
from ..config import settings # Impor 'settings' bukan 'MENUS'

router = APIRouter(
    prefix="/permissions",
    tags=["Permissions"],
    responses={404: {"description": "Not found"}},
)

@router.post("/generate", response_model=List[PermissionSchema])
async def generate_permissions(db: AsyncSession = Depends(get_db)):
    """
    Membuat semua permission CRUD untuk setiap menu jika belum ada di database.
    """
    permissions_created = []
    actions = ["create", "view", "edit", "delete"] 

    # --- PERBAIKAN DI SINI ---
    # Gunakan settings.MENUS untuk mengakses daftar menu
    for menu in settings.MENUS:
        for action in actions:
            permission_name = f"{action}_{menu.lower().replace(' & ', '_').replace(' ', '_')}"
            
            result = await db.execute(select(PermissionModel).where(PermissionModel.name == permission_name))
            existing_permission = result.scalars().first()
            
            if not existing_permission:
                new_permission = PermissionModel(name=permission_name)
                db.add(new_permission)
                await db.flush()
                permissions_created.append(new_permission)
    
    await db.commit()

    for p in permissions_created:
        await db.refresh(p)
        
    if not permissions_created:
        raise HTTPException(
            status_code=status.HTTP_200_OK,
            detail="Semua permission sudah ter-generate."
        )

    return permissions_created

@router.get("/", response_model=List[PermissionSchema])
async def get_permissions(db: AsyncSession = Depends(get_db)):
    """Mengambil semua permission yang ada."""
    result = await db.execute(select(PermissionModel).order_by(PermissionModel.name))
    return result.scalars().all()