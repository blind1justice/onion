from datetime import datetime
from src.models import Base
from src.schemas.users import UserSchema

from sqlalchemy.orm import Mapped, mapped_column, relationship


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str | None] = mapped_column(unique=True)
    phone: Mapped[str | None] = mapped_column(unique=True)
    hashed_password: Mapped[str]

    email_confirmation_token: Mapped[str | None] = mapped_column(nullable=True)
    email_confirmation_sent_at: Mapped[datetime | None] = mapped_column(nullable=True)
    email_confirmed_at: Mapped[datetime | None] = mapped_column(nullable=True)

    phone_confirmation_code: Mapped[str | None] = mapped_column(nullable=True)
    phone_confirmation_sent_at: Mapped[datetime | None] = mapped_column(nullable=True)
    phone_confirmed_at: Mapped[datetime | None] = mapped_column(nullable=True)

    posts = relationship("Post", back_populates="user")

    @property
    def is_confirmed(self):
        return self.email_confirmed_at or self.phone_confirmed_at
    
    def to_read_model(self):
        return UserSchema(
            id=self.id,
            email=self.email,
            phone=self.phone,
            email_confirmed_at=self.email_confirmed_at,
            phone_confirmed_at=self.phone_confirmed_at
        )
