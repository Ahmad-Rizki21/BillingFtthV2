from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
import uuid
from datetime import datetime, timedelta

from fastapi.security import OAuth2PasswordRequestForm
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
security = HTTPBearer()

# Impor model dan skema secara langsung
from ..models.user import User as UserModel
from ..models.role import Role as RoleModel
from ..schemas.user import User as UserSchema, UserCreate, UserUpdate
from ..database import get_db

# passlib untuk hashing password
from passlib.context import CryptContext

from .. import auth
from ..config import settings

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

# Fungsi untuk mendapatkan current user dari token
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    try:
        payload = auth.verify_access_token(credentials.credentials)
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user = await db.get(UserModel, user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Endpoint yang sudah ada (tidak diubah)
@router.post("/token", summary="Create access token for user")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: AsyncSession = Depends(get_db)
):
    query = select(UserModel).where(UserModel.email == form_data.username)
    user = (await db.execute(query)).scalar_one_or_none()

    if not user or not auth.verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email atau password salah",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email, "user_id": user.id},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserSchema)
async def get_current_user_info(current_user: UserModel = Depends(get_current_user)):
    return current_user

@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    existing_user_query = await db.execute(select(UserModel).where(UserModel.email == user.email))
    if existing_user_query.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User dengan email '{user.email}' sudah ada."
        )

    if user.role_id:
        role = await db.get(RoleModel, user.role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role dengan id {user.role_id} tidak ditemukan."
            )

    hashed_password = get_password_hash(user.password)
    user_data = user.model_dump()
    user_data['password'] = hashed_password

    db_user = UserModel(**user_data)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

@router.get("/", response_model=List[UserSchema])
async def get_all_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserModel))
    return result.scalars().all()

@router.get("/{user_id}", response_model=UserSchema)
async def get_user_by_id(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await db.get(UserModel, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.patch("/{user_id}", response_model=UserSchema)
async def update_user(user_id: int, user_update: UserUpdate, db: AsyncSession = Depends(get_db)):
    db_user = await db.get(UserModel, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user_update.model_dump(exclude_unset=True)
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
    db_user = await db.get(UserModel, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    await db.delete(db_user)
    await db.commit()
    return None

# === Endpoint Baru untuk Forgot Password (Tanpa Email) ===
@router.post("/forgot-password")
async def forgot_password(email: str, db: AsyncSession = Depends(get_db)):
    query = select(UserModel).where(UserModel.email == email)
    user = (await db.execute(query)).scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User dengan email tersebut tidak ditemukan"
        )

    # Generate token reset (disimpan di user)
    reset_token = str(uuid.uuid4())
    reset_token_expires = datetime.utcnow() + timedelta(hours=1)  # Token berlaku 1 jam

    user.reset_token = reset_token
    user.reset_token_expires = reset_token_expires
    db.add(user)
    await db.commit()

    return {"message": "Silakan lanjutkan ke langkah reset password dengan token ini.", "token": reset_token}

# === Endpoint Baru untuk Reset Password ===
@router.post("/reset-password")
async def reset_password(email: str, new_password: str, token: str, db: AsyncSession = Depends(get_db)):
    query = select(UserModel).where(UserModel.email == email, UserModel.reset_token == token)
    user = (await db.execute(query)).scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email atau token reset tidak valid"
        )

    if user.reset_token_expires and user.reset_token_expires < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token reset telah kadaluarsa"
        )

    # Hash password baru
    hashed_password = get_password_hash(new_password)

    # Update password dan hapus token
    user.password = hashed_password
    user.reset_token = None
    user.reset_token_expires = None
    db.add(user)
    await db.commit()

    return {"message": "Password berhasil diatur ulang. Silakan login dengan password baru."}