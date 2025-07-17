from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

# Impor model dan skema secara langsung
from ..models.role import Role as RoleModel
from ..schemas.role import Role as RoleSchema, RoleCreate, RoleUpdate
from ..database import get_db

router = APIRouter(
    prefix="/roles",
    tags=["Roles"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=RoleSchema, status_code=status.HTTP_201_CREATED)
async def create_role(role: RoleCreate, db: AsyncSession = Depends(get_db)):
    """
    Membuat role baru.
    Akan gagal jika nama role sudah ada.
    """
    # Validasi: Cek apakah nama role sudah ada
    existing_role_query = await db.execute(select(RoleModel).where(RoleModel.name == role.name))
    if existing_role_query.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Role dengan nama '{role.name}' sudah ada."
        )

    db_role = RoleModel(**role.model_dump())
    db.add(db_role)
    await db.commit()
    await db.refresh(db_role)
    return db_role

@router.get("/", response_model=List[RoleSchema])
async def get_all_roles(db: AsyncSession = Depends(get_db)):
    """
    Mengambil semua role yang ada.
    """
    result = await db.execute(select(RoleModel))
    return result.scalars().all()

@router.patch("/{role_id}", response_model=RoleSchema)
async def update_role(
    role_id: int, role_update: RoleUpdate, db: AsyncSession = Depends(get_db)
):
    """
    Memperbarui nama role berdasarkan ID.
    """
    db_role = await db.get(RoleModel, role_id)
    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # Jika nama baru dikirim, cek apakah nama tersebut sudah digunakan oleh role lain
    if role_update.name:
        existing_role_query = await db.execute(
            select(RoleModel).where(RoleModel.name == role_update.name, RoleModel.id != role_id)
        )
        if existing_role_query.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Nama role '{role_update.name}' sudah digunakan."
            )

    update_data = role_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_role, key, value)

    db.add(db_role)
    await db.commit()
    await db.refresh(db_role)
    return db_role

@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(role_id: int, db: AsyncSession = Depends(get_db)):
    """
    Menghapus role berdasarkan ID.
    """
    db_role = await db.get(RoleModel, role_id)
    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found")

    await db.delete(db_role)
    await db.commit()
    return None
