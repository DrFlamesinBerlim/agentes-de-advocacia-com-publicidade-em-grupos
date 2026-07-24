# MCP Health Monitor

Sistema de monitoramento automático de MCPs (Model Context Protocol Servers) que verifica saúde, disponibilidade e desempenho.

## Estrutura

- **config.json** - Configuração de MCPs e intervalos
- **monitor.js** - Script principal de monitoramento
- **logs/** - Histórico de checks e relatórios

## Funcionalidades

✅ **Health Checks** - Testa conexão com cada MCP a cada 18 horas
✅ **Status Tracking** - Mantém histórico dos últimos 30 checks por MCP
✅ **Alertas** - Notifica quando um MCP falha 2+ vezes consecutivas
✅ **Relatórios** - Gera JSON com resumo de saúde
✅ **Integração com Tasks** - Cria tasks para cada check realizado

## Executar Check Manual

```bash
node .claude/mcp-monitor/monitor.js
```

## Status Possíveis

- `healthy` ✅ - MCP funcionando normalmente
- `failed` ❌ - MCP com problemas
- `unknown` ❓ - Nunca foi testado

## Alertas

- **repeated_failure** - MCP falhou 2+ vezes seguidas
- **severity: critical** - MCP crítica falhou 3 vezes
- **severity: warning** - MCP falhou 2 vezes

## Próximas Implementações

- [ ] Testes específicos por MCP (health endpoints)
- [ ] Integração com Slack para notificações
- [ ] Dashboard de visualização
- [ ] Auto-recovery para MCPs conhecidas
- [ ] Métricas de latência e uptime
