from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
import pyautogui
import time
import os
import subprocess
import pandas as pd


def extrair_tabela(driver, df):
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.ID, "projetos")))

    linhas = driver.find_elements(By.CSS_SELECTOR, "#projetos tr.jqgrow")

    for linha in linhas:
        try:
            edital = linha.find_element(By.CSS_SELECTOR, "td[aria-describedby='projetos_anoofebnf']").get_attribute("title")
            unidade = linha.find_element(By.CSS_SELECTOR, "td[aria-describedby='projetos_nomabvclg']").get_attribute("title")
            titulo = linha.find_element(By.CSS_SELECTOR, "td[aria-describedby='projetos_titprjbnf']").get_attribute("title")
            vertente = linha.find_element(By.CSS_SELECTOR, "td[aria-describedby='projetos_stavteprj']").get_attribute("title")
            orientador = linha.find_element(By.CSS_SELECTOR, "td[aria-describedby='projetos_nompescdn']").get_attribute("title")
            total_bolsa = linha.find_element(By.CSS_SELECTOR, "td[aria-describedby='projetos_numbolapr']").get_attribute("title")

            df.loc[len(df)] = [edital, unidade, titulo, vertente, orientador, total_bolsa]

        except Exception as e:
            print("⚠️ Erro ao processar linha:", e)

    return df

def setup_driver():
    options = Options()
    options.add_argument("--start-maximized")
    prefs = {
        "download.default_directory": os.path.join(os.path.expanduser("~"), "Downloads"),
        "download.prompt_for_download": False,
        "plugins.always_open_pdf_externally": True,
        "plugins.plugins_disabled": ["Chrome PDF Viewer"]
    }
    options.add_experimental_option("prefs", prefs)
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def main():
    driver = setup_driver()
    wait = WebDriverWait(driver, 30)

    try:
        # Login
        driver.get("https://uspdigital.usp.br/jupiterweb/webLogin.jsp")
        usuario = wait.until(EC.presence_of_element_located((By.NAME, "codpes")))
        usuario.send_keys("")
        senha = driver.find_element(By.NAME, "senusu")
        senha.send_keys("")
        driver.find_element(By.NAME, "Submit").click()

        wait.until(EC.url_contains("https://uspdigital.usp.br/jupiterweb/autenticar"))
        print("✅ Login realizado")
        time.sleep(2)

        driver.get("https://uspdigital.usp.br/jupiterweb/beneficioBolsaUnificadaListar?codmnu=6684")
        time.sleep(10)

        edital = driver.find_element(By.ID, "anoofebnf")
        select = Select(edital)
        select.select_by_value("2015")

        time.sleep(10)

        enviar = driver.find_element(By.ID, "enviar")
        time.sleep(2)
        enviar.click()

        time.sleep(10)
        wait.until(EC.presence_of_element_located((By.ID, "gbox_projetos")))
        time.sleep(5)

        global df
        df = pd.DataFrame(columns=["Edital", "Unidade", "Título", "Vertente", "Orientador", "Total de Bolsa"])

        for pagina in range(1, 246):
            print(f"📄 Extraindo página {pagina}/245")
            df = extrair_tabela(driver, df)
            try:
                botao_prox = driver.find_element(By.ID, "next_div_projetos")
                if "ui-state-disabled" in botao_prox.get_attribute("class"):
                    break
                time.sleep(0.4)
                botao_prox.click()
            except:
                print("⚠️ Não achei botão de próxima página, parando.")
                break

        df.to_csv("bolsas_usp_2015.csv", index=False)
        print("✅ Dados salvos em bolsas_usp_2015.csv")



    finally:
        driver.quit()

if __name__ == "__main__":
    main()