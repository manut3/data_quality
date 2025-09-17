import json
import csv
from datetime import datetime

def convert_postman_results_to_csv():
    """Converte resultados exportados do Postman para CSV - versão corrigida"""
    
    try:
        with open('similarity-tests-results.json.postman_test_run.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        print("Arquivo JSON carregado com sucesso!")
    except FileNotFoundError:
        print("Arquivo 'similarity-tests-results.json.postman_test_run.json' não encontrado.")
        return
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON: {e}")
        return
    
    resultados = []
    
    print(f"Analisando {data.get('count', 0)} execuções...")
    
    if 'results' not in data or not data['results']:
        print("Nenhum resultado encontrado no arquivo!")
        return
    
    main_result = data['results'][0]
    
    # Extrair dados de todas as iterações
    for i in range(data.get('count', 0)):
        try:
            # Criar resultado para cada iteração
            resultado = {
                'iteracao': i + 1,
                'timestamp': datetime.fromisoformat(data['startedAt'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S'),
                'status_code': main_result.get('responseCode', {}).get('code', 'N/A'),
                'response_time_ms': main_result.get('times', [0] * 20)[i] if i < len(main_result.get('times', [])) else 0,
                'nome_test': main_result.get('name', 'N/A')
            }
            
            if 'allTests' in main_result and i < len(main_result['allTests']):
                testes = main_result['allTests'][i]
                resultado.update({
                    'resposta_tem_dois_scores': testes.get('Resposta tem dois scores', 'N/A'),
                    'score_similar_maior': testes.get('Score similar maior que score diferente', 'N/A'),
                    'score_similar_acima_075': testes.get('Score similar acima de 0.75', 'N/A'),
                    'score_diferente_abaixo_04': testes.get('Score diferente abaixo de 0.4', 'N/A')
                })
            else:
                resultado.update({
                    'resposta_tem_dois_scores': 'N/A',
                    'score_similar_maior': 'N/A',
                    'score_similar_acima_075': 'N/A',
                    'score_diferente_abaixo_04': 'N/A'
                })
            
            resultados.append(resultado)
            
        except Exception as e:
            print(f" Erro ao processar iteração {i+1}: {e}")
            continue
    
    # Salvar em CSV
    if resultados:
        nome_arquivo = f"resultados_completos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(nome_arquivo, 'w', newline='', encoding='utf-8') as csvfile:
            campos = [
                'iteracao', 'timestamp', 'status_code', 'response_time_ms', 
                'nome_test', 'resposta_tem_dois_scores', 'score_similar_maior',
                'score_similar_acima_075', 'score_diferente_abaixo_04'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=campos)
            writer.writeheader()
            writer.writerows(resultados)
        
        print(f"{len(resultados)} resultados convertidos e salvos em: {nome_arquivo}")
        
        # Calculo estatísticas
        total = len(resultados)
        sucesso = sum(1 for r in resultados if r.get('status_code') == 200)
        
        dois_scores = sum(1 for r in resultados if r.get('resposta_tem_dois_scores') is True)
        similar_maior = sum(1 for r in resultados if r.get('score_similar_maior') is True)
        similar_acima = sum(1 for r in resultados if r.get('score_similar_acima_075') is True)
        diferente_abaixo = sum(1 for r in resultados if r.get('score_diferente_abaixo_04') is True)
        
        
    else:
        print(" Nenhum resultado válido encontrado.")

if __name__ == "__main__":
    print(" CONVERSOR DE RESULTADOS POSTMAN PARA CSV")
    print("=" * 50)
    convert_postman_results_to_csv()