# Event Bus SGCS

Infraestrutura interna de publicação/subscrição de eventos de domínio.

## Objetivo

Desacoplar efeitos colaterais (auditoria, analytics, notificações) sem alterar o comportamento atual dos endpoints.

## Componentes

| Ficheiro | Responsabilidade |
|----------|------------------|
| `events.py` | Definição de `DomainEvent` e nomes padronizados |
| `subscribers.py` | Registo de handlers por evento |
| `dispatcher.py` | Execução segura dos handlers |
| `event_bus.py` | API pública `publish()` / `subscribe()` |

## Uso

```python
from core.events import event_bus, EventNames

event_bus.publish(EventNames.USER_CREATED, {"user_id": 1})
```

## Notas

- Controlado pela feature flag `FEATURE_EVENT_BUS_ENABLED`.
- Por defeito apenas regista logs; integrações futuras subscrevem eventos sem alterar views existentes.
