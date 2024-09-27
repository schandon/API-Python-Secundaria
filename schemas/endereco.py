from pydantic import BaseModel, ConfigDict 
from typing import Optional, List

class EnderecoSchema(BaseModel):
    cep: str = "21240050"
    endereco: Optional[str] = ""
    bairro: Optional[str] = ""
    localidade: Optional[str] = ""
    uf: Optional[str] = ""    
    
    model_config = ConfigDict(from_attributes=True) 
         
class EnderecoBuscaSchema(BaseModel):
  id: Optional[int] = 1 
  
class EnderecoCepSchema(BaseModel):
    cep: str = "21240050",
    endereco: Optional[str] = "",
    bairro: Optional[str] = "",
    uf: Optional[str] = "",
    estado: Optional[str] = ""   
    
  
class EnderecoViewSchema(BaseModel):
    id: int = 1
    
class EnderecoUpdateSchema(BaseModel):
    id: int = 1  
    cep: str = ""
    endereco: Optional[str] = ""
    bairro: Optional[str] = ""
    localidade: Optional[str] = ""
    uf: Optional[str] = "" 
    
class EnderecoDelSchema(BaseModel):
    id: int
    
def apresenta_endereco(endereco):
    return {
        "id": endereco.id,
        "cep": endereco.cep,
        "endereco": endereco.endereco,
        "bairro": endereco.bairro,
        "localidade": endereco.localidade,
        "uf": endereco.uf
    }
    
class EnderecoListaViewSchema(BaseModel):
    enderecos: List[EnderecoViewSchema]

def apresenta_lista_endereco(enderecos):
    result = []
    for endereco in enderecos:
        result.append(apresenta_endereco(endereco))
    return {"enderecos": result}