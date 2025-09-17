# 📊 Dashboard de Análise de Similaridade Semântica


## Sobre o Projeto

Este projeto realiza análise de performance e qualidade semântica do modelo `sentence-transformers/all-MiniLM-L6-v2` da Hugging Face, testando sua capacidade de distinguir similaridades entre frases com contexto geográfico.

## Contexto do Desafio

São realizados testes de qualidade semântica e performance na API do modelo `sentence-transformers/all-MiniLM-L6-v2` do Hugging Face.

Sendo que o modelo transforma frases em embeddings vetoriais e calcula similaridades semânticas entre elas, retornando **scores de similaridade semântica** (valores entre 0 e 1).
Quanto maior o score, mais similares são as frases.





🔹 **Por que isso é importante em um contexto de negócio?**

Empresas que trabalham com **inteligência artificial e dados geográficos** dependem de modelos capazes de identificar similaridades de forma confiável. Por exemplo:

* **Normalização de dados geográficos**: reconhecer que “A floresta amazônica está na América do Sul” e “A selva amazônica fica na América do Sul” têm o mesmo significado, mesmo com palavras diferentes.
* **Busca semântica em grandes bases de dados**: localizar informações relevantes mesmo que o usuário utilize termos ou expressões distintas.
* **Detecção de inconsistências** em cadastros imobiliários, registros territoriais ou documentos geoespaciais, permitindo maior precisão na fiscalização ou na tomada de decisão.


🔹 **Por que automação + randomização + análise de dados?**

* **Automação de testes de API**: garante que o modelo seja avaliado de forma repetível, rápida e escalável, sem dependendo menos de verificações manuais.
* **Randomização no Pre-request Script**: introduz variabilidade nos testes, simulando cenários reais de uso, reduzindo viés e aumentando a representatividade dos resultados.

---




## Metodologia de Testes no Postman

### Estrutura dos Testes
Foram realizadas 20 iterações automáticas usando o Collection Runner, cada uma contendo:

- **1 frase principal fixa**: "A floresta amazônica está localizada na América do Sul."
- **1 frase similar** (selecionada aleatoriamente)
- **1 frase diferente** (selecionada aleatoriamente)

### A randomização no Pre-request Script é importante para:
- Evitar viés de teste com combinações fixas
- Simular uso da API com entradas variadas

### Códigos Postman Implementados

#### Pre-request Script
```javascript
// Frase principal (fixa)
const frase_principal = "A floresta amazônica está localizada na América do Sul.";

// Frases com alta similaridade esperada
const frases_similares = [
    "A selva amazônica fica na América do Sul.",
    "A América do Sul abriga a floresta amazônica.",
    "A floresta amazônica se estende por vários países da América do Sul.",
    "O Brasil contém grande parte da floresta amazônica.",
    "A Amazônia é a maior floresta da América do Sul."
];

// Frases com baixa similaridade esperada
const frases_diferentes = [
    "O Monte Everest é o pico mais alto do mundo.",
    "O deserto do Saara está localizado na África.",
    "Nova York é conhecida por seus arranha-céus.",
    "Tóquio é a capital do Japão.",
    "A Austrália é um continente-ilha."
];

// Sorteia uma frase de cada grupo
const frase_similar = frases_similares[Math.floor(Math.random() * frases_similares.length)];
const frase_diferente = frases_diferentes[Math.floor(Math.random() * frases_diferentes.length)];

// Variáveis para uso na requisição
pm.variables.set("frase_principal", frase_principal);
pm.variables.set("frase_similar", frase_similar);
pm.variables.set("frase_diferente", frase_diferente);
```

#### Body da Requisição
```json
{
  "inputs": {
    "source_sentence": "{{frase_principal}}",
    "sentences": [
      "{{frase_similar}}",
      "{{frase_diferente}}"
    ]
  }
}
```

