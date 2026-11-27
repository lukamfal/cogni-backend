from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.family_member import FamilyMember
from app.schemas.family import FamilyMemberOut
from app.services.storage import upload_photo, delete_photo, InvalidImage

router = APIRouter(prefix="/family", tags=["Familiares"])


@router.get("/", response_model=list[FamilyMemberOut])
def list_family(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(FamilyMember).filter(FamilyMember.user_id == current_user.id).all()


@router.post("/", response_model=FamilyMemberOut, status_code=201)
async def add_family_member(
    name: str = Form(..., min_length=1, max_length=120),
    relation: str = Form(..., min_length=1, max_length=60),
    photo: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not name.strip():
        raise HTTPException(400, "Digite o nome do familiar.")

    # Lê no máximo 5MB + 1 byte: o suficiente para saber se passou do limite.
    file_bytes = await photo.read(5 * 1024 * 1024 + 1)
    try:
        url, key = upload_photo(file_bytes)
    except InvalidImage as e:
        raise HTTPException(400, str(e))

    member = FamilyMember(
        user_id=current_user.id,
        name=name.strip(),
        relation=relation.strip(),
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
