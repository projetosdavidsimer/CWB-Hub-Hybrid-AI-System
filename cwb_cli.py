#!/usr/bin/env python3
"""
CWB Hub Hybrid AI System - Command Line Interface
Criado por: David Simer

Interface de linha de comando para interagir com o sistema CWB Hub Hybrid AI.
Permite executar consultas, gerenciar sessões e monitorar o sistema.
"""

import argparse
import asyncio
import json
import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any
import logging

# Adicionar src ao path
sys.path.append(str(Path(__file__).parent / "src"))

try:
    from src.core.hybrid_ai_orchestrator import HybridAIOrchestrator
except ImportError as e:
    print(f"❌ Erro ao importar módulos do sistema: {e}")
    print("💡 Certifique-se de que o sistema está instalado corretamente.")
    print("   Execute: python install_dependencies.py")
    sys.exit(1)


class CWBHubCLI:
    """Interface de linha de comando para o CWB Hub Hybrid AI System"""
    
    def __init__(self):
        self.orchestrator: Optional[HybridAIOrchestrator] = None
        self.current_session_id: Optional[str] = None
        
    async def initialize(self, verbose: bool = False):
        """Inicializa o sistema CWB Hub"""
        if verbose:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        print("🚀 Inicializando CWB Hub Hybrid AI System...")
        self.orchestrator = HybridAIOrchestrator()
        
        try:
            await self.orchestrator.initialize_agents()
            print("✅ Sistema inicializado com sucesso!")
            
            if verbose:
                active_agents = self.orchestrator.get_active_agents()
                print(f"👥 Agentes ativos: {', '.join(active_agents)}")
                
        except Exception as e:
            print(f"❌ Erro ao inicializar sistema: {e}")
            raise
    
    async def process_request(self, request: str, save_session: bool = True) -> str:
        """Processa uma solicitação através da equipe CWB Hub"""
        if not self.orchestrator:
            raise RuntimeError("Sistema não inicializado. Execute 'initialize' primeiro.")
        
        print("🧠 Processando solicitação com a equipe CWB Hub...")
        print("=" * 60)
        
        try:
            response = await self.orchestrator.process_request(request)
            
            if save_session:
                # Obter ID da sessão ativa
                session_ids = list(self.orchestrator.active_sessions.keys())
                if session_ids:
                    self.current_session_id = session_ids[0]
                    print(f"💾 Sessão salva: {self.current_session_id}")
            
            return response
            
        except Exception as e:
            print(f"❌ Erro ao processar solicitação: {e}")
            raise
    
    async def iterate_solution(self, feedback: str, session_id: Optional[str] = None) -> str:
        """Itera uma solução existente com base no feedback"""
        if not self.orchestrator:
            raise RuntimeError("Sistema não inicializado.")
        
        target_session = session_id or self.current_session_id
        if not target_session:
            raise RuntimeError("Nenhuma sessão ativa encontrada.")
        
        print(f"🔄 Iterando solução (Sessão: {target_session})...")
        
        try:
            response = await self.orchestrator.iterate_solution(target_session, feedback)
            return response
            
        except Exception as e:
            print(f"❌ Erro ao iterar solução: {e}")
            raise
    
    async def get_session_status(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Obtém status de uma sessão"""
        if not self.orchestrator:
            raise RuntimeError("Sistema não inicializado.")
        
        target_session = session_id or self.current_session_id
        if not target_session:
            raise RuntimeError("Nenhuma sessão especificada.")
        
        try:
            status = self.orchestrator.get_session_status(target_session)
            return status
            
        except Exception as e:
            print(f"❌ Erro ao obter status da sessão: {e}")
            raise
    
    async def list_sessions(self) -> Dict[str, Any]:
        """Lista todas as sessões ativas"""
        if not self.orchestrator:
            raise RuntimeError("Sistema não inicializado.")
        
        sessions = {}
        for session_id in self.orchestrator.active_sessions.keys():
            try:
                status = self.orchestrator.get_session_status(session_id)
                sessions[session_id] = status
            except:
                sessions[session_id] = {"status": "unknown"}
        
        return sessions
    
    async def get_collaboration_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas de colaboração"""
        if not self.orchestrator:
            raise RuntimeError("Sistema não inicializado.")
        
        try:
            stats = self.orchestrator.collaboration_framework.get_collaboration_stats()
            return stats
        except Exception as e:
            print(f"❌ Erro ao obter estatísticas: {e}")
            raise
    
    async def shutdown(self):
        """Encerra o sistema"""
        if self.orchestrator:
            print("🔚 Encerrando sistema...")
            await self.orchestrator.shutdown()
            print("✅ Sistema encerrado com sucesso!")


async def cmd_query(args):
    """Comando para fazer uma consulta"""
    cli = CWBHubCLI()
    
    try:
        await cli.initialize(verbose=args.verbose)
        
        # Ler solicitação
        if args.request:
            request = args.request
        elif args.file:
            with open(args.file, 'r', encoding='utf-8') as f:
                request = f.read()
        else:
            print("📝 Digite sua solicitação (Ctrl+D para finalizar):")
            request = sys.stdin.read()
        
        if not request.strip():
            print("❌ Solicitação vazia.")
            return
        
        # Processar solicitação
        response = await cli.process_request(request, save_session=not args.no_save)
        
        # Exibir resposta
        print("\n" + "=" * 80)
        print("💡 RESPOSTA DA EQUIPE CWB HUB")
        print("=" * 80)
        print(response)
        
        # Salvar em arquivo se especificado
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(response)
            print(f"\n💾 Resposta salva em: {args.output}")
        
        # Mostrar estatísticas se solicitado
        if args.stats:
            print("\n" + "=" * 80)
            print("📊 ESTATÍSTICAS")
            print("=" * 80)
            
            try:
                stats = await cli.get_collaboration_stats()
                print(json.dumps(stats, indent=2, ensure_ascii=False))
            except:
                print("Estatísticas não disponíveis")
        
    finally:
        await cli.shutdown()


async def cmd_iterate(args):
    """Comando para iterar uma solução"""
    cli = CWBHubCLI()
    
    try:
        await cli.initialize(verbose=args.verbose)
        
        # Ler feedback
        if args.feedback:
            feedback = args.feedback
        elif args.file:
            with open(args.file, 'r', encoding='utf-8') as f:
                feedback = f.read()
        else:
            print("📝 Digite seu feedback (Ctrl+D para finalizar):")
            feedback = sys.stdin.read()
        
        if not feedback.strip():
            print("❌ Feedback vazio.")
            return
        
        # Iterar solução
        response = await cli.iterate_solution(feedback, args.session)
        
        # Exibir resposta
        print("\n" + "=" * 80)
        print("🔄 SOLUÇÃO REFINADA")
        print("=" * 80)
        print(response)
        
        # Salvar em arquivo se especificado
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(response)
            print(f"\n💾 Resposta salva em: {args.output}")
        
    finally:
        await cli.shutdown()


async def cmd_status(args):
    """Comando para verificar status"""
    cli = CWBHubCLI()
    
    try:
        await cli.initialize(verbose=args.verbose)
        
        if args.session:
            # Status de sessão específica
            status = await cli.get_session_status(args.session)
            print(f"📊 Status da Sessão: {args.session}")
            print("=" * 50)
            print(json.dumps(status, indent=2, ensure_ascii=False))
            
        else:
            # Listar todas as sessões
            sessions = await cli.list_sessions()
            
            if not sessions:
                print("📭 Nenhuma sessão ativa encontrada.")
            else:
                print("📋 SESSÕES ATIVAS")
                print("=" * 50)
                for session_id, status in sessions.items():
                    print(f"🔹 {session_id}: {status}")
        
        # Estatísticas de colaboração
        if args.collaboration:
            print("\n📊 ESTATÍSTICAS DE COLABORAÇÃO")
            print("=" * 50)
            try:
                stats = await cli.get_collaboration_stats()
                print(json.dumps(stats, indent=2, ensure_ascii=False))
            except:
                print("Estatísticas não disponíveis")
        
    finally:
        await cli.shutdown()


async def cmd_agents(args):
    """Comando para listar agentes"""
    cli = CWBHubCLI()
    
    try:
        await cli.initialize(verbose=args.verbose)
        
        active_agents = cli.orchestrator.get_active_agents()
        
        print("👥 AGENTES ATIVOS DA EQUIPE CWB HUB")
        print("=" * 50)
        
        agent_descriptions = {
            "Ana Beatriz Costa": "👩‍💼 CTO - Estratégia e Inovação",
            "Carlos Eduardo Santos": "👨‍💻 Arquiteto de Software Sênior",
            "Sofia Oliveira": "👩‍💻 Engenheira Full Stack",
            "Gabriel Mendes": "👨‍📱 Engenheiro Mobile",
            "Isabella Santos": "👩‍🎨 Designer UX/UI Sênior",
            "Lucas Pereira": "👨‍🔬 Engenheiro de QA",
            "Mariana Rodrigues": "👩‍🔧 Engenheira DevOps",
            "Pedro Henrique Almeida": "👨‍📊 Agile Project Manager"
        }
        
        for agent in active_agents:
            description = agent_descriptions.get(agent, f"🤖 {agent}")
            print(f"✅ {description}")
        
        print(f"\n📊 Total de agentes ativos: {len(active_agents)}")
        
    finally:
        await cli.shutdown()


def main():
    """Função principal do CLI"""
    parser = argparse.ArgumentParser(
        description="CWB Hub Hybrid AI System - Interface de Linha de Comando",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:

  # Fazer uma consulta simples
  python cwb_cli.py query "Como criar um app mobile?"
  
  # Consulta a partir de arquivo
  python cwb_cli.py query --file requisitos.txt --output resposta.md
  
  # Iterar uma solução existente
  python cwb_cli.py iterate "Preciso reduzir o orçamento" --session abc123
  
  # Verificar status das sessões
  python cwb_cli.py status
  
  # Listar agentes ativos
  python cwb_cli.py agents
  
  # Consulta com estatísticas detalhadas
  python cwb_cli.py query "Desenvolver API REST" --stats --verbose

Criado por David Simer - CWB Hub Hybrid AI System
        """
    )
    
    # Argumentos globais
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Modo verboso com logs detalhados')
    
    # Subcomandos
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponíveis')
    
    # Comando query
    query_parser = subparsers.add_parser('query', help='Fazer uma consulta à equipe CWB Hub')
    query_parser.add_argument('request', nargs='?', help='Texto da solicitação')
    query_parser.add_argument('--file', '-f', help='Arquivo com a solicitação')
    query_parser.add_argument('--output', '-o', help='Arquivo para salvar a resposta')
    query_parser.add_argument('--no-save', action='store_true', help='Não salvar sessão')
    query_parser.add_argument('--stats', action='store_true', help='Mostrar estatísticas')
    query_parser.set_defaults(func=cmd_query)
    
    # Comando iterate
    iterate_parser = subparsers.add_parser('iterate', help='Iterar uma solução existente')
    iterate_parser.add_argument('feedback', nargs='?', help='Feedback para iteração')
    iterate_parser.add_argument('--file', '-f', help='Arquivo com o feedback')
    iterate_parser.add_argument('--session', '-s', help='ID da sessão (usa a última se não especificado)')
    iterate_parser.add_argument('--output', '-o', help='Arquivo para salvar a resposta')
    iterate_parser.set_defaults(func=cmd_iterate)
    
    # Comando status
    status_parser = subparsers.add_parser('status', help='Verificar status das sessões')
    status_parser.add_argument('--session', '-s', help='ID de sessão específica')
    status_parser.add_argument('--collaboration', '-c', action='store_true',
                              help='Mostrar estatísticas de colaboração')
    status_parser.set_defaults(func=cmd_status)
    
    # Comando agents
    agents_parser = subparsers.add_parser('agents', help='Listar agentes ativos')
    agents_parser.set_defaults(func=cmd_agents)
    
    # Parse argumentos
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Configurar encoding para Windows
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    
    # Executar comando
    try:
        asyncio.run(args.func(args))
    except KeyboardInterrupt:
        print("\n⚠️ Operação interrompida pelo usuário")
    except Exception as e:
        print(f"❌ Erro: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()