from datetime import datetime

from sqlalchemy import ForeignKey, Integer, String
from src.schemas.posts import PostSchema
from src.models import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    subject: Mapped[str | None] = mapped_column(String(50), nullable=True)
    content: Mapped[str]
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete='CASCADE'))

    user = relationship("User", back_populates="posts")

    def to_read_model(self):
        return {
            "id": self.id,
            "subject": self.subject,
            "content": self.content,
            "user": self.user.to_read_model()
        }

