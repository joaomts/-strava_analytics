## Bibliotecas necessárias
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


# --- Configuração Inicial do Driver (Seu código está bom aqui) ---
def setup_driver():
    """Configura e retorna uma instância do WebDriver."""
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # Dica: Adicione para rodar sem abrir a janela do navegador
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(
        5
    )  # Espera implícita: uma pequena espera padrão para qualquer find_element
    return driver


# --- Funções de Coleta de Dados Refatoradas ---


def pega_tabela_atleta(driver, wait):
    """
    Tenta pegar a tabela de 'Voltas' (laps). Se não existir,
    pega a tabela principal da página da atividade.
    Usa esperas explícitas para garantir que a tabela carregou.
    """
    try:
        # Tenta clicar na aba "Voltas" se ela existir
        laps_button = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'li[data-tracking-element="laps"] a')
            )
        )
        laps_button.click()

        # Espera a tabela de voltas carregar e a extrai
        table_element = wait.until(
            EC.visibility_of_element_located((By.ID, "efforts-table"))
        )

    except TimeoutException:
        # Se a aba "Voltas" não for encontrada ou não carregar a tempo, pega a tabela inicial
        print("  -> Aba 'Voltas' não encontrada. Buscando tabela principal.")
        try:
            table_element = wait.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "table.table.dense"))
            )
        except TimeoutException:
            print("  -> [AVISO] Nenhuma tabela de dados encontrada para este atleta.")
            return None

    # Extração dos dados da tabela encontrada
    headers = [th.text for th in table_element.find_elements(By.TAG_NAME, "th")]
    data = []
    rows = table_element.find_elements(
        By.XPATH, ".//tbody/tr"
    )  # .// para buscar dentro do elemento
    for row in rows:
        cols = [td.text for td in row.find_elements(By.TAG_NAME, "td")]
        if cols:  # Garante que não adiciona linhas vazias
            data.append(cols)

    if not data:
        return None

    return pd.DataFrame(data, columns=headers)


def pega_dados_atletas_principal(driver, url_base_prova: str):
    """
    Percorre a lista de atletas de forma robusta, coletando os dados de cada um.
    """
    print("--- Iniciando coleta de dados de performance dos atletas ---")
    driver.get(url_base_prova)
    wait = WebDriverWait(driver, 20)  # Aumentar o tempo de espera para 20 segundos

    dados_coletados = []
    pagina_atual = 1

    while True:  # Loop infinito que será quebrado quando não houver mais páginas
        url_pagina = f"{url_base_prova}?page={pagina_atual}"
        if pagina_atual > 1:
            print(f"Acessando a página {pagina_atual}: {url_pagina}")
            driver.get(url_pagina)

        try:
            # Espera a tabela de resultados da página carregar
            wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "#results table tbody tr")
                )
            )
        except TimeoutException:
            print(
                f"Aviso: A página {pagina_atual} não carregou a tabela de resultados a tempo ou não existe. Fim da coleta."
            )
            break

        # Coletar todos os links e nomes de atletas ANTES de sair da página
        athlete_links = []
        athlete_names = []
        try:
            # Seletores mais robustos para encontrar os links dos atletas
            athlete_elements = driver.find_elements(
                By.XPATH, '//*[@id="results"]/table/tbody/tr/td[2]/a'
            )

            for elem in athlete_elements:
                athlete_links.append(elem.get_attribute("href"))
                athlete_names.append(elem.text)

        except Exception as e:
            print(f"Erro ao coletar links na página {pagina_atual}: {e}")
            break

        if not athlete_links:
            print("Nenhum atleta encontrado na página. Finalizando.")
            break

        print(f"Encontrados {len(athlete_links)} atletas na página {pagina_atual}.")

        # Loop para visitar cada LINK de atleta coletado
        for i, link in enumerate(athlete_links):
            nome_atleta = athlete_names[i]
            print(f"  -> Coletando dados de: {nome_atleta}")

            try:
                driver.get(link)
                df_atleta = pega_tabela_atleta(driver, wait)

                if df_atleta is not None and not df_atleta.empty:
                    df_atleta.insert(0, "Nome Atleta", nome_atleta)
                    dados_coletados.append(df_atleta)
                else:
                    print(
                        f"  -> [AVISO] Nenhuma tabela válida coletada para {nome_atleta}"
                    )

            except Exception as e:
                print(
                    f"  -> [ERRO] Falha ao processar o atleta {nome_atleta}. Erro: {e}"
                )
                continue  # Pula para o próximo atleta em caso de erro

        pagina_atual += 1

    if not dados_coletados:
        print("\nNenhum dado principal foi coletado.")
        return None

    df_final = pd.concat(dados_coletados, ignore_index=True)
    print("\n--- Coleta de dados de performance concluída ---")
    return df_final


