from sqlalchemy.exc import IntegrityError
from flask_openapi3 import Info, Tag
from flask_openapi3 import OpenAPI
from flask_cors import CORS
from flask import redirect, jsonify
from models.endereco import Endereco
from models import *
from schemas import *
from logger import logger
import requests

info = Info(title="Api Doces", version="1.0.0")
app = OpenAPI(__name__, info=info)
CORS(app)

# definindo tags
endereco_tag = Tag(name="Endereço", description="Adição, visualização e remoção de Endereços da base")
consulta_cep = Tag(name="Consulta", description="Faz consulta a ViaCep")

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

@app.post('/endereco', tags=[endereco_tag],
          responses={"200": EnderecoViewSchema, "409": ErrorSchema, "400": ErrorSchema})
def add_endereco(form: EnderecoSchema):
    """Adiciona um novo endereco à base de dados

    Retorna uma representação dos enderecos
    """
    
    address_info = get_address_from_cep(form.cep)
    if not address_info:
        return {"message": "CEP inválido ou não encontrado"}, 400
    
    
    session = Session()
    endereco = Endereco(
        cep=form.cep,
        endereco= address_info['endereco'],
        bairro= address_info['bairro'],
        localidade= address_info['localidade'],
        uf= address_info['uf'], 
        
        )
    logger.debug(f"Adicionando ID do endereco: '{endereco.id}'")
    try:
        # adicionando endereco
        session.add(endereco)
        # efetivando o camando de adição de novo item na tabela
        session.commit()
        logger.debug(f"Adicionado ID do endereco: '{endereco.id}'")
        return apresenta_endereco(endereco), 200
    except IntegrityError as e:
        error_msg = "endereco de mesmo nome já salvo na base :/"
        logger.warning(f"Erro ao adicionar endereco '{endereco.id}', {error_msg}")
        return {"mesage": error_msg}, 409
    except Exception as e:
        error_msg = "Não foi possível salvar novo item :/"
        logger.warning(f"Erro ao adicionar endereco '{endereco.id}', {error_msg}")
        return {"mesage": error_msg}, 400

@app.get('/endereco', tags=[endereco_tag],
         responses={"200": EnderecoViewSchema, "404": ErrorSchema})
def get_endereco(query: EnderecoBuscaSchema):
    """Faz a busca por um endereco a partir do id do endereco

    Retorna uma representação dos enderecos e comentários associados.
    """
    endereco_id = query.id
    logger.debug(f"Coletando dados sobre endereco #{endereco_id}")
    session = Session()
    endereco = session.query(Endereco).filter(Endereco.id == endereco_id).first()
    if not endereco:
        error_msg = "endereco não encontrado na base :/"
        logger.warning(f"Erro ao buscar endereco '{endereco_id}', {error_msg}")
        return {"mesage": error_msg}, 400
    else:
        logger.debug(f"endereco econtrado: '{endereco.id}'")
        return jsonify(endereco.to_dict()), 200

@app.get('/enderecos', tags=[endereco_tag],
         responses={"200": EnderecoListaViewSchema, "404": ErrorSchema})
def get_enderecos():
    """Lista todos os enderecos cadastrados na base

    Retorna uma lista de representações de enderecos.
    """
    logger.debug(f"Coletando lista de enderecos")
    session = Session()
    enderecos = session.query(Endereco).all()
    print(enderecos)
    if not enderecos:
        error_msg = "endereco não encontrado na base :/"
        logger.warning(f"Erro ao buscar por lista de enderecos. {error_msg}")
        return {"mesage": error_msg}, 400
    else:
        logger.debug(f"Retornando lista de enderecos")
        return apresenta_lista_endereco(enderecos), 200
   
@app.delete('/endereco', tags=[endereco_tag],
            responses={"200": EnderecoDelSchema, "404": ErrorSchema})
def del_endereco(query: EnderecoBuscaSchema):
    """Deleta um endereco a partir do id informado

    Retorna uma mensagem de confirmação da remoção.
    """
    endereco_id = query.id

    logger.debug(f"Deletando dados sobre endereco #{endereco_id}")
    session = Session()

    if endereco_id:
        count = session.query(Endereco).filter(Endereco.id == endereco_id).delete()

    session.commit()
    if count:
        logger.debug(f"Deletado endereco #{endereco_id}")
        return {"mesage": "endereco removido", "id": endereco_id}
    else: 
        error_msg = "endereco não encontrado na base :/"
        logger.warning(f"Erro ao deletar endereco #'{endereco_id}', {error_msg}")
        return {"mesage": error_msg}, 400
    
@app.put('/endereco', tags=[endereco_tag],
         responses={"200": EnderecoViewSchema, "404": ErrorSchema})
def update_endereco(query: EnderecoUpdateSchema):
    """Atualiza um endereco a partir do ID informado.

    Retorna uma mensagem de confirmação da atualização.
    """
    endereco_id = query.id

    logger.debug(f"Atualizando dados do endereco #{endereco_id}")
    session = Session()
    endereco = None

    try:
        # Buscar o endereco existente
        endereco = session.query(Endereco).filter(Endereco.id == endereco_id).first()

        if not endereco:
            error_msg = f"endereco com ID {endereco_id} não encontrado."
            logger.warning(f"Erro ao atualizar endereco #{endereco_id}, {error_msg}")
            return {"message": error_msg}, 404

        # Se o CEP foi alterado, atualizar o endereço
        if query.cep and query.cep != endereco.cep:
            address_info = get_address_from_cep(query.cep)
            if not address_info:
                return {"message": "CEP inválido ou não encontrado"}, 400

            # Atualizar as informações de endereço
            endereco.cep = query.cep
            endereco.endereco = address_info['endereco']
            endereco.bairro = address_info['bairro']
            endereco.localidade = address_info['localidade']
            endereco.uf = address_info['uf']

        # Commit da transação
        session.commit()

        logger.debug(f"endereco #{endereco_id} atualizado com sucesso.")
        return {"message": "endereco atualizado", "id": endereco_id}, 200

    except Exception as e:
        session.rollback()
        error_msg = f"Erro ao atualizar endereco: {str(e)}"
        logger.error(error_msg)
        return {"message": error_msg}, 500

    finally:
        session.close()


@app.get('/cosulta-cep', tags=[consulta_cep],
         responses={"200": EnderecoViewSchema, "404": ErrorSchema})
def consulta_cep(query: EnderecoCepSchema):
    cep = query.get('cep')
    if not cep:
        return jsonify({"error": "CEP não informado"}), 400
    
    try:
        via_cep_url = f'https://viacep.com.br/ws/{cep}/json/'
        response = requests.get(via_cep_url)
        
        if response.status_code != 200:
            return jsonify({"error": f"CEP inválido, {response.status_code}"})
        
        return  response.json()
    
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500