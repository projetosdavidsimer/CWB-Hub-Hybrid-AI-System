"""
Email Distributor - Sistema de Distribuição de Relatórios por Email
Criado pela Equipe Híbrida CWB Hub

Mariana Rodrigues (DevOps): "Sistema robusto de distribuição automática 
de relatórios com suporte a múltiplos destinatários e formatos."
"""

import asyncio
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path
import os

logger = logging.getLogger(__name__)


class EmailDistributor:
    """
    Distribuidor de relatórios por email
    
    Responsabilidades:
    - Enviar relatórios por email
    - Suportar múltiplos destinatários
    - Anexar arquivos de relatórios
    - Configurar templates de email
    """
    
    def __init__(
        self,
        smtp_server: Optional[str] = None,
        smtp_port: Optional[int] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        use_tls: bool = True
    ):
        # Configurações SMTP (com fallback para variáveis de ambiente)
        self.smtp_server = smtp_server or os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = smtp_port or int(os.getenv('SMTP_PORT', '587'))
        self.username = username or os.getenv('SMTP_USERNAME', '')
        self.password = password or os.getenv('SMTP_PASSWORD', '')
        self.use_tls = use_tls
        
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Templates de email
        self.email_templates = self._load_email_templates()
    
    async def send_report(
        self,
        recipients: List[str],
        report_files: List[Path],
        report_type: str,
        subject: Optional[str] = None,
        body: Optional[str] = None,
        execution_id: Optional[str] = None
    ) -> bool:
        """
        Envia relatório por email
        
        Args:
            recipients: Lista de emails destinatários
            report_files: Lista de arquivos do relatório
            report_type: Tipo do relatório
            subject: Assunto customizado
            body: Corpo customizado do email
            execution_id: ID da execução
            
        Returns:
            True se enviado com sucesso
        """
        try:
            if not recipients:
                self.logger.warning("Nenhum destinatário especificado")
                return False
            
            if not self._validate_smtp_config():
                self.logger.error("Configuração SMTP inválida")
                return False
            
            # Preparar email
            msg = self._prepare_email(
                recipients=recipients,
                report_files=report_files,
                report_type=report_type,
                subject=subject,
                body=body,
                execution_id=execution_id
            )
            
            if not msg:
                return False
            
            # Enviar email
            success = await self._send_email(msg, recipients)
            
            if success:
                self.logger.info(f"Relatório enviado por email para {len(recipients)} destinatários")
            else:
                self.logger.error("Falha no envio do email")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Erro ao enviar relatório por email: {e}")
            return False
    
    def _validate_smtp_config(self) -> bool:
        """Valida configuração SMTP"""
        if not self.smtp_server:
            self.logger.error("Servidor SMTP não configurado")
            return False
        
        if not self.username:
            self.logger.warning("Usuário SMTP não configurado")
            # Pode funcionar sem autenticação em alguns casos
        
        return True
    
    def _prepare_email(
        self,
        recipients: List[str],
        report_files: List[Path],
        report_type: str,
        subject: Optional[str] = None,
        body: Optional[str] = None,
        execution_id: Optional[str] = None
    ) -> Optional[MIMEMultipart]:
        """Prepara o email com anexos"""
        try:
            # Criar mensagem
            msg = MIMEMultipart()\n            msg['From'] = self.username or 'noreply@cwbhub.com'\n            msg['To'] = ', '.join(recipients)\n            \n            # Assunto\n            if not subject:\n                subject = self._generate_subject(report_type, execution_id)\n            msg['Subject'] = subject\n            \n            # Corpo do email\n            if not body:\n                body = self._generate_body(report_type, report_files, execution_id)\n            \n            msg.attach(MIMEText(body, 'html', 'utf-8'))\n            \n            # Anexar arquivos\n            for file_path in report_files:\n                if file_path.exists():\n                    self._attach_file(msg, file_path)\n                else:\n                    self.logger.warning(f\"Arquivo não encontrado: {file_path}\")\n            \n            return msg\n            \n        except Exception as e:\n            self.logger.error(f\"Erro ao preparar email: {e}\")\n            return None\n    \n    def _attach_file(self, msg: MIMEMultipart, file_path: Path):\n        \"\"\"Anexa arquivo ao email\"\"\"\n        try:\n            with open(file_path, 'rb') as attachment:\n                part = MIMEBase('application', 'octet-stream')\n                part.set_payload(attachment.read())\n            \n            encoders.encode_base64(part)\n            \n            # Determinar tipo de conteúdo baseado na extensão\n            content_type = self._get_content_type(file_path.suffix)\n            \n            part.add_header(\n                'Content-Disposition',\n                f'attachment; filename= {file_path.name}'\n            )\n            \n            if content_type:\n                part.add_header('Content-Type', content_type)\n            \n            msg.attach(part)\n            \n        except Exception as e:\n            self.logger.error(f\"Erro ao anexar arquivo {file_path}: {e}\")\n    \n    def _get_content_type(self, extension: str) -> str:\n        \"\"\"Determina tipo de conteúdo baseado na extensão\"\"\"\n        content_types = {\n            '.pdf': 'application/pdf',\n            '.html': 'text/html',\n            '.json': 'application/json',\n            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',\n            '.csv': 'text/csv'\n        }\n        return content_types.get(extension.lower(), 'application/octet-stream')\n    \n    def _generate_subject(self, report_type: str, execution_id: Optional[str] = None) -> str:\n        \"\"\"Gera assunto do email\"\"\"\n        timestamp = datetime.now().strftime('%d/%m/%Y às %H:%M')\n        \n        subject_map = {\n            'executive_summary': 'Relatório Executivo CWB Hub',\n            'agent_performance': 'Relatório de Performance dos Agentes',\n            'collaboration_stats': 'Estatísticas de Colaboração',\n            'system_usage': 'Relatório de Uso do Sistema',\n            'quality_analysis': 'Análise de Qualidade'\n        }\n        \n        base_subject = subject_map.get(report_type, f'Relatório {report_type.title()}')\n        \n        return f\"{base_subject} - {timestamp}\"\n    \n    def _generate_body(self, report_type: str, report_files: List[Path], execution_id: Optional[str] = None) -> str:\n        \"\"\"Gera corpo do email\"\"\"\n        template = self.email_templates.get(report_type, self.email_templates['default'])\n        \n        # Preparar dados para o template\n        file_list = \"\\n\".join([\n            f\"<li>{file_path.name} ({self._format_file_size(file_path)})</li>\"\n            for file_path in report_files if file_path.exists()\n        ])\n        \n        return template.format(\n            report_type=report_type.replace('_', ' ').title(),\n            timestamp=datetime.now().strftime('%d/%m/%Y às %H:%M:%S'),\n            file_count=len(report_files),\n            file_list=file_list,\n            execution_id=execution_id or 'N/A',\n            system_name='CWB Hub Hybrid AI System'\n        )\n    \n    def _format_file_size(self, file_path: Path) -> str:\n        \"\"\"Formata tamanho do arquivo\"\"\"\n        try:\n            size_bytes = file_path.stat().st_size\n            \n            if size_bytes < 1024:\n                return f\"{size_bytes} bytes\"\n            elif size_bytes < 1024 * 1024:\n                return f\"{size_bytes / 1024:.1f} KB\"\n            else:\n                return f\"{size_bytes / (1024 * 1024):.1f} MB\"\n        except:\n            return \"Tamanho desconhecido\"\n    \n    async def _send_email(self, msg: MIMEMultipart, recipients: List[str]) -> bool:\n        \"\"\"Envia o email via SMTP\"\"\"\n        try:\n            # Usar asyncio para não bloquear\n            loop = asyncio.get_event_loop()\n            \n            def send_sync():\n                server = smtplib.SMTP(self.smtp_server, self.smtp_port)\n                \n                if self.use_tls:\n                    server.starttls()\n                \n                if self.username and self.password:\n                    server.login(self.username, self.password)\n                \n                text = msg.as_string()\n                server.sendmail(msg['From'], recipients, text)\n                server.quit()\n                \n                return True\n            \n            # Executar em thread separada\n            result = await loop.run_in_executor(None, send_sync)\n            return result\n            \n        except smtplib.SMTPAuthenticationError:\n            self.logger.error(\"Erro de autenticação SMTP - verifique usuário e senha\")\n            return False\n        except smtplib.SMTPConnectError:\n            self.logger.error(f\"Erro de conexão SMTP - verifique servidor {self.smtp_server}:{self.smtp_port}\")\n            return False\n        except smtplib.SMTPException as e:\n            self.logger.error(f\"Erro SMTP: {e}\")\n            return False\n        except Exception as e:\n            self.logger.error(f\"Erro inesperado ao enviar email: {e}\")\n            return False\n    \n    def _load_email_templates(self) -> Dict[str, str]:\n        \"\"\"Carrega templates de email\"\"\"\n        return {\n            'default': \"\"\"\n            <html>\n            <head>\n                <style>\n                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}\n                    .header {{ background: #1976D2; color: white; padding: 20px; text-align: center; }}\n                    .content {{ padding: 20px; }}\n                    .file-list {{ background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 15px 0; }}\n                    .footer {{ background: #f0f0f0; padding: 15px; text-align: center; font-size: 12px; color: #666; }}\n                </style>\n            </head>\n            <body>\n                <div class=\"header\">\n                    <h1>{system_name}</h1>\n                    <p>Relatório Automatizado</p>\n                </div>\n                \n                <div class=\"content\">\n                    <h2>{report_type}</h2>\n                    <p>Relatório gerado automaticamente em {timestamp}.</p>\n                    \n                    <div class=\"file-list\">\n                        <h3>Arquivos Anexos ({file_count}):</h3>\n                        <ul>\n                            {file_list}\n                        </ul>\n                    </div>\n                    \n                    <p>Este relatório contém informações importantes sobre o desempenho e status do sistema.</p>\n                    \n                    <p><strong>ID da Execução:</strong> {execution_id}</p>\n                </div>\n                \n                <div class=\"footer\">\n                    <p>Este é um email automático do Sistema de Relatórios CWB Hub.</p>\n                    <p>Para dúvidas ou suporte, entre em contato com a equipe técnica.</p>\n                </div>\n            </body>\n            </html>\n            \"\"\",\n            \n            'executive_summary': \"\"\"\n            <html>\n            <head>\n                <style>\n                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}\n                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; }}\n                    .content {{ padding: 20px; }}\n                    .highlight {{ background: #e3f2fd; padding: 15px; border-left: 4px solid #2196F3; margin: 15px 0; }}\n                    .file-list {{ background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 15px 0; }}\n                    .footer {{ background: #f0f0f0; padding: 15px; text-align: center; font-size: 12px; color: #666; }}\n                </style>\n            </head>\n            <body>\n                <div class=\"header\">\n                    <h1>📊 Relatório Executivo</h1>\n                    <p>{system_name}</p>\n                </div>\n                \n                <div class=\"content\">\n                    <div class=\"highlight\">\n                        <h2>Resumo Executivo Disponível</h2>\n                        <p>O relatório executivo do período foi gerado com sucesso em {timestamp}.</p>\n                    </div>\n                    \n                    <p>Este relatório contém:</p>\n                    <ul>\n                        <li>📈 Métricas de performance do sistema</li>\n                        <li>👥 Estatísticas dos agentes especializados</li>\n                        <li>🤝 Análise de colaboração</li>\n                        <li>📊 Indicadores de qualidade</li>\n                    </ul>\n                    \n                    <div class=\"file-list\">\n                        <h3>Arquivos do Relatório ({file_count}):</h3>\n                        <ul>\n                            {file_list}\n                        </ul>\n                    </div>\n                    \n                    <p><strong>ID da Execução:</strong> {execution_id}</p>\n                </div>\n                \n                <div class=\"footer\">\n                    <p>Relatório gerado automaticamente pelo Sistema CWB Hub</p>\n                </div>\n            </body>\n            </html>\n            \"\"\"\n        }\n    \n    def test_connection(self) -> bool:\n        \"\"\"Testa conexão SMTP\"\"\"\n        try:\n            server = smtplib.SMTP(self.smtp_server, self.smtp_port)\n            \n            if self.use_tls:\n                server.starttls()\n            \n            if self.username and self.password:\n                server.login(self.username, self.password)\n            \n            server.quit()\n            \n            self.logger.info(\"Teste de conexão SMTP bem-sucedido\")\n            return True\n            \n        except Exception as e:\n            self.logger.error(f\"Falha no teste de conexão SMTP: {e}\")\n            return False\n    \n    def get_config_status(self) -> Dict[str, Any]:\n        \"\"\"Retorna status da configuração\"\"\"\n        return {\n            \"smtp_server\": self.smtp_server,\n            \"smtp_port\": self.smtp_port,\n            \"username_configured\": bool(self.username),\n            \"password_configured\": bool(self.password),\n            \"use_tls\": self.use_tls,\n            \"connection_test\": self.test_connection()\n        }"