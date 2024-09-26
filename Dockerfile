# Usar uma imagem base oficial do Python
FROM python:3.9

# Criar um diretório de trabalho no container
WORKDIR /app

# Copiar o arquivo requirements.txt para o diretório de trabalho
COPY requirements.txt ./

# Instalar as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todos os arquivos do diretório atual para o diretório de trabalho
COPY . . 

# Definir o comando para rodar a aplicação
CMD [ "flask", "run", "--host", "0.0.0.0", "--port", "9000", "--reload" ]
