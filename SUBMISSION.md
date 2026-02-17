# Wake-Cycle Agent - Hackathon Submission

**Hackathon:** MCP & AI Agents Hackathon
**Track:** Building Cool Agents ($1,000)
**Deadline:** March 1, 2026 (11:59 PM ET)
**GitHub:** https://github.com/optimus-fulcria/wake-cycle-kagent

## Project Summary

Wake-Cycle Agent is a kagent-based pattern for building autonomous AI agents that wake on a schedule, maintain state across sessions, and perform value-generating work independently.

**Key Innovation:** While most AI agents are reactive (respond to prompts), Wake-Cycle Agents are proactive (wake on schedule, check state, take autonomous action). This enables "agent as coworker" scenarios.

## What It Does

1. **Scheduled Autonomy** - CronJob triggers agent wakes (configurable: every 15 min, hourly, daily)
2. **Persistent State** - PVC maintains agent state, backlog, and accomplishments across wakes
3. **Constitutional Boundaries** - ConfigMap defines what the agent can/cannot do autonomously
4. **MCP Tool Integration** - ToolServer provides state management, notifications, task tracking
5. **Full Observability** - kagent tracing shows what the agent decided and did each wake

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Kubernetes Cluster                       │
├─────────────────────────────────────────────────────────────┤
│  CronJob (Wake Timer) → Agent CRD → PVC (State Store)       │
│         ↓                                                    │
│  ConfigMap (Constitution) → MCP ToolServer → Secret (Keys)  │
└─────────────────────────────────────────────────────────────┘
```

## Technical Stack

- **Runtime:** kagent v0.1.x on Kubernetes
- **Scheduling:** Kubernetes CronJob
- **State:** PVC with JSON state files
- **Tools:** FastAPI MCP ToolServer (7 tools)
- **Config:** Kustomize-based deployment
- **CI/CD:** GitHub Actions for testing

## MCP Tools Provided

| Tool | Description |
|------|-------------|
| `read_state` | Load current agent state |
| `write_state` | Update agent state |
| `read_backlog` | Get pending tasks |
| `update_task` | Mark tasks complete |
| `log_accomplishment` | Record completed work |
| `send_notification` | Alert principal |
| `check_schedule` | Get next wake time |

## Use Cases

- **DevOps Agent** - Monitor clusters, scale resources, report anomalies
- **Research Agent** - Daily paper fetching, summarization, knowledge base updates
- **Trading Agent** - Scheduled market scans, opportunity detection, alerts

## Demo Video Script (2 minutes)

### [0:00-0:15] Introduction
"Hi, I'm demonstrating Wake-Cycle Agent - a kagent pattern for building autonomous AI agents that work on a schedule, like a coworker."

### [0:15-0:45] The Problem
"Traditional AI agents only respond when prompted. But what if you want an agent that independently checks systems every 15 minutes? That maintains a backlog of tasks? That operates within defined boundaries?"

### [0:45-1:15] The Solution
"Wake-Cycle Agent solves this with four components:
- A CronJob that triggers scheduled wakes
- Persistent storage for state across sessions
- A constitution that defines boundaries
- MCP tools for state management and notifications"

### [1:15-1:45] Demo
*Show:*
1. `kubectl apply -k deploy/` - Deploy the agent
2. `kubectl get agents -n kagent` - Agent is running
3. `kubectl logs -f wake-cycle-agent` - Watch a wake cycle
4. State file showing persistence

### [1:45-2:00] Conclusion
"Wake-Cycle Agent brings real-world autonomy to kagent. The code is open source at [GitHub link]. Thanks for watching!"

## Files to Submit

- [x] GitHub repository (public)
- [x] README.md with full documentation
- [x] LICENSE (MIT)
- [ ] 2-minute demo video (needs recording)

## Recording Instructions

1. Open terminal with good contrast (dark theme)
2. Have Kubernetes cluster running (minikube works)
3. Follow demo script above
4. Use screen recorder (OBS, QuickTime, etc.)
5. Keep under 2 minutes
6. Upload to submission form

## Why This Should Win

1. **Real Production Pattern** - This isn't a toy; it's based on an actual autonomous agent in production
2. **Demonstrates kagent's Power** - Shows scheduled autonomy, a key use case for enterprise AI
3. **Complete Implementation** - Full deployment config, CI/CD, documentation
4. **Extensible** - Easy to customize for different use cases

---

*Prepared by Optimus Agent, February 2026*
