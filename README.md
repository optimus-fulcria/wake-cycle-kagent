# Wake-Cycle Agent

A kagent-based pattern for building autonomous AI agents that wake on a schedule, maintain state across sessions, and perform value-generating work independently.

## What is a Wake-Cycle Agent?

Traditional AI agents are **reactive** - they respond to prompts. Wake-Cycle Agents are **proactive** - they wake on a schedule, check their state and environment, and take autonomous action.

```
┌─────────────────────────────────────────────────────────────┐
│                        Wake Cycle                            │
├─────────────────────────────────────────────────────────────┤
│  ┌─────┐    ┌──────┐    ┌──────┐    ┌──────┐    ┌─────┐    │
│  │Sleep│───▶│ Wake │───▶│Check │───▶│ Work │───▶│Log  │    │
│  │     │    │      │    │State │    │      │    │     │    │
│  └──┬──┘    └──────┘    └──────┘    └──────┘    └──┬──┘    │
│     │                                               │       │
│     └───────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

## Architecture

The Wake-Cycle Agent runs on Kubernetes using kagent, with:

- **CronJob**: Triggers wakes on a schedule (default: every 15 minutes)
- **PVC**: Persists state, backlog, and accomplishments across sessions
- **ConfigMap**: Stores the agent's "constitution" - its values and boundaries
- **ToolServer**: Provides MCP tools for state management and external interactions

```
┌─────────────────────────────────────────────────────────────┐
│                     Kubernetes Cluster                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────┐    ┌──────────────────┐               │
│  │   CronJob        │    │   ConfigMap      │               │
│  │   (Wake Timer)   │───▶│   (Constitution) │               │
│  └────────┬─────────┘    └──────────────────┘               │
│           │                                                  │
│           ▼                                                  │
│  ┌──────────────────┐    ┌──────────────────┐               │
│  │   kagent Agent   │───▶│   PVC            │               │
│  │   (Wake-Cycle)   │    │   (State Store)  │               │
│  └────────┬─────────┘    └──────────────────┘               │
│           │                                                  │
│           ▼                                                  │
│  ┌──────────────────┐    ┌──────────────────┐               │
│  │   MCP ToolServer │    │   Secret         │               │
│  │   (Capabilities) │    │   (API Keys)     │               │
│  └──────────────────┘    └──────────────────┘               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Kubernetes cluster (minikube works great)
- kagent installed ([installation guide](https://kagent.dev/docs/installation))
- kubectl configured

### Deploy

```bash
# Clone and deploy
kubectl apply -k deploy/

# Verify deployment
kubectl get agents -n kagent
kubectl get cronjobs -n kagent

# Watch the agent work
kubectl logs -f -l app=wake-cycle-agent -n kagent
```

### Demo Mode

For demonstration, you can set the wake cycle to 1 minute:

```bash
# Edit cronjob schedule
kubectl patch cronjob wake-trigger -n kagent \
  --type='json' \
  -p='[{"op": "replace", "path": "/spec/schedule", "value": "*/1 * * * *"}]'
```

## Core Concepts

### 1. State Persistence

The agent maintains state across wakes in `/data/state.json`:

```json
{
  "wake_count": 42,
  "last_wake": "2026-02-15T01:00:00Z",
  "current_focus": "Building hackathon submission",
  "active_tasks": ["research", "coding"],
  "accomplishments_today": 3
}
```

### 2. Task Backlog

Tasks live in `/data/backlog.json`:

```json
{
  "tasks": [
    {
      "id": "research-001",
      "title": "Research kagent ecosystem",
      "priority": "high",
      "status": "pending"
    }
  ]
}
```

### 3. Constitution

The agent operates within defined boundaries (ConfigMap):

```yaml
# AUTONOMOUS: Can do freely
- Research and planning
- Internal operations
- Logging accomplishments

# APPROVAL_REQUIRED: Must ask first
- External communications
- Spending money
- Publishing content

# FORBIDDEN: Never allowed
- Impersonating humans
- Accessing unauthorized systems
```

### 4. MCP Tools

The ToolServer provides these capabilities:

| Tool | Description |
|------|-------------|
| `read_state` | Load current agent state |
| `write_state` | Update agent state |
| `read_backlog` | Get pending tasks |
| `update_task` | Mark tasks complete |
| `log_accomplishment` | Record completed work |
| `send_notification` | Alert principal |

## Use Cases

### DevOps Agent
- Wake every 30 minutes
- Check cluster health
- Scale resources if needed
- Report anomalies

### Research Agent
- Wake daily
- Fetch new papers in domain
- Summarize and categorize
- Update knowledge base

### Monitoring Agent
- Wake every 5 minutes
- Check service endpoints
- Alert on failures
- Track uptime metrics

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `WAKE_INTERVAL` | Cron schedule | `*/15 * * * *` |
| `STATE_PATH` | Path to state file | `/data/state.json` |
| `LOG_LEVEL` | Logging verbosity | `info` |

### Customizing the Constitution

Edit `deploy/configmap.yaml` to define your agent's values and boundaries:

```yaml
data:
  CONSTITUTION.md: |
    # My Custom Agent Constitution

    ## Primary Objective
    Monitor Kubernetes clusters and alert on issues.

    ## Autonomous Actions
    - Read metrics from Prometheus
    - Check pod health
    - Create log summaries

    ## Requires Approval
    - Restart pods
    - Scale deployments
    - Modify configurations
```

## Observability

Wake-Cycle Agents integrate with kagent's tracing:

```bash
# View agent traces
kubectl port-forward svc/kagent-controller 8080:8080 -n kagent
# Open http://localhost:8080/traces
```

Each wake cycle produces traces showing:
- What tasks were checked
- What decisions were made
- What actions were taken
- What state was updated

## Why Wake-Cycle Agents?

| Feature | Reactive Agent | Wake-Cycle Agent |
|---------|---------------|------------------|
| Initiative | User-prompted | Self-initiated |
| Memory | Per-session | Persistent |
| Scheduling | Manual | Automated |
| Boundaries | Implicit | Constitutional |
| Observability | Logs only | Full tracing |

Wake-Cycle Agents enable "agent as coworker" scenarios where the agent independently handles background tasks while maintaining transparency and boundaries.

## Development

### Local Testing

```bash
# Run ToolServer locally
cd tools/wake-tools
pip install -r requirements.txt
python main.py

# Test tools
curl -X POST http://localhost:8000/tools/read_state -d '{}'
```

### Adding New Tools

1. Add tool definition to `deploy/toolserver.yaml`
2. Implement handler in `tools/wake-tools/main.py`
3. Test locally, then deploy

## License

MIT License - see LICENSE file.

## Acknowledgments

- Built on [kagent](https://kagent.dev) - Kubernetes AI Agent platform
- Inspired by real-world autonomous agent operations
- Created for the MCP Agents Hackathon 2026

---

*"The future of AI is not agents that wait for instructions, but agents that anticipate needs."*
