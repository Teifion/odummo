from sqlalchemy import (
    Column,
    Boolean,
    Integer,
    String,
    ForeignKey,
    DateTime,
)

# You will need to point this to wherever your declarative base is
from ...models import Base

class OdummoProfile(Base):
    __tablename__    = 'odummo_profiles'
    user             = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, primary_key=True)
    
    preferred_colour = Column(Boolean, default=False)
    
    matchmaking      = Column(Boolean, nullable=False, default=False)
    last_move        = Column(DateTime, default=False)
    
    wins             = Column(Integer, default=0, nullable=False)
    losses           = Column(Integer, default=0, nullable=False)

class OdummoGame(Base):
    __tablename__ = 'odummo_games'
    id            = Column(Integer, primary_key=True)
    turn          = Column(Integer)
    
    started       = Column(DateTime, nullable=False)
    
    player1       = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    player2       = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    winner        = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    current_state = Column(String, nullable=False, default=' '*64)
    
    rematch = Column(Integer, ForeignKey("odummo_games.id"))
    source  = Column(Integer, ForeignKey("odummo_games.id"))

class OdummoMove(Base):
    __tablename__ = 'odummo_moves'
    id            = Column(Integer, primary_key=True)
    
    game          = Column(Integer, ForeignKey("odummo_games.id"), nullable=False)
    player        = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    move          = Column(Integer, nullable=False)
    timestamp     = Column(DateTime, nullable=False)
