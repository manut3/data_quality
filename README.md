
📊 Dashboard de Análise de Similaridade Semântica
📋 Sobre o Projeto
Este projeto realiza análise de performance e qualidade semântica do modelo sentence-transformers/all-MiniLM-L6-v2 da Hugging Face, testando sua capacidade de distinguir similaridades entre frases com contexto geográfico relevante para a Cortex Intelligence.

🚀 Como Executar o Projeto
Pré-requisitos
Python 3.8 ou superior

Git

Postman (opcional, para executar novos testes)

Instalação das Dependências
bash
# Clone o repositório
git clone <url-do-repositorio>
cd DATA_QUALITY

# Instale as dependências
pip install -r requirements.txt
Crie um arquivo requirements.txt com:

text
streamlit
pandas
matplotlib
seaborn
numpy
Método 1: Usando os Arquivos Exportados (Recomendado)
Execute o script de extração para processar os resultados do Postman:

bash
python extraction.py
Execute o dashboard Streamlit:

bash
streamlit run dashboard.py
No dashboard, faça upload do arquivo CSV gerado (resultados_completos_*.csv)

Método 2: Executando Novos Testes no Postman
Importe a coleção similarity-collection.json no Postman

Configure a autenticação com seu token da Hugging Face

Execute o Collection Runner com 20 iterações

Exporte os resultados no formato JSON

Use o script de extração para converter para CSV

Visualize os resultados no dashboard Streamlit

📁 Estrutura do Projeto
text
DATA_QUALITY/
├── dashboard.py              # Aplicação Streamlit para visualização
├── extraction.py             # Script para converter JSON → CSV
├── similarity-collection.json # Coleção do Postman para testes
├── resultados_completos_*.csv # Resultados exportados (gerado automaticamente)
└── README.md                 # Este arquivo
🔧 Scripts Principais
extraction.py
Converte os resultados JSON exportados do Postman para formato CSV, extraindo métricas importantes como:

Status codes das respostas

Tempos de resposta

Resultados dos testes de similaridade

Métricas de qualidade semântica

dashboard.py
Aplicação Streamlit que fornece visualizações completas dos resultados:

Visão Geral: Métricas principais e distribuições

Performance: Análise de tempos de resposta e estabilidade

Qualidade: Avaliação da eficácia do modelo

Dados Brutos: Tabela interativa com todos os resultados

Estatísticas: Análises descritivas detalhadas

📊 Métricas Analisadas
Performance da API
Tempo de resposta (ms)

Status codes

Estabilidade das requisições

Qualidade Semântica
Score de similaridade para frases relacionadas

Score de similaridade para frases não relacionadas

Eficácia na distinção entre frases similares e diferentes
