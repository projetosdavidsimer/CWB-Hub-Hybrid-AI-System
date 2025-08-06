#!/usr/bin/env python3
"""
Teste de Validação Completa do Sistema CWB Hub Hybrid AI
Executa testes abrangentes com diferentes tipos de solicitações
"""

import asyncio
import logging
import time
from typing import List, Dict, Any

# Configurar logging para os testes
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class SystemValidator:
    """Validador completo do sistema CWB Hub"""
    
    def __init__(self):
        self.test_results = []
        self.orchestrator = None
        
    async def initialize_system(self):
        """Inicializa o sistema para testes"""
        try:
            from src.core.hybrid_ai_orchestrator import HybridAIOrchestrator
            
            print("🔧 Inicializando sistema CWB Hub...")
            self.orchestrator = HybridAIOrchestrator()
            await self.orchestrator.initialize_agents()
            
            print("✅ Sistema inicializado com sucesso!")
            print(f"👥 Agentes ativos: {len(self.orchestrator.get_active_agents())}")
            return True
            
        except Exception as e:
            print(f"❌ Erro na inicialização: {e}")
            return False
    
    async def test_strategic_request(self):
        """Testa solicitação estratégica (CTO focus)"""
        print("\n" + "="*60)
        print("🎯 TESTE 1: Solicitação Estratégica")
        print("="*60)
        
        request = """
        Nossa empresa precisa definir a estratégia tecnológica para os próximos 3 anos.
        Queremos focar em inovação, escalabilidade e competitividade no mercado.
        Como devemos proceder considerando tendências de IA, cloud computing e 
        transformação digital?
        """
        
        start_time = time.time()
        try:
            response = await self.orchestrator.process_request(request.strip())
            end_time = time.time()
            
            # Validações
            assert response is not None, "Resposta não pode ser None"
            assert len(response) > 100, "Resposta muito curta"
            assert "CTO" in response or "estratégia" in response.lower(), "Deve mencionar estratégia"
            
            print(f"✅ Teste estratégico passou!")
            print(f"⏱️ Tempo de resposta: {end_time - start_time:.2f}s")
            print(f"📝 Tamanho da resposta: {len(response)} caracteres")
            
            self.test_results.append({
                "test": "Strategic Request",
                "status": "PASS",
                "time": end_time - start_time,
                "response_length": len(response)
            })
            
            return True
            
        except Exception as e:
            print(f"❌ Teste estratégico falhou: {e}")
            self.test_results.append({
                "test": "Strategic Request", 
                "status": "FAIL",
                "error": str(e)
            })
            return False
    
    async def test_technical_request(self):
        """Testa solicitação técnica (Arquiteto + Full Stack focus)"""
        print("\n" + "="*60)
        print("🏗️ TESTE 2: Solicitação Técnica")
        print("="*60)
        
        request = """
        Preciso desenvolver uma API REST para um sistema de e-commerce que suporte:
        - Autenticação JWT
        - Catálogo de produtos com busca
        - Carrinho de compras
        - Processamento de pagamentos
        - Notificações em tempo real
        
        A API deve ser escalável, segura e ter alta performance.
        """
        
        start_time = time.time()
        try:
            response = await self.orchestrator.process_request(request.strip())
            end_time = time.time()
            
            # Validações
            assert response is not None, "Resposta não pode ser None"
            assert len(response) > 200, "Resposta muito curta para solicitação técnica"
            assert any(word in response.lower() for word in ["api", "arquitetura", "implementação"]), "Deve mencionar aspectos técnicos"
            
            print(f"✅ Teste técnico passou!")
            print(f"⏱️ Tempo de resposta: {end_time - start_time:.2f}s")
            print(f"📝 Tamanho da resposta: {len(response)} caracteres")
            
            self.test_results.append({
                "test": "Technical Request",
                "status": "PASS", 
                "time": end_time - start_time,
                "response_length": len(response)
            })
            
            return True
            
        except Exception as e:
            print(f"❌ Teste técnico falhou: {e}")
            self.test_results.append({
                "test": "Technical Request",
                "status": "FAIL",
                "error": str(e)
            })
            return False
    
    async def test_mobile_design_request(self):
        """Testa solicitação mobile + design (Mobile + UX/UI focus)"""
        print("\n" + "="*60)
        print("📱 TESTE 3: Solicitação Mobile + Design")
        print("="*60)
        
        request = """
        Quero criar um aplicativo mobile para delivery de comida com:
        - Interface intuitiva e atrativa
        - Experiência de usuário excepcional
        - Funcionalidade offline
        - Geolocalização
        - Pagamento integrado
        - Push notifications
        
        O app deve funcionar bem em iOS e Android.
        """
        
        start_time = time.time()
        try:
            response = await self.orchestrator.process_request(request.strip())
            end_time = time.time()
            
            # Validações
            assert response is not None, "Resposta não pode ser None"
            assert len(response) > 150, "Resposta muito curta"
            assert any(word in response.lower() for word in ["mobile", "ux", "ui", "design", "usuário"]), "Deve mencionar aspectos mobile/design"
            
            print(f"✅ Teste mobile+design passou!")
            print(f"⏱️ Tempo de resposta: {end_time - start_time:.2f}s")
            print(f"📝 Tamanho da resposta: {len(response)} caracteres")
            
            self.test_results.append({
                "test": "Mobile + Design Request",
                "status": "PASS",
                "time": end_time - start_time,
                "response_length": len(response)
            })
            
            return True
            
        except Exception as e:
            print(f"❌ Teste mobile+design falhou: {e}")
            self.test_results.append({
                "test": "Mobile + Design Request",
                "status": "FAIL", 
                "error": str(e)
            })
            return False
    
    async def test_devops_quality_request(self):
        """Testa solicitação DevOps + QA (DevOps + QA focus)"""
        print("\n" + "="*60)
        print("🔧 TESTE 4: Solicitação DevOps + Qualidade")
        print("="*60)
        
        request = """
        Preciso configurar um pipeline de CI/CD completo para nossa aplicação web:
        - Testes automatizados
        - Deploy automatizado
        - Monitoramento de qualidade
        - Infraestrutura como código
        - Segurança integrada
        - Rollback automático
        
        Tudo deve rodar na AWS com alta disponibilidade.
        """
        
        start_time = time.time()
        try:
            response = await self.orchestrator.process_request(request.strip())
            end_time = time.time()
            
            # Validações
            assert response is not None, "Resposta não pode ser None"
            assert len(response) > 150, "Resposta muito curta"
            assert any(word in response.lower() for word in ["devops", "ci/cd", "testes", "qualidade", "infraestrutura"]), "Deve mencionar aspectos DevOps/QA"
            
            print(f"✅ Teste DevOps+QA passou!")
            print(f"⏱️ Tempo de resposta: {end_time - start_time:.2f}s")
            print(f"📝 Tamanho da resposta: {len(response)} caracteres")
            
            self.test_results.append({
                "test": "DevOps + QA Request",
                "status": "PASS",
                "time": end_time - start_time,
                "response_length": len(response)
            })
            
            return True
            
        except Exception as e:
            print(f"❌ Teste DevOps+QA falhou: {e}")
            self.test_results.append({
                "test": "DevOps + QA Request",
                "status": "FAIL",
                "error": str(e)
            })
            return False
    
    async def test_project_management_request(self):
        """Testa solicitação de gestão de projeto (PM focus)"""
        print("\n" + "="*60)
        print("📊 TESTE 5: Solicitação de Gestão de Projeto")
        print("="*60)
        
        request = """
        Preciso planejar um projeto de desenvolvimento de software com:
        - Equipe de 8 pessoas
        - Prazo de 6 meses
        - Orçamento limitado
        - Metodologia ágil
        - Entregas incrementais
        - Gestão de riscos
        
        Como organizar e executar este projeto com sucesso?
        """
        
        start_time = time.time()
        try:
            response = await self.orchestrator.process_request(request.strip())
            end_time = time.time()
            
            # Validações
            assert response is not None, "Resposta não pode ser None"
            assert len(response) > 150, "Resposta muito curta"
            assert any(word in response.lower() for word in ["projeto", "agile", "scrum", "planejamento", "gestão"]), "Deve mencionar aspectos de gestão"
            
            print(f"✅ Teste gestão de projeto passou!")
            print(f"⏱️ Tempo de resposta: {end_time - start_time:.2f}s")
            print(f"📝 Tamanho da resposta: {len(response)} caracteres")
            
            self.test_results.append({
                "test": "Project Management Request",
                "status": "PASS",
                "time": end_time - start_time,
                "response_length": len(response)
            })
            
            return True
            
        except Exception as e:
            print(f"❌ Teste gestão de projeto falhou: {e}")
            self.test_results.append({
                "test": "Project Management Request",
                "status": "FAIL",
                "error": str(e)
            })
            return False
    
    async def test_iteration_functionality(self):
        """Testa funcionalidade de iteração"""
        print("\n" + "="*60)
        print("🔄 TESTE 6: Funcionalidade de Iteração")
        print("="*60)
        
        # Primeira solicitação
        initial_request = "Quero criar um site simples para minha empresa."
        
        try:
            print("📝 Processando solicitação inicial...")
            initial_response = await self.orchestrator.process_request(initial_request)
            
            # Obter sessão ativa
            sessions = list(self.orchestrator.active_sessions.keys())
            assert len(sessions) > 0, "Deve ter pelo menos uma sessão ativa"
            
            session_id = sessions[0]
            print(f"🔍 Sessão ativa: {session_id}")
            
            # Feedback para iteração
            feedback = """
            Gostei da proposta inicial, mas preciso de mais detalhes sobre:
            - Tecnologias específicas a usar
            - Cronograma de desenvolvimento
            - Orçamento estimado
            - Funcionalidades prioritárias
            """
            
            print("🔄 Processando iteração com feedback...")
            start_time = time.time()
            refined_response = await self.orchestrator.iterate_solution(session_id, feedback)
            end_time = time.time()
            
            # Validações
            assert refined_response is not None, "Resposta refinada não pode ser None"
            assert len(refined_response) > 100, "Resposta refinada muito curta"
            assert refined_response != initial_response, "Resposta refinada deve ser diferente da inicial"
            
            # Verificar se iteração foi registrada
            session_status = self.orchestrator.get_session_status(session_id)
            assert session_status["iterations"] > 0, "Deve ter pelo menos uma iteração"
            
            print(f"✅ Teste de iteração passou!")
            print(f"⏱️ Tempo de iteração: {end_time - start_time:.2f}s")
            print(f"🔢 Iterações registradas: {session_status['iterations']}")
            
            self.test_results.append({
                "test": "Iteration Functionality",
                "status": "PASS",
                "time": end_time - start_time,
                "iterations": session_status["iterations"]
            })
            
            return True
            
        except Exception as e:
            print(f"❌ Teste de iteração falhou: {e}")
            self.test_results.append({
                "test": "Iteration Functionality",
                "status": "FAIL",
                "error": str(e)
            })
            return False
    
    async def test_collaboration_metrics(self):
        """Testa métricas de colaboração"""
        print("\n" + "="*60)
        print("📊 TESTE 7: Métricas de Colaboração")
        print("="*60)
        
        try:
            # Obter estatísticas de colaboração
            stats = self.orchestrator.collaboration_framework.get_collaboration_stats()
            
            print(f"📈 Estatísticas de colaboração:")
            print(f"   Total de colaborações: {stats.get('total_collaborations', 0)}")
            print(f"   Agentes participantes: {len(stats.get('agent_stats', {}))}")
            
            # Validações básicas
            assert isinstance(stats, dict), "Estatísticas devem ser um dicionário"
            assert "total_collaborations" in stats, "Deve ter total de colaborações"
            
            print(f"✅ Teste de métricas passou!")
            
            self.test_results.append({
                "test": "Collaboration Metrics",
                "status": "PASS",
                "total_collaborations": stats.get('total_collaborations', 0)
            })
            
            return True
            
        except Exception as e:
            print(f"❌ Teste de métricas falhou: {e}")
            self.test_results.append({
                "test": "Collaboration Metrics",
                "status": "FAIL",
                "error": str(e)
            })
            return False
    
    async def test_agent_individual_functionality(self):
        """Testa funcionalidade individual dos agentes"""
        print("\n" + "="*60)
        print("👥 TESTE 8: Funcionalidade Individual dos Agentes")
        print("="*60)
        
        try:
            agents = self.orchestrator.get_active_agents()
            print(f"🔍 Testando {len(agents)} agentes...")
            
            for agent_id in agents[:3]:  # Testar apenas 3 agentes para economizar tempo
                agent = self.orchestrator.agents[agent_id]
                
                # Testar análise individual
                test_request = "Desenvolver uma funcionalidade de login"
                analysis = await agent.analyze_request(test_request)
                
                assert analysis is not None, f"Análise do {agent_id} não pode ser None"
                assert len(analysis) > 50, f"Análise do {agent_id} muito curta"
                
                # Testar informações do agente
                agent_info = agent.get_agent_info()
                assert "profile" in agent_info, f"Info do {agent_id} deve ter profile"
                assert "status" in agent_info, f"Info do {agent_id} deve ter status"
                
                print(f"   ✅ {agent.profile.name} - OK")
            
            print(f"✅ Teste de agentes individuais passou!")
            
            self.test_results.append({
                "test": "Individual Agent Functionality",
                "status": "PASS",
                "agents_tested": len(agents)
            })
            
            return True
            
        except Exception as e:
            print(f"❌ Teste de agentes individuais falhou: {e}")
            self.test_results.append({
                "test": "Individual Agent Functionality",
                "status": "FAIL",
                "error": str(e)
            })
            return False
    
    async def cleanup_system(self):
        """Limpa o sistema após os testes"""
        try:
            if self.orchestrator:
                await self.orchestrator.shutdown()
                print("🧹 Sistema limpo com sucesso!")
            return True
        except Exception as e:
            print(f"⚠️ Erro na limpeza: {e}")
            return False
    
    def print_final_report(self):
        """Imprime relatório final dos testes"""
        print("\n" + "="*80)
        print("📋 RELATÓRIO FINAL DE VALIDAÇÃO")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        failed_tests = total_tests - passed_tests
        
        print(f"📊 Resumo dos Testes:")
        print(f"   Total: {total_tests}")
        print(f"   ✅ Passou: {passed_tests}")
        print(f"   ❌ Falhou: {failed_tests}")
        print(f"   📈 Taxa de Sucesso: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests == 0:
            print("\n🎉 TODOS OS TESTES PASSARAM!")
            print("✅ Sistema CWB Hub Hybrid AI está 100% funcional!")
        else:
            print(f"\n⚠️ {failed_tests} teste(s) falharam:")
            for result in self.test_results:
                if result["status"] == "FAIL":
                    print(f"   ❌ {result['test']}: {result.get('error', 'Erro desconhecido')}")
        
        # Métricas de performance
        times = [r.get("time", 0) for r in self.test_results if "time" in r]
        if times:
            avg_time = sum(times) / len(times)
            print(f"\n⏱️ Performance:")
            print(f"   Tempo médio de resposta: {avg_time:.2f}s")
            print(f"   Tempo total de testes: {sum(times):.2f}s")
        
        return failed_tests == 0

async def main():
    """Função principal de validação"""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                    CWB HUB HYBRID AI                         ║
    ║                  VALIDAÇÃO COMPLETA                          ║
    ║                                                              ║
    ║  Testando todas as funcionalidades do sistema               ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    validator = SystemValidator()
    
    try:
        # Inicializar sistema
        if not await validator.initialize_system():
            print("❌ Falha na inicialização. Abortando testes.")
            return False
        
        # Executar todos os testes
        tests = [
            validator.test_strategic_request,
            validator.test_technical_request,
            validator.test_mobile_design_request,
            validator.test_devops_quality_request,
            validator.test_project_management_request,
            validator.test_iteration_functionality,
            validator.test_collaboration_metrics,
            validator.test_agent_individual_functionality
        ]
        
        print(f"\n🚀 Executando {len(tests)} testes de validação...")
        
        for i, test in enumerate(tests, 1):
            print(f"\n📋 Progresso: {i}/{len(tests)}")
            await test()
            
            # Pequena pausa entre testes
            await asyncio.sleep(0.5)
        
        # Relatório final
        success = validator.print_final_report()
        
        return success
        
    except Exception as e:
        print(f"❌ Erro crítico durante validação: {e}")
        return False
        
    finally:
        # Sempre limpar o sistema
        await validator.cleanup_system()

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        if success:
            print("\n🎉 VALIDAÇÃO COMPLETA: Sistema aprovado!")
            exit(0)
        else:
            print("\n❌ VALIDAÇÃO FALHOU: Verificar erros acima.")
            exit(1)
    except KeyboardInterrupt:
        print("\n⚠️ Validação interrompida pelo usuário.")
        exit(1)
    except Exception as e:
        print(f"\n💥 Erro fatal na validação: {e}")
        exit(1)