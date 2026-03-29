# 🏓 Organizador de Campeonatos de Tênis de Mesa

Sistema web desenvolvido em **Django** para gerenciamento completo de campeonatos de tênis de mesa, incluindo cadastro de jogadores, organização de torneios, geração de confrontos e acompanhamento das partidas.

---

## 🚀 Funcionalidades

* 📌 Cadastro de campeonatos
* 👥 Cadastro de participantes
* 🏆 Sistema de ranking
* 🔀 Geração automática de rodadas (Sistema Suíço)
* 🎯 Fases eliminatórias (mata-mata)
* 📊 Controle de resultados das partidas
* 📺 Visualização de chaveamentos (brackets)
* 🧠 Organização automática dos confrontos
* 🔎 Consulta de standings (classificação geral)

---

## 🧱 Tecnologias Utilizadas

* 🐍 Python 3.x
* 🌐 Django
* 🗄️ SQLite (padrão, podendo migrar para PostgreSQL)
* 🎨 HTML + CSS + Bootstrap
* ⚙️ JavaScript (para interações e visualização de chaves)

---

## 📁 Estrutura do Projeto

```
organizador-campeonatos-tt/
│
├── core/                # App principal (torneios, lógica)
├── usuarios/            # Autenticação e usuários
├── static/              # Arquivos estáticos (CSS, JS)
├── templates/           # Templates HTML
├── db.sqlite3           # Banco de dados
├── manage.py
└── README.md
```

---

## ⚙️ Como rodar o projeto

### 1. Clone o repositório

```bash
git clone https://github.com/marcoantonio567/organizador-campeonatos-tt.git
cd organizador-campeonatos-tt
```

### 2. Crie um ambiente virtual

```bash
python -m venv venv
```

Ative:

* Windows:

```bash
venv\Scripts\activate
```

* Linux/Mac:

```bash
source venv/bin/activate
```

---

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

---

### 4. Rode as migrações

```bash
python manage.py migrate
```

---

### 5. Crie um superusuário

```bash
python manage.py createsuperuser
```

---

### 6. Execute o servidor

```bash
python manage.py runserver
```

Acesse no navegador:

```
http://127.0.0.1:8000/
```

---

## 🧠 Regras do Sistema

### Sistema Suíço

* Jogadores enfrentam adversários com desempenho semelhante
* Evita confrontos repetidos
* Pontuação acumulativa

### Fase Eliminatória

* Classificação dos melhores do suíço
* Confrontos em formato mata-mata
* Definição do campeão

---

## 📊 Modelagem (Resumo)

* **Campeonato**
* **Jogador**
* **Partida**
* **Rodada**
* **Ranking**

---

## 🎯 Objetivo do Projeto

Este sistema foi desenvolvido para:

* Facilitar a organização de campeonatos locais
* Automatizar o chaveamento e confrontos
* Melhorar a experiência de gestão de torneios
* Servir como base para projetos maiores (SaaS de torneios)

---

## 🔮 Possíveis melhorias futuras

* 📱 Interface mobile responsiva
* 📡 API REST com Django Rest Framework
* 🏅 Sistema de histórico de jogadores
* 📈 Estatísticas avançadas
* 🎥 Integração com telão (display de partidas)
* ☁️ Deploy em nuvem (AWS / Render)

---

## 🤝 Contribuição

Contribuições são bem-vindas!

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-feature`)
3. Commit (`git commit -m 'feat: nova feature'`)
4. Push (`git push origin feature/nova-feature`)
5. Abra um Pull Request

---

## 📄 Licença

Este projeto está sob a licença MIT.

---

## 👨‍💻 Autor

Desenvolvido por **Marco Antonio**
🔗 GitHub: [https://github.com/marcoantonio567](https://github.com/marcoantonio567)

---
