from sqlalchemy.exc import IntegrityError
from flask_openapi3 import Info, Tag
from flask_openapi3 import OpenAPI
from flask_cors import CORS
from flask import redirect, jsonify
from models.cliente import Cliente
from models import *
from schemas import *
from logger import logger
import requests

info = Info(title="Api Doces", version="1.0.0")
app = OpenAPI(__name__, info=info)
CORS(app)

# definindo tags
cliente_tag = Tag(name="Cliente", description="Adição, visualização e remoção de clientes da base")


@app.get('/')
def home():
    return redirect('/openapi')

def get_address_from_cep(cep):
    response = requests.get(f'https://viacep.com.br/ws/{cep}/json/')
    if response.status_code == 200:
        data = response.json()
        if "erro" not in data:
            return {
                "endereco": data.get("logradouro"),
                "bairro": data.get("bairro"),
                "localidade": data.get("localidade"),
                "uf": data.get("uf")
            }
    return None

@app.post('/cliente', tags=[cliente_tag],
          responses={"200": ClienteViewSchema, "409": ErrorSchema, "400": ErrorSchema})
def add_cliente(form: ClienteSchema):
    """Adiciona um novo cliente à base de dados

    Retorna uma representação dos clientes
    """
    
    address_info = get_address_from_cep(form.cep)
    if not address_info:
        return {"message": "CEP inválido ou não encontrado"}, 400
    
    
    session = Session()
    cliente = Cliente(
        cep=form.cep,
        endereco= address_info['endereco'],
        bairro= address_info['bairro'],
        localidade= address_info['localidade'],
        uf= address_info['uf'], 
        
        )
    logger.debug(f"Adicionando ID do Cliente: '{cliente.id}'")
    try:
        # adicionando cliente
        session.add(cliente)
        # efetivando o camando de adição de novo item na tabela
        session.commit()
        logger.debug(f"Adicionado ID do Cliente: '{cliente.id}'")
        return apresenta_cliente(cliente), 200
    except IntegrityError as e:
        error_msg = "cliente de mesmo nome já salvo na base :/"
        logger.warning(f"Erro ao adicionar cliente '{cliente.id}', {error_msg}")
        return {"mesage": error_msg}, 409
    except Exception as e:
        error_msg = "Não foi possível salvar novo item :/"
        logger.warning(f"Erro ao adicionar cliente '{cliente.id}', {error_msg}")
        return {"mesage": error_msg}, 400

@app.get('/cliente', tags=[cliente_tag],
         responses={"200": ClienteViewSchema, "404": ErrorSchema})
def get_cliente(query: ClienteBuscaSchema):
    """Faz a busca por um cliente a partir do id do cliente

    Retorna uma representação dos clientes e comentários associados.
    """
    cliente_id = query.id
    logger.debug(f"Coletando dados sobre cliente #{cliente_id}")
    session = Session()
    cliente = session.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        error_msg = "cliente não encontrado na base :/"
        logger.warning(f"Erro ao buscar cliente '{cliente_id}', {error_msg}")
        return {"mesage": error_msg}, 400
    else:
        logger.debug(f"cliente econtrado: '{cliente.id}'")
        return apresenta_cliente(cliente), 200

@app.get('/clientes', tags=[cliente_tag],
         responses={"200": ClienteListaViewSchema, "404": ErrorSchema})
def get_clientes():
    """Lista todos os clientes cadastrados na base

    Retorna uma lista de representações de clientes.
    """
    logger.debug(f"Coletando lista de clientes")
    session = Session()
    clientes = session.query(Cliente).all()
    print(clientes)
    if not clientes:
        error_msg = "cliente não encontrado na base :/"
        logger.warning(f"Erro ao buscar por lista de clientes. {error_msg}")
        return {"mesage": error_msg}, 400
    else:
        logger.debug(f"Retornando lista de clientes")
        return apresenta_lista_cliente(clientes), 200
   
@app.delete('/cliente', tags=[cliente_tag],
            responses={"200": ClienteDelSchema, "404": ErrorSchema})
def del_cliente(query: ClienteBuscaSchema):
    """Deleta um cliente a partir do id informado

    Retorna uma mensagem de confirmação da remoção.
    """
    cliente_id = query.id

    logger.debug(f"Deletando dados sobre cliente #{cliente_id}")
    session = Session()

    if cliente_id:
        count = session.query(Cliente).filter(Cliente.id == cliente_id).delete()

    session.commit()
    if count:
        logger.debug(f"Deletado cliente #{cliente_id}")
        return {"mesage": "cliente removido", "id": cliente_id}
    else: 
        error_msg = "cliente não encontrado na base :/"
        logger.warning(f"Erro ao deletar cliente #'{cliente_id}', {error_msg}")
        return {"mesage": error_msg}, 400
    
@app.put('/cliente', tags=[cliente_tag],
         responses={"200": ClienteViewSchema, "404": ErrorSchema})
def update_cliente(form: ClienteUpdateSchema):
    """Atualiza um cliente a partir do ID informado.

    Retorna uma mensagem de confirmação da atualização.
    """
    cliente_id = form.id

    logger.debug(f"Atualizando dados do cliente #{cliente_id}")
    session = Session()

    try:
        # Buscar o cliente existente
        cliente = session.query(Cliente).filter(Cliente.id == cliente_id).first()

        if not cliente:
            error_msg = f"Cliente com ID {cliente_id} não encontrado."
            logger.warning(f"Erro ao atualizar cliente #{cliente_id}, {error_msg}")
            return {"message": error_msg}, 404

        # Se o CEP foi alterado, atualizar o endereço
        if form.cep and form.cep != cliente.cep:
            address_info = get_address_from_cep(form.cep)
            if not address_info:
                return {"message": "CEP inválido ou não encontrado"}, 400

            # Atualizar as informações de endereço
            cliente.cep = form.cep
            cliente.endereco = address_info['endereco']
            cliente.bairro = address_info['bairro']
            cliente.localidade = address_info['localidade']
            cliente.uf = address_info['uf']

        # Commit da transação
        session.commit()

        logger.debug(f"Cliente #{cliente_id} atualizado com sucesso.")
        return {"message": "Cliente atualizado", "id": cliente_id}, 200

    except Exception as e:
        session.rollback()
        error_msg = f"Erro ao atualizar cliente: {str(e)}"
        logger.error(error_msg)
        return {"message": error_msg}, 500

    finally:
        session.close()
