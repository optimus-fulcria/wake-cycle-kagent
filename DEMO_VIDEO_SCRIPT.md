# Wake-Cycle Agent Demo Video Script

**Duration:** 3-5 minutes
**Format:** Screen recording with voiceover (or text overlay)

---

## [0:00-0:15] Hook

**Visual:** Title card with Wake-Cycle Agent logo/name

**Script:**
"What if your AI agent didn't wait for commands... but woke up on its own, checked its tasks, and got to work? That's the Wake-Cycle Agent pattern - autonomous agents that run on Kubernetes using kagent."

---

## [0:15-0:45] Problem Statement

**Visual:** Split screen - left: human typing prompts, right: idle AI waiting

**Script:**
"Traditional AI agents are reactive. They wait for you to prompt them. But real productivity requires an agent that can work in the background - checking systems, handling tasks, and reporting back.

The challenge: How do you build an agent that:
- Wakes on a schedule
- Remembers what it was doing
- Knows its boundaries
- Works autonomously within constraints?"

---

## [0:45-1:15] Solution Overview

**Visual:** Architecture diagram from README

**Script:**
"Wake-Cycle Agent solves this with four components:

1. A CronJob that triggers wakes - every 15 minutes, every hour, whatever you need
2. Persistent storage that maintains state across sessions
3. A Constitution that defines what the agent can and can't do
4. MCP tools that give the agent capabilities"

---

## [1:15-2:30] Live Demo

**Visual:** Terminal showing kubectl commands

**Script:**
"Let me show you. I've deployed a Wake-Cycle Agent to this Kubernetes cluster."

```bash
# Show the deployed resources
kubectl get agents,cronjobs,pvc -n kagent

# Expected output showing:
# - wake-cycle-agent (Agent)
# - wake-trigger (CronJob)
# - agent-data (PVC)
```

"Here's the agent watching for work..."

```bash
# Show the agent logs
kubectl logs -f -l app=wake-cycle-agent -n kagent --tail=50
```

"And here's the magic - let's look at its state file:"

```bash
# Port-forward to read state
kubectl exec deploy/wake-cycle-agent -n kagent -- cat /data/state.json | jq .
```

"The agent remembers its wake count, current focus, and what it accomplished. Every wake, it picks up where it left off."

---

## [2:30-3:00] Constitution Demo

**Visual:** Show constitution.yaml

**Script:**
"The key innovation is the Constitution. It defines the agent's boundaries:"

```yaml
# AUTONOMOUS: The agent can do this freely
- Read metrics
- Check systems
- Log accomplishments

# APPROVAL_REQUIRED: Must ask first
- Restart services
- Spend money
- External communications
```

"This lets you deploy agents with confidence. They operate within defined limits."

---

## [3:00-3:30] MCP Tools

**Visual:** Show ToolServer code

**Script:**
"The agent's capabilities come from MCP tools. This ToolServer provides:

- read_state / write_state - Memory across sessions
- read_backlog / update_task - Task management
- log_accomplishment - Track completed work
- send_notification - Alert the human principal

Adding new capabilities is just adding new tools."

---

## [3:30-4:00] Use Cases

**Visual:** 3-panel showing different agent use cases

**Script:**
"Wake-Cycle Agents enable new possibilities:

- A DevOps agent that monitors clusters and scales resources
- A Research agent that fetches papers and updates knowledge bases
- A Sales agent that checks leads and sends reports

Any background task that benefits from persistence and boundaries."

---

## [4:00-4:30] Closing

**Visual:** GitHub repo link, kagent logo

**Script:**
"Wake-Cycle Agent is open source and built on kagent - the Kubernetes AI Agent platform.

The pattern works today. Deploy one in your cluster and see how autonomous agents can amplify your team.

Links in the description. Thanks for watching."

---

## Recording Notes

1. **Environment Setup:**
   - Minikube or kind cluster
   - kagent installed
   - Demo data pre-populated for smooth demo

2. **Backup Plan:**
   - Pre-recorded terminal sessions using asciinema if live demo fails
   - Static screenshots as fallback

3. **Audio:**
   - Can record voiceover separately and add to video
   - Alternative: text overlays if voiceover not available

4. **Tools Needed:**
   - OBS or similar for screen recording
   - Terminal with good font size (18+)
   - Dark theme for readability

## Submission Checklist

- [ ] Video uploaded to YouTube/Loom
- [ ] README has video link
- [ ] GitHub repo is public
- [ ] Submitted on aihackathon.dev before March 1

---

*Script created: 2026-02-15*
