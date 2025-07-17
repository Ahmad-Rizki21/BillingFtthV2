from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

# Impor model dan skema secara langsung
from ..models.user import User as UserModel
from ..models.role import Role as RoleModel
from ..schemas.user import User as UserSchema, UserCreate, UserUpdate
from ..database import get_db

# passlib adalah library standar untuk hashing password
from passlib.context import CryptContext

# Konfigurasi untuk hashing password
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={404: {"description": "Not found"}},
)

def get_password_hash(password: str) -> str:
    """Fungsi untuk men-hash password."""
    return pwd_context.hash(password)

@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Membuat user baru.
    """
    # Validasi: Cek apakah email sudah terdaftar
    existing_user_query = await db.execute(select(UserModel).where(UserModel.email == user.email))
    if existing_user_query.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User dengan email '{user.email}' sudah ada."
        )

    # Validasi: Cek apakah role_id ada (jika diberikan)
    if user.role_id:
        role = await db.get(RoleModel, user.role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role dengan id {user.role_id} tidak ditemukan."
            )

    # Hash password sebelum disimpan
    hashed_password = get_password_hash(user.password)
    
    # Buat dictionary dari data user, ganti password dengan yang sudah di-hash
    user_data = user.model_dump()
    user_data['password'] = hashed_password

    db_user = UserModel(**user_data)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

@router.get("/", response_model=List[UserSchema])
async def get_all_users(db: AsyncSession = Depends(get_db)):
    """
    Mengambil semua data user.
    """
    result = await db.execute(select(UserModel))
    return result.scalars().all()

@router.get("/{user_id}", response_model=UserSchema)
async def get_user_by_id(user_id: int, db: AsyncSession = Depends(get_db)):
    """
    Mengambil satu user berdasarkan ID.
    """
    user = await db.get(UserModel, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.patch("/{user_id}", response_model=UserSchema)
async def update_user(user_id: int, user_update: UserUpdate, db: AsyncSession = Depends(get_db)):
    """
    Memperbarui data user.
    """
    db_user = await db.get(UserModel, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user_update.model_dump(exclude_unset=True)

    # Jika password di-update, hash password baru tersebut
    if "password" in update_data:
        update_data["password"] = get_password_hash(update_data["password"])

    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """
    Menghapus user berdasarkan ID.
    """
    db_user = await db.get(UserModel, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    await db.delete(db_user)
    await db.commit()
    return None
