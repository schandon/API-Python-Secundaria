from sqlalchemy import Column, String, Integer, DateTime, Float
from datetime import datetime
from typing import Union
from models import Base


class Endereco(Base):
    __tablename__ = 'endereco'

    id = Column("pk_endereco", Integer, primary_key=True)
    cep = Column(String(8), nullable=False)
    endereco = Column(String(4000),nullable=True)
    bairro = Column(String(4000), nullable=True)
    localidade = Column(String(4000),nullable=True)
    uf = Column(String(2), nullable=True)
    data_insercao = Column(DateTime, default=datetime.now)
   
    def __init__(self, cep:str , endereco:str, bairro: str, localidade: str, uf:str,
        data_insercao:Union[DateTime, None] = None):
        
        self.cep = cep
        self.endereco = endereco
        self.bairro = bairro
        self.localidade = localidade
        self.uf = uf
        if data_insercao:
            self.data_insercao = data_insercao

    def to_dict(self):
        return {
            "cep": self.cep,
            "endereco": self.endereco,
            "bairro": self.bairro,
            "localidade": self.localidade,
            "uf": self.uf,
        }