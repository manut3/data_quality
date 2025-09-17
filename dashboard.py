import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
from datetime import datetime
import ast

# Configuração 
st.set_page_config(
    page_title="Dashboard de Similaridade Semântica",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo 
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem;
    }
    .positive { color: #2ecc71; }
    .negative { color: #e74c3c; }
    .neutral { color: #f39c12; }
</style>
""", unsafe_allow_html=True)

def load_data():
    """Carrega dados do arquivo JSON ou CSV"""
    uploaded_file = st.sidebar.file_uploader(
        "📤 Carregue seu arquivo JSON ou CSV", 
        type=['json', 'csv']
    )
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.json'):
                data = json.load(uploaded_file)
                df = process_json_data(data)
            else:
                df = pd.read_csv(uploaded_file)
            
            return df
        except Exception as e:
            st.error(f"Erro ao carregar arquivo: {e}")
            return None
    else:
        st.info("👆 Por favor, carregue um arquivo JSON ou CSV")
        return None

def process_json_data(data):
    """Processa dados JSON do Postman"""
    resultados = []
    main_result = data['results'][0]
    
    for i in range(data.get('count', 0)):
        try:
            resultado = {
                'iteracao': i + 1,
                'status_code': main_result.get('responseCode', {}).get('code', 200),
                'response_time_ms': main_result.get('times', [0] * 20)[i] if i < len(main_result.get('times', [])) else 0,
                'test_name': main_result.get('name', 'N/A')
            }
            
            if 'allTests' in main_result and i < len(main_result['allTests']):
                testes = main_result['allTests'][i]
                resultado.update({
                    'resposta_tem_dois_scores': testes.get('Resposta tem dois scores', False),
                    'score_similar_maior': testes.get('Score similar maior que score diferente', False),
                    'score_similar_acima_075': testes.get('Score similar acima de 0.75', False),
                    'score_diferente_abaixo_04': testes.get('Score diferente abaixo de 0.4', False)
                })
            
            resultados.append(resultado)
            
        except Exception as e:
            st.warning(f"Erro na iteração {i+1}: {e}")
            continue
    
    return pd.DataFrame(resultados)

def create_dashboard(df):
    """Cria o dashboard com os dados"""
    
    # Header
    st.markdown('<h1 class="main-header">📊 Dashboard de Qualidade de Dados</h1>', unsafe_allow_html=True)
    
    # Métricas principais
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total de Iterações", len(df))
    
    with col2:
        success_rate = (df['status_code'] == 200).mean() * 100
        st.metric("Taxa de Sucesso", f"{success_rate:.1f}%")
    
    with col3:
        valid_comparisons = df['score_similar_maior'].mean() * 100
        st.metric("Comparações Válidas", f"{valid_comparisons:.1f}%")
    
    with col4:
        avg_response_time = df['response_time_ms'].mean()
        st.metric("Tempo Médio (ms)", f"{avg_response_time:.0f}")
    
    with col5:
        excellence_rate = ((df['score_similar_acima_075'] == True) & 
                          (df['score_diferente_abaixo_04'] == True)).mean() * 100
        st.metric("Excelência", f"{excellence_rate:.1f}%")
    
    # Abas para diferentes visualizações
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Visão Geral", "⏱️ Performance", "✅ Qualidade", "📋 Dados Brutos", "📊 Estatísticas"
    ])
    
    
    with tab1:
        st.subheader("Visão Geral dos Resultados")
        
        # Criar figura com subplots
        fig = plt.figure(figsize=(16, 12))
        gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
        
        # Gráfico 1: Distribuição de status codes
        ax1 = fig.add_subplot(gs[0, 0])
        status_counts = df['status_code'].value_counts()
        colors_status = ['#2Ecc71' if code == 200 else '#E74c3c' for code in status_counts.index]
        wedges, texts, autotexts = ax1.pie(status_counts.values, labels=status_counts.index, 
                                        autopct='%1.1f%%', colors=colors_status, startangle=90,
                                        textprops={'fontsize': 10})
        ax1.set_title('Distribuição de Status Codes', fontweight='bold', fontsize=12)
        
        # Gráfico 2: Histograma de tempo de resposta
        ax2 = fig.add_subplot(gs[0, 1])
        n, bins, patches = ax2.hist(df['response_time_ms'], bins=12, alpha=0.7, 
                                color='#3498db', edgecolor='white', linewidth=0.5)
        ax2.axvline(df['response_time_ms'].mean(), color='#e74c3c', linestyle='--', linewidth=2,
                    label=f'Média: {df["response_time_ms"].mean():.0f}ms')
        ax2.set_xlabel('Tempo de Resposta (ms)', fontsize=10)
        ax2.set_ylabel('Frequência', fontsize=10)
        ax2.set_title('Distribuição do Tempo de Resposta', fontweight='bold', fontsize=12)
        ax2.legend()
        ax2.grid(True, alpha=0.2)
        
         # Gráfico 3: Eficacia do modelo
        ax3 = fig.add_subplot(gs[1, 0])
        valid_data = df['score_similar_maior'].value_counts()
        colors_valid = ['#e74c3c', '#2ecc71']
        bars3 = ax3.bar(['Inválido', 'Válido'], valid_data.values, color=colors_valid, alpha=0.8)

        ax3.set_title('Eficacia do Modelo em Distinguir Frases\n(Similar vs Diferente)', fontweight='bold', fontsize=12)

        ax3.set_ylabel('Quantidade', fontsize=10)



        # Adicionar valores e porcentagens
        total = sum(valid_data.values)
        for i, (bar, value) in enumerate(zip(bars3, valid_data.values)):
            percentage = (value / total) * 100
            ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                    f'{value}\n({percentage:.1f}%)', ha='center', va='bottom', 
                    fontweight='bold', fontsize=9)
        
        # Gráfico 4: Taxa de Sucesso por Tipo de Teste
        ax4 = fig.add_subplot(gs[1, 1])
        test_types = ['Dois Scores', 'Similar >\nDiferente', 'Similar >\n0.75', 'Diferente <\n0.4']
        success_rates = [
            df['resposta_tem_dois_scores'].mean() * 100,
            df['score_similar_maior'].mean() * 100,
            df['score_similar_acima_075'].mean() * 100,
            df['score_diferente_abaixo_04'].mean() * 100
        ]
        
        colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4']
        bars4 = ax4.bar(test_types, success_rates, color=colors, alpha=0.8, edgecolor='white', linewidth=1)
        ax4.set_ylabel('Taxa de Sucesso (%)', fontsize=10)
        ax4.set_title('Performance por Métrica de Qualidade', fontweight='bold', fontsize=12)
        ax4.set_ylim(0, 105)
        ax4.grid(True, alpha=0.2, axis='y')
        
        # Adicionar valores nas barras
        for bar, value in zip(bars4, success_rates):
            ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                    f'{value:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=9)
        
        # Linhas de referência
        ax4.axhline(y=90, color='#27ae60', linestyle=':', alpha=0.7, linewidth=1)
        ax4.axhline(y=70, color='#f39c12', linestyle=':', alpha=0.7, linewidth=1)
        ax4.axhline(y=50, color='#e74c3c', linestyle=':', alpha=0.7, linewidth=1)
        
        plt.tight_layout()
        st.pyplot(fig)
        
        # Métricas rápidas abaixo dos gráficos
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📊 Total Testes", len(df))
        
        with col2:
            st.metric("✅ Sucesso HTTP", f"{(df['status_code'] == 200).mean() * 100:.1f}%")
        
        with col3:
            st.metric("🎯 Comparações Válidas", f"{df['score_similar_maior'].mean() * 100:.1f}%")
        
        with col4:
            excellence = ((df['score_similar_acima_075'] == True) & 
                        (df['score_diferente_abaixo_04'] == True)).mean() * 100
            st.metric("🏅 Qualidade Excelente", f"{excellence:.1f}%")



    
    with tab2:
        st.subheader("Análise de Performance")
        
        # Criar duas colunas: uma para o gráfico, outra para as estatísticas
        col_graph, col_stats = st.columns([2, 1])  # 2/3 para gráfico, 1/3 para stats
        
        with col_graph:
            # Gráfico de linha - Performance ao longo do tempo
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.plot(df['iteracao'], df['response_time_ms'], marker='o', linewidth=2, 
                    color='steelblue', markersize=6)
            ax.set_xlabel('Iteração', fontsize=12)
            ax.set_ylabel('Tempo de Resposta (ms)', fontsize=12)
            ax.set_title('Performance ao Longo do Tempo', fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3)
            
            # Adicionar valor médio como linha de referência
            avg_time = df['response_time_ms'].mean()
            ax.axhline(y=avg_time, color='red', linestyle='--', alpha=0.8, 
                    label=f'Média: {avg_time:.0f}ms')
            ax.legend()
            
            st.pyplot(fig)
        
        with col_stats:
            st.subheader("📊 Estatísticas")
            
            # Container para as métricas
            with st.container():
                st.metric(
                    "⏱️ Tempo Médio", 
                    f"{df['response_time_ms'].mean():.0f} ms",
                    delta=f"{df['response_time_ms'].std():.0f} ms std"
                )
                
                st.metric(
                    "📉 Tempo Mínimo", 
                    f"{df['response_time_ms'].min():.0f} ms"
                )
                
                st.metric(
                    "📈 Tempo Máximo", 
                    f"{df['response_time_ms'].max():.0f} ms"
                )
                
                st.metric(
                    "🎯 Desvio Padrão", 
                    f"{df['response_time_ms'].std():.0f} ms"
                )
            
            # Estatísticas adicionais
            st.info(f"""
            **📋 Resumo:**
            - Total de medições: {len(df)}
            - Variação: {df['response_time_ms'].max() - df['response_time_ms'].min():.0f} ms
            - Coeficiente de variação: {(df['response_time_ms'].std() / df['response_time_ms'].mean() * 100):.1f}%
            """)
    
    with tab3:
        st.subheader("Análise de Qualidade Semântica")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Heatmap de correlação de qualidade
            quality_df = df[['score_similar_maior', 'score_similar_acima_075', 'score_diferente_abaixo_04']]
            quality_df = quality_df.replace({True: 1, False: 0})
            
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.heatmap(quality_df.corr(), annot=True, cmap='coolwarm', center=0, ax=ax)
            ax.set_title('Correlação entre Métricas de Qualidade')
            st.pyplot(fig)
        
        with col2:
            # Barras de métricas de qualidade
            metrics = {
                'Dois Scores': df['resposta_tem_dois_scores'].mean() * 100,
                'Similar > Diferente': df['score_similar_maior'].mean() * 100,
                'Similar > 0.75': df['score_similar_acima_075'].mean() * 100,
                'Diferente < 0.4': df['score_diferente_abaixo_04'].mean() * 100
            }
            
            fig, ax = plt.subplots(figsize=(10, 6))
            bars = ax.bar(metrics.keys(), metrics.values(), color=['blue', 'green', 'orange', 'red'])
            ax.set_ylabel('Taxa de Sucesso (%)')
            ax.set_title('Métricas de Qualidade')
            ax.set_ylim(0, 100)
            
            # Adicionar valores nas barras
            for bar, value in zip(bars, metrics.values()):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2, 
                       f'{value:.1f}%', ha='center', va='bottom')
            
            st.pyplot(fig)
    
    with tab4:
        st.subheader("Dados Brutos")
        
        # DataFrame 
        st.dataframe(
            df.style.format({
                'response_time_ms': '{:.0f}ms',
                'resposta_tem_dois_scores': lambda x: '✅' if x else '❌',
                'score_similar_maior': lambda x: '✅' if x else '❌',
                'score_similar_acima_075': lambda x: '✅' if x else '❌',
                'score_diferente_abaixo_04': lambda x: '✅' if x else '❌'
            }),
            height=400
        )
        
        # Opção de download
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name="resultados_analise.csv",
            mime="text/csv"
        )
    
    with tab5:
        st.subheader("Estatísticas Detalhadas")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Estatísticas Descritivas:**")
            st.dataframe(df.describe())
        
        with col2:
            st.write("**Informações do Dataset:**")
            info_data = {
                'Total de Linhas': len(df),
                'Total de Colunas': len(df.columns),
                'Colunas Numéricas': len(df.select_dtypes(include=['number']).columns),
                'Colunas Booleanas': len(df.select_dtypes(include=['bool']).columns),
                'Valores Faltantes': df.isnull().sum().sum()
            }
            
            for key, value in info_data.items():
                st.write(f"{key}: {value}")

def main():
    """Função principal"""
    st.sidebar.title("🔧 Configurações")
    st.sidebar.info("Dashboard para análise de resultados de similaridade semântica")
    
    # Carregar dados
    df = load_data()
    
    if df is not None:
        create_dashboard(df)
    else:
        # Exemplo de dados para demonstração
        st.warning("💡 Carregando dados de exemplo...")
        

if __name__ == "__main__":
    main()