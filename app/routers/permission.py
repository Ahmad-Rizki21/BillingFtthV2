# app/routers/permission.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from ..models.permission import Permission as PermissionModel
from ..database import get_db
from ..schemas.permission import Permission as PermissionSchema
from ..config import MENUS # <-- Impor daftar menu dari config

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
    # Definisikan semua aksi CRUD yang Anda inginkan
    actions = ["create", "view", "edit", "delete"] 

    for menu in MENUS:
        for action in actions:
            # Buat nama permission yang konsisten, contoh: "view_data_teknis"
            permission_name = f"{action}_{menu.lower().replace(' & ', '_').replace(' ', '_')}"
            
            # Cek apakah permission dengan nama ini sudah ada
            result = await db.execute(select(PermissionModel).where(PermissionModel.name == permission_name))
            existing_permission = result.scalars().first()
            
            # Jika belum ada, buat yang baru
            if not existing_permission:
                new_permission = PermissionModel(name=permission_name)
                db.add(new_permission)
                await db.flush() # Kirim ke DB untuk mendapatkan ID
                permissions_created.append(new_permission)
    
    await db.commit()

    # Refresh objek untuk memastikan data ter-update
    for p in permissions_created:
        await db.refresh(p)
        
    # Jika tidak ada permission baru yang dibuat, kembalikan pesan
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