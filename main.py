import tkinter as tk
from tkinter import messagebox
import pandas as pd
import requests
from bs4 import BeautifulSoup

# Função para realizar a pesquisa no Google Maps via request
def google_maps_search(user_query):
    formatted_query = user_query.replace(' ', '+')  # Substitui espaços por '+' na consulta
    url = f"https://www.google.com/maps/search/{formatted_query}"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Gera exceção se houver erro
        html = response.text
    except Exception as e:
        print(f"Erro ao realizar a pesquisa no Google Maps: {e}")
        html = ""

    return html

def extract_data(html):
    soup = BeautifulSoup(html, 'html.parser')
    results = []

    print("HTML retornado:", soup.prettify())  # Para visualizar o HTML retornado

    # Itera sobre os resultados da pesquisa no Google Maps
    for g in soup.find_all('div', class_='section-result'):
        # Extraindo o nome
        nome_elemento = g.find('a', class_='hfpxzc')
        nome = nome_elemento.text.strip() if nome_elemento else 'Nome não encontrado'

        # Extraindo o telefone
        telefone_elemento = g.find('a', class_='Io6YTe fontBodyMedium kR99db fdkmkc')
        telefone = telefone_elemento.text.strip() if telefone_elemento else 'Telefone não encontrado'

        print(f"Resultado encontrado: Nome: {nome}, Telefone: {telefone}")

        # Adiciona os dados ao resultado
        results.append({
            'Nome': nome,
            'Telefone': telefone,
        })

    print("Resultados extraídos:", results)  # Verificar resultados extraídos
    return results

# Função para pesquisar e salvar resultados
def search_and_save():
    user_query = entry.get()
    if not user_query:
        messagebox.showwarning("Entrada Vazia", "Por favor, insira um termo de pesquisa.")
        return

    print(f"Consulta do usuário: {user_query}")  # Depuração: mostrar a consulta
    html = google_maps_search(user_query)  # Obtém o HTML da pesquisa no Google Maps
    data = extract_data(html)  # Passa o HTML para a função de extração

    if data:
        df = pd.DataFrame(data)
        df.to_excel('resultados_pesquisa_maps.xlsx', index=False, sheet_name='Resultados')
        messagebox.showinfo("Sucesso", "Resultados salvos em 'resultados_pesquisa_maps.xlsx'.")
    else:
        print("Nenhum resultado encontrado.")  # Mensagem de erro
        messagebox.showerror("Erro", "Nenhum resultado encontrado.")

# Configuração da interface do Tkinter
root = tk.Tk()
root.title("Pesquisa no Google Maps")
root.geometry("400x200")

label = tk.Label(root, text="Digite o termo de pesquisa:")
label.pack(pady=10)

entry = tk.Entry(root, width=50)
entry.pack(pady=10)

search_button = tk.Button(root, text="Pesquisar e Salvar", command=search_and_save)
search_button.pack(pady=20)

# Executa o loop principal do Tkinter
root.mainloop()
