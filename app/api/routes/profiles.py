from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.user import UserOut
from app.services.storage import upload_photo, InvalidImage

router = APIRouter(prefix="/profiles", tags=["Perfil"])


@router.get("/me", response_model=UserOut)
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/me/avatar", response_model=UserOut)
async def update_avatar(
    photo: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    file_bytes = await photo.read(5 * 1024 * 1024 + 1)
    try:
        url, _ = upload_photo(file_bytes, folder="avatars")
    except InvalidImage as e:
        raise HTTPException(400, str(e))
    current_user.avatar_url = url
    db.commit()
    db.refresh(current_user)
    return current_user
