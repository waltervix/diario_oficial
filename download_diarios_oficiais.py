import requests
import os


def baixa_dioes(num_inicial=10000):

    """
    Baixa arquivos PDF e imagens das capas de todos os diários oficiais disponibilizados no site do DIO-ES.
    Parâmetro 'num_inicial': número inicial que serve de índice para a edição mais recente dos diários oficiais.
    Ex.: 'https://ioes.dio.es.gov.br/portal/edicoes/download/7247' (num_inicial = 7247)
    Deve-se fornecer um número superior ao índice da última edição disponível do diário.
    Para ter uma ideia do índice da edicação mais recente do diário, deve-se verificar o link da imagem da capa da última edição.
    A função realiza um loop regressivo a partir do num_inicial até chegar ao número 1.
    É criada a pasta 'DIOES no diretório corrente onde está localizado este arquivo Python.
    Todos os arquivos PDF e JPG baixados são salvos nesta pasta DIOES com os respectivos nomes originais.
    Atualmente (16/07/2022), o DIOES disponibliza os seguintes diários oficiais:
    1) Diário Oficial dos Poderes do Estado (diario_oficial)
    2) Diário Oficial dos Municípios (dom_amunes)
    3) Diário Oficial do Município da Serra (serra)
    O aplicativo baixa esses três diários oficiais.
    """

    # Extrai diretório corrente do arquivo .PY
    cwd = os.getcwd()

    # Cria pasta no diretório corrente para armazenar arquivos PDF E JPG (capas) dos diários oficiais, caso não exista
    try:
        os.mkdir(f'{cwd}\DIOES')
    except FileExistsError:
        pass

    diretorio = f'{cwd}\DIOES'

    # Loop regressivo sobre índices dos arquivos PDF do DIO
    # O índice é crescente. Portanto, deve-se colocar um número maior que o índice da última edição do DIO
    for i in range(num_inicial, 0, -1):

        # Cria resposta para os arquivos PDF
        response = requests.get(f'https://ioes.dio.es.gov.br/portal/edicoes/download/{i}')

        # Verifica se a edição existe
        if response.status_code != 200 or response.headers.get("Content-Disposition") == None:
            print(i)
            continue

        else:
            # Extrai nome do arquivo PDF
            nome_arquivo = response.headers.get("Content-Disposition").split("filename=")[1].replace('"', '')
            print(i, nome_arquivo)

            # Salva arquivo PDF
            with open(f'{diretorio}\{nome_arquivo}', 'wb') as file:
                file.write(response.content)

            # Cria resposta para os imagens JPG das capas dos arquivos PDF
            response_capa = requests.get(f'https://ioes.dio.es.gov.br/apifront/portal/edicoes/imagem_diario/{i}/1/imagem')
            
            # Gera nome para a imagem da capa do arquivo PDF (arquivo JPG)
            nome_arquivo_capa = response.headers.get("Content-Disposition").split("filename=")[1].replace('"', '').replace('.pdf', '')
            
            # Salva imagem da capa do arquivo PDF (arquivo JPG)
            with open(f'{diretorio}\{nome_arquivo_capa}_capa.jpg', 'wb') as file:
                file.write(response_capa.content)
    
if __name__ == '__main__':

    baixa_dioes(7270)
