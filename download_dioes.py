import requests


def baixa_dio():

    # Loop regressivo sobre índices dos arquivos PDF do DIO
    # O índice é crescente. Portanto, deve-se colocar um número maior que o índice da última edição do DIO
    for i in range(7270, 0, -1):

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
            with open(f'DIOES\{nome_arquivo}', 'wb') as file:
                file.write(response.content)

if __name__ == '__main__':

    baixa_dio()
