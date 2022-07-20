import requests
import os
import shutil
from datetime import date
from playwright.sync_api import sync_playwright
from glob import glob


# Armazena pasta onde os arquivos serão salvos
diretorio = None


def cria_pasta():

    """
    Cria pasta 'DIOES' no diretório corrente onde está localizado este arquivo Python.
    Todos os arquivos PDF baixados são salvos nesta pasta DIOES com os respectivos nomes originais.
    """

    global diretorio

    # Extrai diretório corrente do arquivo .PY
    cwd = os.getcwd()

    # Cria pasta no diretório corrente para armazenar arquivos PDF dos diários oficiais, caso não exista
    try:
        os.mkdir(f'{cwd}\DIOES')
    except FileExistsError:
        pass

    diretorio = f'{cwd}\DIOES'


def baixa_todas_edicoes_dio_es(num_inicial=10000):

    """
    Baixa arquivos PDF de todos os diários oficiais disponibilizados no site do DIO-ES.
    Parâmetro 'num_inicial': número inicial que serve de índice para a edição mais recente dos diários oficiais.
    Ex.: 'https://ioes.dio.es.gov.br/portal/edicoes/download/7247' (num_inicial = 7247)
    Deve-se fornecer um número superior ao índice da última edição disponível do diário.
    Para se ter uma ideia do índice da edição mais recente do diário, deve-se verificar o link da imagem da capa da última edição.
    A função realiza um loop regressivo a partir do num_inicial até chegar ao número 1.
    Atualmente (20/07/2022), o DIOES disponibliza os seguintes diários oficiais:
    1) Diário Oficial dos Poderes do Estado (diario_oficial)
    2) Diário Oficial dos Municípios (carderno dos municípios)
    3) Diário Oficial dos Municípios (dom_amunes)
    4) Diário Oficial do Município da Serra (serra)
    O Diário Oficial dos Municípios (caderno dos município), foi descontinuado a partir de 06/04/2022.
    O Diário Oficial dos Poderes do Estado (diário oficial) contém o Diário Oficial do Município da Serra.
    O aplicativo baixa todas as edições publicadas desses 4 diários oficiais.
    Cada edição possui uma numeração própria de edições, mas uma sequência única de índices para download.
    """

    # Calcula número inicial do índice de edições para uso no loop regressivo
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, slow_mo=0, timeout=0)
        page = browser.new_page()
        page.goto("https://ioes.dio.es.gov.br/portal/visualizacoes/diario_oficial")
        #page.wait_for_selector('#imagemCapa')
        #temp = page.query_selector('#imagemCapa')
        page.wait_for_timeout(3000)
        temp = page.locator('#imagemCapa')
        temp = temp.get_attribute('src')
        print(temp)
        
        # +15 -> edições acima da edição atual, por segurança, já que vários o DIO hospeda mais de um diario com a mesa sequência de índice
        num_inicial = int(temp.split(r'/')[-3]) + 30
        #print(num_inicial)

    # Loop regressivo sobre índices dos arquivos PDF do DIO
    # O índice no site é crescente. Portanto, deve-se colocar um número maior que o índice da última edição do DIO
    # O n evita que edições com mesmo nome/data (suplemento/extraordinária) sejam sobrepostos
    for n, i in enumerate(range(num_inicial, 0, -1)):

        # Cria resposta para os arquivos PDF
        response = requests.get(f'https://ioes.dio.es.gov.br/portal/edicoes/download/{i}')

        # Verifica se a edição existe no site. Se não estiver, continua o loop.
        if response.status_code != 200 or response.headers.get("Content-Disposition") == None:
            print(i)
            continue

        else:
            # Extrai nome do arquivo PDF
            nome_arquivo = response.headers.get("Content-Disposition").split("filename=")[1].replace('"', '').replace('-', '_')
            
            # Verifica se o arquivo já foi baixado e, em caso positivo, reinicia o loop
            if os.path.exists(f'{diretorio}\dio_es.csv'):
                with open(f'{diretorio}\dio_es.csv', 'r') as f:
                    pdf = [x.replace('\n', '') for x in f.readlines()]
                    if nome_arquivo in pdf:
                        print(i, nome_arquivo, 'BAIXADO')
                        continue

            print(i, nome_arquivo)

            # Salva arquivo PDF
            with open(f'{diretorio}\{n}_{nome_arquivo}', 'wb') as f:
                f.write(response.content)

            # Cria / atualiza arquivo CSV que armazenar lista de arquivos baixados
            with open(f'{diretorio}\dio_es.csv', 'a') as f:
                f.write(nome_arquivo + '\n')
            

            # EXTRAÇÃO DE IMAGENS

            # Cria resposta para os imagens JPG das capas dos arquivos PDF
            #response_capa = requests.get(f'https://ioes.dio.es.gov.br/apifront/portal/edicoes/imagem_diario/{i}/1/imagem')
            
            # Gera nome para a imagem da capa do arquivo PDF (arquivo JPG)
            #nome_arquivo_capa = response.headers.get("Content-Disposition").split("filename=")[1].replace('"', '').replace('.pdf', '')
            
            # Salva imagem da capa do arquivo PDF (arquivo JPG)
            #with open(f'{diretorio}\{nome_arquivo_capa}_capa.jpg', 'wb') as file:
            #    file.write(response_capa.content)

    


