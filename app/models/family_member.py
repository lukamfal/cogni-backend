from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class FamilyMember(Base):
    __tablename__ = "family_members"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # idoso dono do cadastro

    name = Column(String(120), nullable=False)
    relation = Column(String(60), nullable=False)  # ex: "filho", "neta", "esposa"
    photo_url = Column(String, nullable=True)           # URL no S3
    photo_key = Column(String, nullable=True)           # key no S3 para deleção

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="family_members")
