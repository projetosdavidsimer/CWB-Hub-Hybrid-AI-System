#!/usr/bin/env python3
"""
Teste do Sistema de Webhooks CWB Hub
Melhoria #3 Fase 2 - Validação do sistema de webhooks
"""

import asyncio
import json
import time
from datetime import datetime
from webhook_manager import (
    WebhookManager, WebhookEvent, 
    register_cwb_webhook, trigger_cwb_event,
    trigger_analysis_started, trigger_analysis_completed
)

class WebhookTester:
    """Testador do sistema de webhooks"""
    
    def __init__(self):
        self.webhook_manager = WebhookManager()
        self.test_results = []
    
    async def test_webhook_registration(self):
        """Testar registro de webhooks"""
        print("🧪 Testando registro de webhooks...")
        
        try:
            # Testar registro válido
            webhook_id = self.webhook_manager.register_webhook(
                "https://httpbin.org/post",
                [WebhookEvent.ANALYSIS_COMPLETED.value],
                secret="test-secret"
            )
            
            assert webhook_id is not None
            assert len(webhook_id) == 16
            
            # Verificar se foi registrado
            webhook = self.webhook_manager.get_webhook(webhook_id)
            assert webhook is not None
            assert webhook.url == "https://httpbin.org/post"
            assert WebhookEvent.ANALYSIS_COMPLETED.value in webhook.events
            
            print(f"✅ Webhook registrado: {webhook_id}")
            
            # Testar URL inválida
            try:
                self.webhook_manager.register_webhook(
                    "invalid-url",
                    [WebhookEvent.ANALYSIS_COMPLETED.value]
                )
                assert False, "Deveria ter falhado com URL inválida"
            except ValueError:
                print("✅ Validação de URL funcionando")
            
            # Testar evento inválido
            try:
                self.webhook_manager.register_webhook(
                    "https://httpbin.org/post",
                    ["invalid.event"]
                )
                assert False, "Deveria ter falhado com evento inválido"
            except ValueError:
                print("✅ Validação de evento funcionando")
            
            self.test_results.append(("Registro de Webhooks", True))
            return webhook_id
            
        except Exception as e:
            print(f"❌ Erro no teste de registro: {e}")
            self.test_results.append(("Registro de Webhooks", False))
            return None
    
    async def test_webhook_delivery(self, webhook_id: str):
        """Testar entrega de webhooks"""
        print("\n🧪 Testando entrega de webhooks...")
        
        try:
            # Disparar evento
            deliveries = await self.webhook_manager.trigger_event(
                WebhookEvent.ANALYSIS_COMPLETED.value,
                {
                    "session_id": "test_session",
                    "analysis": "Teste de análise",
                    "stats": {"collaborations": 5}
                }
            )
            
            assert len(deliveries) == 1
            delivery = deliveries[0]
            
            # Aguardar um pouco para a entrega
            await asyncio.sleep(2)
            
            print(f"✅ Webhook entregue: {delivery.id}")
            print(f"   Status: {delivery.status_code}")
            print(f"   URL: {delivery.url}")
            
            # Verificar se foi bem-sucedido
            if delivery.status_code and delivery.status_code < 400:
                print("✅ Entrega bem-sucedida")
                self.test_results.append(("Entrega de Webhooks", True))
            else:
                print(f"⚠️ Entrega com problemas: {delivery.status_code}")
                self.test_results.append(("Entrega de Webhooks", False))
            
            return delivery
            
        except Exception as e:
            print(f"❌ Erro no teste de entrega: {e}")
            self.test_results.append(("Entrega de Webhooks", False))
            return None
    
    async def test_webhook_signature(self):
        """Testar assinatura de webhooks"""
        print("\n🧪 Testando assinatura de webhooks...")
        
        try:
            # Registrar webhook com secret
            webhook_id = self.webhook_manager.register_webhook(
                "https://httpbin.org/post",
                [WebhookEvent.ANALYSIS_STARTED.value],
                secret="super-secret-key"
            )
            
            # Disparar evento
            deliveries = await self.webhook_manager.trigger_event(
                WebhookEvent.ANALYSIS_STARTED.value,
                {"session_id": "test_signature", "request": "Teste"}
            )
            
            assert len(deliveries) == 1
            delivery = deliveries[0]
            
            # Verificar se a assinatura foi gerada
            webhook = self.webhook_manager.get_webhook(webhook_id)
            assert webhook.secret == "super-secret-key"
            
            print("✅ Webhook com assinatura criado")
            print(f"   Delivery ID: {delivery.id}")
            
            self.test_results.append(("Assinatura de Webhooks", True))
            return True
            
        except Exception as e:
            print(f"❌ Erro no teste de assinatura: {e}")
            self.test_results.append(("Assinatura de Webhooks", False))
            return False
    
    async def test_webhook_retry(self):
        """Testar retry de webhooks"""
        print("\n🧪 Testando retry de webhooks...")
        
        try:
            # Registrar webhook para URL que vai falhar
            webhook_id = self.webhook_manager.register_webhook(
                "https://httpbin.org/status/500",  # Sempre retorna 500
                [WebhookEvent.SYSTEM_HEALTH.value]
            )
            
            # Configurar retry count baixo para teste rápido
            webhook = self.webhook_manager.get_webhook(webhook_id)
            webhook.retry_count = 2
            
            # Disparar evento
            start_time = time.time()
            deliveries = await self.webhook_manager.trigger_event(
                WebhookEvent.SYSTEM_HEALTH.value,
                {"status": "testing_retry"}
            )
            end_time = time.time()
            
            assert len(deliveries) == 1
            delivery = deliveries[0]
            
            # Verificar se tentou múltiplas vezes
            assert delivery.attempt == 2  # Deveria ter tentado 2 vezes
            assert delivery.status_code == 500
            assert end_time - start_time > 2  # Deveria ter demorado pelo backoff
            
            print(f"✅ Retry funcionando: {delivery.attempt} tentativas")
            print(f"   Tempo total: {end_time - start_time:.2f}s")
            
            self.test_results.append(("Retry de Webhooks", True))
            return True
            
        except Exception as e:
            print(f"❌ Erro no teste de retry: {e}")
            self.test_results.append(("Retry de Webhooks", False))
            return False
    
    async def test_webhook_stats(self, webhook_id: str):
        """Testar estatísticas de webhooks"""
        print("\n🧪 Testando estatísticas de webhooks...")
        
        try:
            # Obter estatísticas
            stats = self.webhook_manager.get_webhook_stats(webhook_id)
            
            assert "webhook_id" in stats
            assert "total_deliveries" in stats
            assert "success_rate" in stats
            
            print("✅ Estatísticas obtidas:")
            print(f"   Total deliveries: {stats['total_deliveries']}")
            print(f"   Success rate: {stats['success_rate']:.1f}%")
            
            self.test_results.append(("Estatísticas de Webhooks", True))
            return stats
            
        except Exception as e:
            print(f"❌ Erro no teste de estatísticas: {e}")
            self.test_results.append(("Estatísticas de Webhooks", False))
            return None
    
    async def test_health_check(self):
        """Testar health check"""
        print("\n🧪 Testando health check...")
        
        try:
            health = await self.webhook_manager.health_check()
            
            assert "status" in health
            assert "webhooks" in health
            assert "deliveries_24h" in health
            
            print("✅ Health check funcionando:")
            print(f"   Status: {health['status']}")
            print(f"   Webhooks ativos: {health['webhooks']['active']}")
            print(f"   Deliveries 24h: {health['deliveries_24h']['total']}")
            
            self.test_results.append(("Health Check", True))
            return health
            
        except Exception as e:
            print(f"❌ Erro no health check: {e}")
            self.test_results.append(("Health Check", False))
            return None
    
    async def test_cwb_events(self):
        """Testar eventos específicos do CWB Hub"""
        print("\n🧪 Testando eventos específicos do CWB Hub...")
        
        try:
            # Registrar webhook para eventos CWB
            webhook_id = await register_cwb_webhook(
                "https://httpbin.org/post",
                [
                    WebhookEvent.ANALYSIS_STARTED.value,
                    WebhookEvent.ANALYSIS_COMPLETED.value,
                    WebhookEvent.ITERATION_COMPLETED.value
                ]
            )
            
            # Testar evento de análise iniciada
            await trigger_analysis_started("test_session", "Teste de projeto")
            
            # Testar evento de análise concluída
            await trigger_analysis_completed(
                "test_session",
                "Análise de teste concluída com sucesso",
                {"collaborations": 8, "confidence": 0.95}
            )
            
            # Aguardar entregas
            await asyncio.sleep(3)
            
            # Verificar deliveries
            deliveries = self.webhook_manager.get_deliveries(webhook_id)
            assert len(deliveries) >= 2
            
            print(f"�� Eventos CWB Hub funcionando: {len(deliveries)} deliveries")
            
            self.test_results.append(("Eventos CWB Hub", True))
            return True
            
        except Exception as e:
            print(f"❌ Erro nos eventos CWB Hub: {e}")
            self.test_results.append(("Eventos CWB Hub", False))
            return False
    
    def print_test_summary(self):
        """Imprimir resumo dos testes"""
        print("\n" + "="*60)
        print("📊 RESUMO DOS TESTES DE WEBHOOKS")
        print("="*60)
        
        passed = 0
        total = len(self.test_results)
        
        for test_name, result in self.test_results:
            status = "✅ PASSOU" if result else "❌ FALHOU"
            print(f"{status} - {test_name}")
            if result:
                passed += 1
        
        print(f"\n🎯 RESULTADO: {passed}/{total} testes passaram ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 TODOS OS TESTES PASSARAM! Sistema de webhooks funcionando perfeitamente!")
        else:
            print("⚠️ Alguns testes falharam. Verifique os logs acima.")
        
        return passed == total
    
    async def run_all_tests(self):
        """Executar todos os testes"""
        print("🧪 INICIANDO TESTES DO SISTEMA DE WEBHOOKS")
        print("=" * 60)
        
        # Teste 1: Registro
        webhook_id = await self.test_webhook_registration()
        
        if webhook_id:
            # Teste 2: Entrega
            await self.test_webhook_delivery(webhook_id)
            
            # Teste 3: Estatísticas
            await self.test_webhook_stats(webhook_id)
        
        # Teste 4: Assinatura
        await self.test_webhook_signature()
        
        # Teste 5: Retry
        await self.test_webhook_retry()
        
        # Teste 6: Health Check
        await self.test_health_check()
        
        # Teste 7: Eventos CWB Hub
        await self.test_cwb_events()
        
        # Resumo
        success = self.print_test_summary()
        
        # Cleanup
        await self.webhook_manager.shutdown()
        
        return success

async def main():
    """Função principal"""
    print("🔗 CWB HUB WEBHOOK SYSTEM - TEST SUITE")
    print("Melhoria #3 Fase 2 - Sistema de Webhooks")
    print()
    
    tester = WebhookTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n🎉 Sistema de webhooks está pronto para uso!")
        print("📚 Documentação: webhook_manager.py")
    else:
        print("\n⚠️ Alguns testes falharam. Verifique a implementação.")

if __name__ == "__main__":
    asyncio.run(main())