def baixa_todas_edicoes_dio_vitoria():

    """
    Baixa arquivos PDF de todos os diários oficiais do Município de Vitória/ES.
    A função realiza um loop regressivo a partir do ano atual até o ano 2014, quando começaram as publicações.
    Primeiro a função gera uma lista de links contendo as URLs de todos os arquivos PDF com o módulo Playwright.
    Depois baixa cada arquivo PDF da lista com o módulo Requests.
    """

    ################################ EXTRAI LINKS ################################

    # Cria lista para armazenar links (URL) dos arquivos PDF
    lista_links = []

    # Variável de controle para baixar apenas a última edição
    apenas_ultima_edicao=False

    with sync_playwright() as p:

        # Instancia navegador Chromium. timeout=0 (desabilita tempo máximo de espera que retorna erro)
        browser = p.chromium.launch(headless=True, slow_mo=0, timeout=0)

        # Cria página do navegador
        page = browser.new_page()

        # Abre página de pesquisa do Diário Oficial do Município de Vitória
        page.goto("https://diariooficial.vitoria.es.gov.br/")

        # Extrai ano atual
        ano_atual = date.today().year

        # Loop regressivo sobre os anos
        # Primeiro ano de disponibilização do diário: 2014
        for ano in range(ano_atual, 2013, -1):

            print(ano)

            # Captura seletor de ano e seleciona o ano
            page.wait_for_selector('#ctl00_conteudo_ucPesquisarDiarioOficial_ddlAno')
            seletor_ano = page.locator('#ctl00_conteudo_ucPesquisarDiarioOficial_ddlAno')
            seletor_ano.select_option(label=str(ano))

            # Captura seletor de mes
            # Os tempos de espera são usados para aguardar a disponibilidade do próximo elemento a ser acionado
            page.wait_for_selector('#ctl00_conteudo_ucPesquisarDiarioOficial_ddlMes')
            seletor_mes = page.locator('#ctl00_conteudo_ucPesquisarDiarioOficial_ddlMes')
            page.wait_for_timeout(1000)

            # Extrai meses existentes no seletor de meses
            select = page.query_selector('#ctl00_conteudo_ucPesquisarDiarioOficial_ddlMes')
            meses = select.query_selector_all('option')
            meses = [x.inner_text() for x in meses[1:]]
            print(meses)

            # Loop sobre meses
            for mes in meses:
                
                # Seleciona mes
                seletor_mes.select_option(label=mes)
                page.wait_for_timeout(1000)

                # Captura elemento (unordered list) do paginador
                ul = page.locator('#ctl00_UpdatePanelMaster > div:nth-child(3) > div > div > div.col-md-7 > div:nth-child(4) > div > div.table-responsive > nav > ul')
                
                # Extrai número de páginas do paginador
                c = ul.locator('li').count() - 1 # O -1 é para subtrair a página que começa selecionada (página 1)

                # Captura lista de links dos arquivos PDF da primeira página (já começa selecionada) e adiciona à 'lista_links'
                page.wait_for_selector('#ctl00_conteudo_ucPesquisarDiarioOficial_grdArquivos > tbody')
                tbody = page.query_selector('#ctl00_conteudo_ucPesquisarDiarioOficial_grdArquivos > tbody')
                a = tbody.query_selector_all('a')
                a = ['https://diariooficial.vitoria.es.gov.br/' + x.get_attribute('href') for x in a]
                lista_links += a

                # Interrompe execução do loop meses
                if apenas_ultima_edicao == True:
                    break

                # Loop sobre número de páginas
                for k in range(c):

                    # Extrai elemento de cada página e clica sobre ele
                    li = page.locator(f'#ctl00_UpdatePanelMaster > div:nth-child(3) > div > div > div.col-md-7 > div:nth-child(4) > div > div.table-responsive > nav > ul > li:nth-child({k + 2}) > a')
                    page.wait_for_timeout(1000)
                    li.click()
                    page.wait_for_timeout(1000)

                    # Captura lista de links dos arquivos PDF e adiciona à 'lista_links'
                    page.wait_for_selector('#ctl00_conteudo_ucPesquisarDiarioOficial_grdArquivos > tbody')
                    tbody = page.query_selector('#ctl00_conteudo_ucPesquisarDiarioOficial_grdArquivos > tbody')
                    a = tbody.query_selector_all('a')
                    a = ['https://diariooficial.vitoria.es.gov.br/' + x.get_attribute('href') for x in a]
                    lista_links += a

                # Retorna seleção do paginador para a página 1 antes de mudar para o próximo mês
                li = page.locator('#ctl00_UpdatePanelMaster > div:nth-child(3) > div > div > div.col-md-7 > div:nth-child(4) > div > div.table-responsive > nav > ul > li:nth-child(1) > a')
                page.wait_for_timeout(1000)
                try:
                    li.click()
                except:
                    pass
                page.wait_for_timeout(1000)

            # Interrompe execução do loop anos
            if apenas_ultima_edicao == True:
                break

        print(len(lista_links))

    ############################### BAIXA ARQUIVOS ###############################
    
    # Baixar arquivos PDF
    # Loop sobre lista de links dos arquivos PDF
    # O n evita que edições com mesmo nome/data (suplemento/extraordinária) sejam sobrepostos
    for n, i in enumerate(lista_links): 

        # Cria resposta para o arquivo PDF
        response = requests.get(i)
        
        # Extrai nome do arquivo PDF
        nome_arquivo = response.headers.get("Content-Disposition").split("filename=")[1].replace('"', '').replace('/', '_')
        print(nome_arquivo)
    
        # Salva arquivo PDF
        with open(f'{diretorio}\{n}_{nome_arquivo}', 'wb') as file:
            file.write(response.content)

        if apenas_ultima_edicao == True:
            break

    
