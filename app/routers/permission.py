from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models.permission import Permission
from ..database import get_db
from ..schemas.permission import PermissionCreate, Permission
from ..config import MENUS

router = APIRouter(
    prefix="/permissions",
    tags=["Permissions"],
    responses={404: {"description": "Not found"}},
)

@router.post("/generate", response_model=list[Permission])
async def generate_permissions(db: AsyncSession = Depends(get_db)):
    permissions = []
    actions = ["view", "edit", "delete"]  # Aksi dasar untuk setiap menu

    for menu in MENUS:
        for action in actions:
            permission_name = f"{action}_{menu.lower().replace(' ', '_')}"
            # Cek apakah permission sudah ada
            result = await db.execute(select(Permission).where(Permission.name == permission_name))
            existing_permission = result.scalars().first()
            if not existing_permission:
                new_permission = Permission(name=permission_name)
                db.add(new_permission)
                permissions.append(new_permission)
    
    await db.commit()
    for permission in permissions:
        await db.refresh(permission)
    return permissions

@router.get("/", response_model=list[Permission])
async def get_permissions(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Permission))
    return result.scalars().all()