def coletar_dados_de_filtro(
    driver,
    url_base_prova: str,
    nome_coluna: str,
    botao_filtro_xpath: str,
    lista_opcoes_xpath: str,
):
    """
    Função genérica para coletar nomes de atletas baseados em um filtro (sexo, idade, etc.).
    """
    print(f"\n--- Coletando filtro: {nome_coluna} ---")
    driver.get(url_base_prova)
    wait = WebDriverWait(driver, 15)

    dados_filtro = []

    try:
        # Clica para abrir o menu de filtros
        wait.until(EC.element_to_be_clickable((By.XPATH, botao_filtro_xpath))).click()

        # Pega todos os links das opções de filtro de uma vez para evitar StaleElement
        opcoes = wait.until(
            EC.visibility_of_element_located((By.XPATH, lista_opcoes_xpath))
        ).find_elements(By.TAG_NAME, "a")
        links_e_textos = [
            (opt.get_attribute("href"), opt.text)
            for opt in opcoes
            if opt.text and opt.get_attribute("href")
        ]
    except TimeoutException:
        print(f"Não foi possível encontrar o filtro '{nome_coluna}'. Pulando.")
        return pd.DataFrame(columns=[nome_coluna, "nome_atleta"])

    # Itera sobre os links coletados (mais estável)
    for link, texto_filtro in links_e_textos:
        print(f"Processando filtro '{texto_filtro}'...")
        driver.get(link)

        pagina_filtro = 1
        while True:
            url_pagina_filtro = f"{link}&page={pagina_filtro}"
            if pagina_filtro > 1:
                driver.get(url_pagina_filtro)

            try:
                wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "#results table tbody tr")
                    )
                )
            except TimeoutException:
                break  # Sai do loop se não encontrar tabela (fim das páginas)

            nomes_na_pagina = [
                elem.text
                for elem in driver.find_elements(
                    By.XPATH, '//*[@id="results"]/table/tbody/tr/td[2]/a'
                )
            ]
            if not nomes_na_pagina:
                break  # Sai se não houver mais nomes

            for nome in nomes_na_pagina:
                dados_filtro.append({nome_coluna: texto_filtro, "nome_atleta": nome})

            pagina_filtro += 1

    return pd.DataFrame(dados_filtro)


def gerar_dataframe_final_completo(url_base_prova: str, nome_arquivo: str):
    """
    Orquestra toda a coleta de dados e os une.
    """
    driver = setup_driver()

    try:
        # PASSO 1: Coletar dados principais de tempo e performance
        df_principal = pega_dados_atletas_principal(driver, url_base_prova)
        if df_principal is None or df_principal.empty:
            print("Coleta principal falhou. Abortando.")
            return

        # PASSO 2: Coletar dados dos filtros (usando a função genérica)
        # NOTA: Os XPaths exatos podem precisar de ajuste se o site mudar.
        df_sexo = coletar_dados_de_filtro(
            driver,
            url_base_prova,
            "sexo",
            '//*[@id="segment-leaderboard-filter-gender"]/button',
            '//*[@id="segment-leaderboard-filter-gender"]/ul',
        )

        df_idade = coletar_dados_de_filtro(
            driver,
            url_base_prova,
            "faixa_etaria",
            '//*[@id="segment-leaderboard-filter-age_group"]/button',
            '//*[@id="segment-leaderboard-filter-age_group"]/ul',
        )

        df_peso = coletar_dados_de_filtro(
            driver,
            url_base_prova,
            "peso",
            '//*[@id="segment-leaderboard-filter-weight_class"]/button',
            '//*[@id="segment-leaderboard-filter-weight_class"]/ul',
        )

        # PASSO 3: Unir os DataFrames
        print("\n--- Unindo todos os dados coletados ---")
        df_final = pd.merge(
            df_principal,
            df_sexo,
            how="left",
            left_on="Nome Atleta",
            right_on="nome_atleta",
        )
        df_final = pd.merge(
            df_final,
            df_idade,
            how="left",
            left_on="Nome Atleta",
            right_on="nome_atleta",
        )
        df_final = pd.merge(
            df_final, df_peso, how="left", left_on="Nome Atleta", right_on="nome_atleta"
        )

        # Limpeza de colunas duplicadas do merge
        df_final = df_final.loc[:, ~df_final.columns.str.contains("^nome_atleta")]

        # PASSO 4: Salvar o resultado
        df_final.to_csv(nome_arquivo, index=False, encoding="utf-8-sig")
        print(f"\nPROCESSO CONCLUÍDO! DataFrame final salvo em '{nome_arquivo}'")

        return df_final

    finally:
        print("Fechando o navegador.")
        driver.quit()


# --- Exemplo de como chamar ---
if __name__ == "__main__":
    # Use o link do segmento que inclui "/leaderboard" no final para cair na página certa
    url_da_prova = "https://www.strava.com/segments/35231066/leaderboard"

    df_completo = gerar_dataframe_final_completo(
        url_base_prova=url_da_prova, nome_arquivo="dados_teste_gemini.csv"
    )

    if df_completo is not None:
        print("\nAmostra do DataFrame final:")
        print(df_completo.head().to_string())