def baixa_todas_edicoes_dio_vila_velha():

    with sync_playwright() as p:

        # Extrai data atual
        temp = date.today()
        data_atual = str(temp.strftime('%d')) + '/' + str(temp.strftime('%m')) + '/' + str(temp.year)

        # Instancia Chromium no modo headless
        browser = p.chromium.launch(headless=True, slow_mo=0, timeout=0)
        
        # Abre janela do navegador
        page = browser.new_page()

        # Acessa endereço do Diário Oficial de Vila Velha
        url = 'https://diariooficial.vilavelha.es.gov.br'
        page.goto(url)

        # Seleciona campo Data Inicial e insere data inicial da pesquisa
        page.wait_for_selector('#ctl00_cpConteudo_txtDataInicial') # Espera elemento ficar visível
        data_inicial = page.query_selector('#ctl00_cpConteudo_txtDataInicial') # Captura elemento
        data_inicial.type('06/04/2022') # Digita data
    
        # Seleciona campo Data Final e insere data final da pesquisa: data atual
        page.wait_for_selector('#ctl00_cpConteudo_txtDataFinal')
        data_final = page.query_selector('#ctl00_cpConteudo_txtDataFinal')
        data_final.type(data_atual)

        # Seleciona e clica no botão OK
        page.wait_for_selector('#ctl00_cpConteudo_btnPesquisarArquivos')
        data_final = page.query_selector('#ctl00_cpConteudo_btnPesquisarArquivos')
        data_final.click()

        # Seleciona elementos de paginação. Retorna lista
        # Os elementos só aparecem se a pesquisa retornar mais de 6 arquivos
        page.wait_for_timeout(3000) # Aguarda carregamento dos elementos
        paginador = page.query_selector_all('#ctl00_cpConteudo_gvDocumentos > tbody > tr.pagination-ys > td > table > tbody > tr > td')
        print(paginador)

        print()
        print(f'extrai dados da página 1')

        # Realiza download dos arquivos PDF, conforme detalhado acima
        # Retorna lista de 'td' da tabela que contém os elementos para baixar os arquivos PDF
        # Cada 'tr' da tabela possui apenas um 'td'
        links = page.query_selector_all('#ctl00_cpConteudo_gvDocumentos > tbody > tr > td')
        
        # Loop sobre os elementos 'td'
        for j in links:

            # Verifica se o elemento 'td' não começa com dígito (exclui o 'td' dos botões de paginação)
            if not j.query_selector('span').text_content().isdigit():

                with page.expect_download() as download_info:

                    # Seleciona e clica sobre a imagem do arquivo PDF
                    j.query_selector('img[title="Baixar no formato PDF"]').click()

                    # Extrai o nome do arquivo contido no elemento 'span'
                    file_name = j.query_selector('span').text_content()
                
                # Aguarda download e cria variável de acesso ao arquivo baixado
                download = download_info.value
                
                # Extrai endereço do arquivo baixado
                path = download.path()
                print(file_name)

                # Copia arquivo baixado para a pasta DIOES
                shutil.copy(path, f'{diretorio}\{file_name}.pdf')

        # Verifica se existe botões de paginação. Se não houver, termina o script
        if paginador == []:
            return

        # Se houver botões de paginação, inicia loop sobre número dos botões
        for i in range(2, 10000):

            print()

            # Captura texto do último botão do paginador
            num_paginas = page.locator('#ctl00_cpConteudo_gvDocumentos > tbody > tr.pagination-ys > td > table > tbody > tr')
            num_paginas = num_paginas.locator('td').last.text_content()
            print(num_paginas)
            
            # Verifica se o valor de 'i' é maior do que o valor do texto último botão do paginador, indicando não haver mais botões
            # O texto do último botão nem sempre é um dígito
            try:
                num_paginas = int(num_paginas)
                if i > num_paginas:
                    return
            except:
                pass
        
            # Clica sobre o botão que possui como texto o número 'i'
            page.click(f"text='{i}'")
            
            # Realiza download dos arquivos PDF, conforme detalhado acima
            print(f'extrai dados da página {i}')
            page.wait_for_selector('#ctl00_cpConteudo_gvDocumentos > tbody > tr > td')
            links = page.query_selector_all('#ctl00_cpConteudo_gvDocumentos > tbody > tr > td') # Aponta para um localizador lista
            for j in links:
                if not j.query_selector('span').text_content().isdigit():
                    with page.expect_download() as download_info:
                        j.query_selector('img[title="Baixar no formato PDF"]').click()
                        file_name = j.query_selector('span').text_content()
                    download = download_info.value
                    path = download.path()
                    print(file_name)
                    shutil.copy(path, f'{diretorio}\{file_name}.pdf')
                    
            if i % 10 == 0:
                try:
                    td = page.locator(f"text='...'").last
                    td.click()
                except:
                    pass


if __name__ == '__main__':

    cria_pasta()
    baixa_todas_edicoes_dio_es()
    #baixa_todas_edicoes_dio_vitoria()
    #baixa_todas_edicoes_dio_vila_velha()
