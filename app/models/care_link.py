from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint, Enum as SAEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class CareLinkStatus(str, enum.Enum):
    PENDING = "pending"    # pedido enviado, esperando quem joga permitir
    ACCEPTED = "accepted"  # quem joga permitiu


class CareLink(Base):
    """Um familiar ou cuidador acompanhando o progresso de quem joga.

    O pedido é feito pelo e-mail de quem joga e só vale depois que essa pessoa
    permite. Ele é guardado pelo e-mail para não revelar se a conta existe: se
    ainda não existir, o pedido aparece quando a pessoa se cadastrar.
    """
    __tablename__ = "care_links"
    __table_args__ = (UniqueConstraint("caregiver_id", "elder_email", name="uq_care_link"),)

    id = Column(Integer, primary_key=True, index=True)
    caregiver_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    elder_email = Column(String(200), nullable=False, index=True)
    elder_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    status = Column(SAEnum(CareLinkStatus), nullable=False, default=CareLinkStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    accepted_at = Column(DateTime(timezone=True), nullable=True)

    caregiver = relationship("User", foreign_keys=[caregiver_id])
    elder = relationship("User", foreign_keys=[elder_id])
