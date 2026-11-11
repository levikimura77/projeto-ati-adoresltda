# Site do jogo Atiçadores LTDA

Site de apresentação com visual inspirado em jogos 2D em pixel art. O formulário envia nome, e-mail e sugestão para um servidor Python, que salva os dados em SQLite.

A seção **Download** disponibiliza `frontend/downloads/AticadoresLTDA.exe`, a compilação para Windows. Para atualizar o download depois de gerar uma nova versão, substitua esse arquivo pelo novo executável.

## Executar no Windows

Abra o PowerShell nesta pasta `site` e rode:

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

Depois, abra <http://127.0.0.1:5000> no navegador. Na primeira execução, o servidor cria automaticamente `backend/database/suggestions.sqlite3` e a tabela definida em `backend/database/schema.sql`.

**Importante:** abra o endereço `http://127.0.0.1:5000` enquanto `python app.py` estiver rodando. Não abra `frontend/index.html` diretamente nem use a extensão Live Server para enviar sugestões: esses modos servem apenas arquivos estáticos e não executam a API Python nem gravam no banco. Os caminhos relativos de CSS, JavaScript e logo também permitem visualizar a página com um servidor estático, mas o formulário só funciona com o servidor Python.

Se o PowerShell bloquear a ativação do ambiente virtual, rode os comandos de instalação e execução diretamente, sem ativá-lo:

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Para consultar as sugestões no SQLite:

```sql
SELECT name, email, suggestion, created_at
FROM suggestions
ORDER BY id DESC;
```

O servidor fica acessível apenas no computador local por padrão. Para publicar o site, será necessário hospedá-lo em um serviço que execute Python e mantenha o arquivo do banco de dados persistente.
