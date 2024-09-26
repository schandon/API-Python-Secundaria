# API-Python-Secundaria

Foco do Desenvolvimento desta API Secundaria é fazer a utilização do API Publica ViaCep, tendo sua documentação [Link Documentação API ViaCep](https://viacep.com.br/). Vamos fazer a conexão com o componemte principal que é [API-Doces-Simplificada](https://github.com/schandon/API-Doces-Simplificada)

### Deploy
 * Passo 1:
    - Vamos rodar o código do Docker Compose que foi configurado préviamente
```
  docker compose up -d
```
* Passo 2:
    - Verificar se a aplicação está rodando na porta 9000
```
  http://localhost:9000
```

### Desenvolvedor
  * Passo 1:
    - Vamos começar pela mode configuração do modo desenvolvedor da aplicação, estaremos preparando o ambientamente
```
  python -m venv env
```
 * Passo 2:
    * Entrar na modo virtualizado, executando o código
```
      env\Scripts\activate
```
* Passo 3:
    * Será necessário ter todas as libs python listadas no `requirements.txt` instaladas, é bem simples o processo. 
```
    pip install -r requirements.txt 
```
  * Passo 4:
    * Para executar a API  basta executar:
```
    flask run --host 0.0.0.0 --port 9000 --reload
```  

