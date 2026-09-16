from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.family_member import FamilyMember
from app.schemas.family import FamilyMemberOut
from app.services.storage import upload_photo, delete_photo

router = APIRouter(prefix="/family", tags=["Familiares"])

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}


@router.get("/", response_model=list[FamilyMemberOut])
def list_family(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(FamilyMember).filter(FamilyMember.user_id == current_user.id).all()


@router.post("/", response_model=FamilyMemberOut, status_code=201)
async def add_family_member(
    name: str = Form(...),
    relation: str = Form(...),
    photo: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if photo.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, "Formato de imagem inválido. Use JPG, PNG ou WebP.")

    file_bytes = await photo.read()
    if len(file_bytes) > 5 * 1024 * 1024:
        raise HTTPException(400, "Foto muito grande. Máximo 5MB.")

    url, key = upload_photo(file_bytes, photo.content_type)

    member = FamilyMember(
        user_id=current_user.id,
        name=name,
        relation=relation,
        photo_url=url,
        photo_key=key,
    )
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


@router.delete("/{member_id}", status_code=204)
def delete_family_member(
    member_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    member = db.query(FamilyMember).filter(
        FamilyMember.id == member_id,
        FamilyMember.user_id == current_user.id,
    ).first()
    if not member:
        raise HTTPException(404, "Familiar não encontrado")
    if member.photo_key:
        delete_photo(member.photo_key)
    db.delete(member)
    db.commit()
