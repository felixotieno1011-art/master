from sqlalchemy import create_engine, String, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    fullname: Mapped[str] = mapped_column(String)

engine = create_engine("sqlite:///drill.db")
Base.metadata.create_all(engine)
print("table created")

with Session(engine) as session:
    session.add(User(id=1, fullname="Felix"))
    session.commit()

    user = session.get(User, 1)
    print("found:", user.fullname)