#### Test Script
```javascript
// Verifica se a resposta foi bem-sucedida
pm.test("Status code é 200", function () {
    pm.response.to.have.status(200);
});

// Verifica se a resposta é um array
pm.test("Resposta é um array", function () {
    pm.expect(pm.response.json()).to.be.an('array');
});

let responseData = pm.response.json();

// Verifica se há dois scores
pm.test("Resposta tem dois scores", function () {
    pm.expect(responseData.length).to.eql(2);
});

// Extrai os scores
const score_similar = responseData[0];
const score_diferente = responseData[1];

// Recupera as frases 
const frase_principal = pm.variables.get("frase_principal");
const frase_similar = pm.variables.get("frase_similar");
const frase_diferente = pm.variables.get("frase_diferente");

// Salva os scores nas variáveis de ambiente
pm.environment.set("score_similar", score_similar);
pm.environment.set("score_diferente", score_diferente);

// Valida se score da frase similar é maior que da frase diferente
const comparacao_valida = score_similar > score_diferente;
pm.environment.set("comparacao_valida", comparacao_valida);

// Classifica a qualidade da comparação
let qualidade_comparacao = "indefinida";
if (score_similar >= 0.75 && score_diferente <= 0.4) {
    qualidade_comparacao = "excelente";
} else if (score_similar >= 0.6) {
    qualidade_comparacao = "aceitável";
} else {
    qualidade_comparacao = "ruim";
}
pm.environment.set("qualidade_comparacao", qualidade_comparacao);

pm.test("Score similar maior que score diferente", function () {
    pm.expect(score_similar).to.be.above(score_diferente);
});

// Métricas de performance da api
pm.environment.set("codigo_status", pm.response.code);
pm.environment.set("tempo_resposta_ms", pm.response.responseTime);
pm.environment.set("tamanho_resposta_bytes", pm.response.headers.get('Content-Length') || pm.response.text().length);
```




## Como Executar o Projeto

### Pré-requisitos
- Python 3.8 ou superior
- Git
- Postman (para executar novos testes)

### Instalação das Dependências

```bash
# Clone o repositório
git clone <url-do-repositorio>
cd DATA_QUALITY

# Instale as dependências
pip install -r requirements.txt
```

Crie um arquivo `requirements.txt` com:
```
streamlit
pandas
matplotlib
seaborn
numpy
```

### Método 1: Usando os Arquivos Exportados (Recomendado)

1. **Execute o script de extração** para processar os resultados do Postman:
```bash
python extraction.py
```

2. **Execute o dashboard Streamlit**:
```bash
streamlit run dashboard.py
```

3. **No dashboard**, faça upload do arquivo CSV gerado (`resultados_completos_*.csv`)

### Método 2: Executando Novos Testes no Postman

1. **Importe a coleção** `similarity-collection.json.postman_collection.json` no Postman
2. **Configure a autenticação** com seu token da Hugging Face
3. **Execute o Collection Runner** com 20 iterações
4. **Exporte os resultados** no formato JSON
5. **Use o script de extração** para converter para CSV
6. **Visualize os resultados** no dashboard Streamlit

## Estrutura do Projeto

```
DATA_QUALITY/
├── dashboard.py              # Aplicação Streamlit para visualização
├── extraction.py             # Script para converter JSON → CSV
├── similarity-collection.json # Coleção do Postman para testes
├── resultados_completos_*.csv # Resultados exportados (gerado automaticamente)
└── README.md                 # Este arquivo
```

## Scripts Principais

### extraction.py
Converte os resultados JSON exportados do Postman para formato CSV, extraindo métricas importantes como:
- Status codes das respostas
- Tempos de resposta
- Resultados dos testes de similaridade
- Métricas de qualidade semântica

### dashboard.py
Aplicação Streamlit que fornece visualizações completas dos resultados:
- **Visão Geral**: Métricas principais e distribuições
- **Performance**: Análise de tempos de resposta e estabilidade
- **Qualidade**: Avaliação da eficácia do modelo
- **Dados Brutos**: Tabela interativa com todos os resultados
- **Estatísticas**: Análises descritivas detalhadas

<img width="1845" height="861" alt="image" src="https://github.com/user-attachments/assets/e6d830b9-4931-427a-89ca-8f1a28214b27" />

<img width="1845" height="861" alt="image" src="https://github.com/user-attachments/assets/e591f67c-6350-4946-b99c-68e7a80f711c" />

<img width="1837" height="893" alt="image" src="https://github.com/user-attachments/assets/7e529f0c-e15c-417b-8000-a6939c609f22" />

<img width="1837" height="893" alt="image" src="https://github.com/user-attachments/assets/063a35ec-d552-40c5-a215-63690ff456b4" />

<img width="944" height="397" alt="image" src="https://github.com/user-attachments/assets/b622155b-a8d0-4ab0-aac0-9ee63558b51c" />







