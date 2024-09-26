from pydantic import BaseModel, ConfigDict 
from typing import Optional, List

class ClienteSchema(BaseModel):
    cliente_id: int = 1
    cep: str = "21240050"
    endereco: Optional[str] = ""
    bairro: Optional[str] = ""
    localidade: Optional[str] = ""
    uf: Optional[str] = ""    
    
    model_config = ConfigDict(from_attributes=True) 
         
class ClienteBuscaSchema(BaseModel):
  id: Optional[int] = 1  
  
class ClienteViewSchema(BaseModel):
    id: int = 1
    
class ClienteUpdateSchema(BaseModel):
    id: int = 1  
    cep: str = ""
    endereco: Optional[str] = ""
    bairro: Optional[str] = ""
    localidade: Optional[str] = ""
    uf: Optional[str] = "" 
    
class ClienteDelSchema(BaseModel):
    id: int
    
def apresenta_cliente(cliente):
     
    return {
        "id": cliente.id,
        "cep": cliente.cep,
        "endereco": cliente.endereco,
        "bairro": cliente.bairro,
        "localidade": cliente.localidade,
        "uf": cliente.uf
    }
    
class ClienteListaViewSchema(BaseModel):
    clientes: List[ClienteViewSchema]

def apresenta_lista_cliente(clientes):
    result = []
    for cliente in clientes:
        result.append(apresenta_cliente(cliente))
    return {"clientes": result}