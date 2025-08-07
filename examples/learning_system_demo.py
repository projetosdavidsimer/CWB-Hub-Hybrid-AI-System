"""
Demonstração do Sistema de Aprendizado Contínuo CWB Hub
Melhoria #7 - Exemplo prático de uso

Este exemplo demonstra como usar o sistema de aprendizado contínuo
para melhorar continuamente a performance dos agentes CWB Hub.

Funcionalidades demonstradas:
1. Inicialização do sistema
2. Processamento de feedback
3. Análise de padrões
4. Adaptação de agentes
5. Insights de aprendizado

Criado por: David Simer
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
import json

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from learning import (
    learning_system,
    pattern_analyzer,
    feedback_processor,
    learning_integration,
    FeedbackType,
    LearningEventType
)

from core.hybrid_ai_orchestrator import HybridAIOrchestrator


class LearningSystemDemo:
    """Demonstração do Sistema de Aprendizado Contínuo"""
    
    def __init__(self):
        self.orchestrator = None
        self.demo_data = {
            "sessions": [],
            "feedback_samples": [
                {
                    "text": "Excelente resposta da Ana! Muito clara e útil.",
                    "rating": 5,
                    "agent": "ana_beatriz_costa"
                },
                {
                    "text": "Carlos foi muito técnico, mas poderia ser mais claro.",
                    "rating": 3,
                    "agent": "carlos_eduardo_santos"
                },
                {
                    "text": "Sofia deu uma solução perfeita para o problema web!",
                    "rating": 5,
                    "agent": "sofia_oliveira"
                },
                {
                    "text": "A colaboração entre os agentes foi confusa.",
                    "rating": 2,
                    "agent": None
                },
                {
                    "text": "Gabriel ajudou muito com o desenvolvimento mobile.",
                    "rating": 4,
                    "agent": "gabriel_mendes"
                },
                {
                    "text": "Isabella criou um design incrível! Muito criativa.",
                    "rating": 5,
                    "agent": "isabella_santos"
                },
                {
                    "text": "Lucas encontrou vários bugs importantes. Bom trabalho!",
                    "rating": 4,
                    "agent": "lucas_pereira"
                },
                {
                    "text": "Mariana configurou tudo perfeitamente. DevOps excelente!",
                    "rating": 5,
                    "agent": "mariana_rodrigues"
                },
                {
                    "text": "Pedro organizou bem o projeto, mas poderia ser mais ágil.",
                    "rating": 3,
                    "agent": "pedro_henrique_almeida"
                },
                {
                    "text": "A equipe trabalhou bem juntos neste projeto!",
                    "rating": 4,
                    "agent": None
                }
            ]
        }
    
    async def initialize_system(self):
        """Inicializa o sistema CWB Hub com aprendizado"""
        print("🚀 Inicializando Sistema CWB Hub com Aprendizado Contínuo...")
        
        # Inicializar orquestrador
        self.orchestrator = HybridAIOrchestrator()
        await self.orchestrator.initialize_agents()
        
        # Inicializar integração de aprendizado
        await learning_integration.initialize(self.orchestrator)
        
        print("✅ Sistema inicializado com sucesso!")
        print(f"📊 Agentes ativos: {len(self.orchestrator.agents)}")
        print(f"🧠 Sistema de aprendizado: {'Ativo' if learning_integration.is_active else 'Inativo'}")
    
    async def simulate_user_sessions(self):
        """Simula sessões de usuário para gerar dados"""
        print("\n🎭 Simulando sessões de usuário...")
        
        sample_requests = [
            "Como criar um app mobile para e-commerce?",
            "Preciso de uma arquitetura web escalável",
            "Como implementar testes automatizados?",
            "Qual a melhor estratégia de DevOps?",
            "Como criar uma interface de usuário moderna?",
            "Preciso de ajuda com gerenciamento de projeto ágil",
            "Como otimizar performance de banco de dados?",
            "Qual framework usar para desenvolvimento full-stack?"
        ]
        
        for i, request in enumerate(sample_requests):
            print(f"  📝 Processando requisição {i+1}: {request[:50]}...")
            
            try:
                # Processar requisição
                response = await self.orchestrator.process_request(request)
                
                # Simular delay realista
                await asyncio.sleep(0.5)
                
                print(f"  ✅ Resposta gerada ({len(response)} caracteres)")
                
            except Exception as e:
                print(f"  ❌ Erro na requisição {i+1}: {e}")
        
        print(f"✅ {len(sample_requests)} sessões simuladas!")
    
    async def process_feedback_samples(self):
        """Processa amostras de feedback"""
        print("\n💬 Processando feedback dos usuários...")
        
        for i, feedback_sample in enumerate(self.demo_data["feedback_samples"]):
            print(f"  📝 Processando feedback {i+1}: {feedback_sample['text'][:40]}...")
            
            try:
                # Processar feedback através da integração
                result = await learning_integration.process_user_feedback(
                    feedback_text=feedback_sample["text"],
                    session_id=f"demo_session_{i}",
                    user_id=f"demo_user_{i % 3}",  # 3 usuários diferentes
                    rating=feedback_sample["rating"]
                )
                
                sentiment = result["processed_feedback"]["sentiment"]
                priority = result["processed_feedback"]["priority"]
                
                print(f"  ✅ Feedback processado - Sentimento: {sentiment}, Prioridade: {priority}")
                
            except Exception as e:
                print(f"  ❌ Erro no feedback {i+1}: {e}")
        
        print(f"✅ {len(self.demo_data['feedback_samples'])} feedbacks processados!")
    
    async def demonstrate_pattern_analysis(self):
        """Demonstra análise de padrões"""
        print("\n🔍 Analisando padrões de uso...")
        
        try:
            # Obter sessões ativas para análise
            sessions = list(self.orchestrator.active_sessions.values())
            
            if not sessions:
                print("  ⚠️ Nenhuma sessão ativa encontrada para análise")
                return
            
            # Analisar padrões
            analysis_result = await pattern_analyzer.analyze_session_patterns(sessions)
            
            print(f"  📊 Análise concluída:")
            print(f"    • Padrões encontrados: {len(analysis_result.patterns_found)}")
            print(f"    • Confiança média: {analysis_result.confidence_score:.2f}")
            print(f"    • Qualidade dos dados: {analysis_result.data_quality:.2f}")
            
            # Mostrar insights
            if analysis_result.insights:
                print(f"  💡 Insights principais:")
                for insight in analysis_result.insights[:3]:
                    print(f"    • {insight}")
            
            # Mostrar recomendações
            if analysis_result.recommendations:
                print(f"  🎯 Recomendações:")
                for rec in analysis_result.recommendations[:3]:
                    print(f"    • {rec}")
            
        except Exception as e:
            print(f"  ❌ Erro na análise de padrões: {e}")
    
    async def demonstrate_agent_adaptation(self):
        """Demonstra adaptação de agentes"""
        print("\n🔄 Demonstrando adaptação de agentes...")
        
        try:
            # Obter insights de um agente específico
            agent_id = "ana_beatriz_costa"
            insights = await learning_integration.get_learning_insights(agent_id)
            
            print(f"  📊 Insights do agente {agent_id}:")
            metrics = insights.get("current_metrics", {})
            print(f"    • Performance: {metrics.get('performance_score', 0):.2f}")
            print(f"    • Feedback Score: {metrics.get('feedback_score', 0):.2f}")
            print(f"    • Colaboração: {metrics.get('collaboration_effectiveness', 0):.2f}")
            
            # Aplicar adaptação manual
            adaptation_result = await learning_integration.trigger_manual_adaptation(
                agent_id=agent_id,
                adaptation_type="performance_improvement",
                parameters={
                    "communication_style": "more_detailed",
                    "collaboration_style": "enhanced_synergy"
                }
            )
            
            if adaptation_result.get("success"):
                print(f"  ✅ Adaptação aplicada com sucesso para {agent_id}")
            else:
                print(f"  ❌ Falha na adaptação para {agent_id}")
            
        except Exception as e:
            print(f"  ❌ Erro na adaptação: {e}")
    
    async def show_learning_analytics(self):
        """Mostra analytics de aprendizado"""
        print("\n📈 Analytics de Aprendizado...")
        
        try:
            # Analytics de feedback
            feedback_analytics = await learning_integration.get_feedback_analytics(7)
            
            summary = feedback_analytics.get("summary", {})
            if summary and "total_feedback" in summary:
                print(f"  📊 Resumo de Feedback (7 dias):")
                print(f"    • Total de feedbacks: {summary['total_feedback']}")
                
                metrics = summary.get("metrics", {})
                if metrics:
                    print(f"    • Sentimento médio: {metrics.get('avg_sentiment', 0):.2f}")
                    print(f"    • Rating médio: {metrics.get('avg_rating', 0):.1f}/5")
                    print(f"    • Taxa positiva: {metrics.get('positive_ratio', 0):.1%}")
                
                # Distribuições
                distributions = summary.get("distributions", {})
                if distributions.get("sentiment"):
                    print(f"    • Distribuição de sentimento:")
                    for sentiment, count in distributions["sentiment"].items():
                        print(f"      - {sentiment}: {count}")
            
            # Tendências
            trends = feedback_analytics.get("trends", [])
            if trends:
                print(f"  📈 Tendências identificadas:")
                for trend in trends[:3]:
                    direction_emoji = "📈" if trend["direction"] == "improving" else "📉" if trend["direction"] == "declining" else "➡️"
                    print(f"    {direction_emoji} {trend['type']}: {trend['direction']} (valor atual: {trend['current_value']:.2f})")
            
            # Insights
            insights = feedback_analytics.get("insights", [])
            if insights:
                print(f"  💡 Insights de aprendizado:")
                for insight in insights[:3]:
                    print(f"    • {insight['description']}")
            
        except Exception as e:
            print(f"  ❌ Erro ao obter analytics: {e}")
    
    async def demonstrate_export_import(self):
        """Demonstra exportação e importação de dados"""
        print("\n💾 Demonstrando exportação de dados de aprendizado...")
        
        try:
            # Exportar dados
            exported_data = await learning_integration.export_learning_data("json")
            
            # Salvar em arquivo
            filename = f"learning_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(exported_data)
            
            print(f"  ✅ Dados exportados para: {filename}")
            
            # Mostrar estatísticas do export
            data = json.loads(exported_data)
            print(f"  📊 Estatísticas do export:")
            print(f"    • Timestamp: {data.get('export_timestamp', 'N/A')}")
            
            system_status = data.get("system_status", {})
            if system_status:
                learning_metrics = system_status.get("learning_metrics", {})
                print(f"    • Total de eventos: {learning_metrics.get('total_events', 0)}")
                print(f"    • Total de feedback: {learning_metrics.get('total_feedback', 0)}")
                print(f"    • Agentes monitorados: {learning_metrics.get('agents_count', 0)}")
            
        except Exception as e:
            print(f"  ❌ Erro na exportação: {e}")
    
    async def run_complete_demo(self):
        """Executa demonstração completa"""
        print("🎯 DEMONSTRAÇÃO COMPLETA DO SISTEMA DE APRENDIZADO CONTÍNUO CWB HUB")
        print("=" * 70)
        
        try:
            # 1. Inicializar sistema
            await self.initialize_system()
            
            # 2. Simular sessões
            await self.simulate_user_sessions()
            
            # 3. Processar feedback
            await self.process_feedback_samples()
            
            # 4. Analisar padrões
            await self.demonstrate_pattern_analysis()
            
            # 5. Adaptar agentes
            await self.demonstrate_agent_adaptation()
            
            # 6. Mostrar analytics
            await self.show_learning_analytics()
            
            # 7. Exportar dados
            await self.demonstrate_export_import()
            
            print("\n🎉 DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
            print("=" * 70)
            print("✅ Todas as funcionalidades do sistema de aprendizado foram demonstradas")
            print("🧠 O sistema está continuamente aprendendo e melhorando")
            print("📈 Os agentes CWB Hub estão evoluindo baseado no feedback e padrões")
            
        except Exception as e:
            print(f"\n❌ ERRO NA DEMONSTRAÇÃO: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            # Cleanup
            if learning_integration.is_active:
                await learning_integration.shutdown()
            
            if self.orchestrator:
                await self.orchestrator.shutdown()


async def main():
    """Função principal"""
    demo = LearningSystemDemo()
    await demo.run_complete_demo()


if __name__ == "__main__":
    # Executar demonstração
    print("🚀 Iniciando demonstração do Sistema de Aprendizado Contínuo...")
    asyncio.run(main())