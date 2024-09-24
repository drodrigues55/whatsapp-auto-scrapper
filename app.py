from flask import Flask, render_template, request
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import webbrowser
import threading
import re
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side

app = Flask(__name__)

# Defina o caminho do ChromeDriver
CHROME_DRIVER_PATH = r'C:\Users\ZNIT\Documents\chromedriver.exe'
service = Service(CHROME_DRIVER_PATH)

# Função para realizar a pesquisa no Google em modo headless
def google_search(user_query):
    # Formate a consulta aqui
    formatted_query = f"{user_query}; instagram"  # Formatação desejada

    chrome_options = Options()
    # Remova '--headless' para depuração
    # chrome_options.add_argument('--headless')  # Executar em modo headless
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get("https://www.google.com")

    try:
        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys(formatted_query)  # Use a string formatada
        search_box.submit()
        
        driver.implicitly_wait(10)  # Aguarde até 10 segundos
        html = driver.page_source
    except Exception as e:
        print(f"Erro ao realizar a pesquisa: {e}")
        html = ""
    finally:
        driver.quit()

    return html

# Função para extrair dados usando BeautifulSoup
def extract_data(html):
    soup = BeautifulSoup(html, 'html.parser')  # Cria um objeto BeautifulSoup a partir do HTML
    results = []

    print("HTML retornado:", soup.prettify())  # Para visualizar o HTML retornado

    # Itera sobre cada resultado encontrado na página
    for g in soup.find_all('div', class_='g'):  # 'g' é a classe dos resultados do Google
        title = g.find('h3')  # Busca o título do resultado
        link = g.find('a', href=True)  # Busca o link do resultado

        # Verifica se tanto o título quanto o link foram encontrados
        if title and link:
            title_text = title.text
            link_url = link['href']
            print(f"Resultado encontrado: {title_text} - {link_url}")  # Adiciona depuração

            # Adicione a lógica de extração de Nome, Telefone e Cidade
            results.append({
                'Nome': title_text,  # Aqui você pode substituir pelo nome real encontrado
                'Telefone': '123456789',  # Exemplo de telefone
                'Cidade': extract_city_from_title(title_text) or 'Cidade Desconhecida',  # Usa a cidade extraída ou um valor padrão
            })

    print("Resultados extraídos:", results)  # Verificar resultados extraídos
    return results

# Função para extrair a cidade do título usando expressões regulares
def extract_city_from_title(title):
    cities = ["Campo Grande"]  # Adicione mais cidades conforme necessário
    pattern = r'\b(?:' + '|'.join(map(re.escape, cities)) + r')\b'
    match = re.search(pattern, title)
    return match.group(0) if match else None

# Rota para a página inicial
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_query = request.form['query']
        print(f"Consulta do usuário: {user_query}")  # Depuração: mostrar a consulta

        # Chama google_search passando a consulta do usuário
        print(f"Realizando pesquisa: {user_query}")  # Depuração: mostrar a pesquisa
        html = google_search(user_query)  # Isso obtém o HTML da pesquisa
        data = extract_data(html)          # Passa o HTML para a função de extração

        if data:
            df = pd.DataFrame(data)
            df.to_excel('resultados_pesquisa.xlsx', index=False, sheet_name='Resultados')
            return render_template('success.html')
        else:
            print("Nenhum resultado encontrado.")  # Mensagem de erro
            return "Nenhum resultado encontrado.", 404

    return render_template('index.html')

# Rota para a página de sucesso
@app.route('/success')
def success():
    return render_template('success.html')

# Função para abrir a URL no navegador
def open_browser():
    webbrowser.open('http://127.0.0.1:5000/')

# Executa o servidor
if __name__ == '__main__':
    threading.Timer(1, open_browser).start()
    app.run(debug=True)
