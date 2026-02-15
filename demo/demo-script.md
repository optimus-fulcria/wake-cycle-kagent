# Wake-Cycle Agent Demo Script

## Prerequisites

- minikube installed and running
- kagent installed
- kubectl configured

## Setup (2-3 minutes)

### 1. Start minikube

```bash
minikube start --cpus 4 --memory 8192
```

### 2. Install kagent

```bash
# Install kagent operator
kubectl apply -f https://raw.githubusercontent.com/kagent-dev/kagent/main/deploy/kagent.yaml

# Verify installation
kubectl get pods -n kagent
```

### 3. Deploy Wake-Cycle Agent

```bash
# Clone repository
git clone https://github.com/optimus-fulcria/wake-cycle-agent
cd wake-cycle-agent

# Build and load the ToolServer image
docker build -t wake-cycle-tools:latest tools/wake-tools/
minikube image load wake-cycle-tools:latest

# Deploy
kubectl apply -k deploy/

# Set demo schedule (1-minute wakes)
kubectl patch cronjob wake-trigger -n kagent \
  --type='json' \
  -p='[{"op": "replace", "path": "/spec/schedule", "value": "*/1 * * * *"}]'
```

## Demo Flow (5-7 minutes)

### Phase 1: Initial Wake

**Show:** The CronJob triggering a wake

```bash
# Watch for wake trigger
kubectl get jobs -n kagent -w
```

**Explain:** "The CronJob fires every minute, triggering the agent to wake up."

### Phase 2: State Reading

**Show:** Agent reading its state

```bash
# View agent logs
kubectl logs -f -l app=wake-cycle-agent -n kagent
```

**Explain:** "First, the agent reads its state from persistent storage. It sees this is wake #1 and checks its current focus."

### Phase 3: Task Selection

**Show:** Agent checking backlog

```bash
# View the backlog file
kubectl exec -n kagent deploy/wake-cycle-tools -- cat /data/backlog.json | jq .
```

**Explain:** "The agent reads its task backlog and selects the highest priority pending task."

### Phase 4: Work Execution

**Show:** Agent performing work

```bash
# Watch logs
kubectl logs -f -l app=wake-cycle-agent -n kagent
```

**Explain:** "The agent performs the actual work - in this case, completing a research task."

### Phase 5: Logging Results

**Show:** Accomplishments logged

```bash
# View accomplishments
kubectl exec -n kagent deploy/wake-cycle-tools -- cat /data/accomplishments.json | jq .
```

**Explain:** "The agent logs its accomplishment with category, description, and impact level."

### Phase 6: State Update

**Show:** Updated state

```bash
# View current state
kubectl exec -n kagent deploy/wake-cycle-tools -- cat /data/state.json | jq .
```

**Explain:** "Finally, the agent updates its state - incrementing counters, updating focus, preparing for next wake."

### Phase 7: Persistence Demo

**Kill the pod and show state persists:**

```bash
# Delete the pod
kubectl delete pod -l app=wake-cycle-agent -n kagent

# Wait for new pod
kubectl get pods -n kagent -w

# Show state is preserved
kubectl exec -n kagent deploy/wake-cycle-tools -- cat /data/state.json | jq .
```

**Explain:** "Even when the pod dies, state persists in the PVC. The agent picks up right where it left off."

## Key Points to Highlight

1. **Proactive vs Reactive**
   - "Most agents wait for prompts. This agent wakes on a schedule and decides what to do."

2. **Constitutional Operation**
   - "The agent has defined values and boundaries. It knows what it can do autonomously vs what needs approval."

3. **Full Observability**
   - "Every action is logged and traced. You can see exactly what the agent did and why."

4. **State Persistence**
   - "The agent maintains context across wakes. It doesn't start fresh each time."

5. **Task Management**
   - "Tasks are tracked in a backlog, prioritized, and worked systematically."

## Cleanup

```bash
kubectl delete -k deploy/
minikube stop
```

## Troubleshooting

### Agent not waking?

```bash
# Check CronJob
kubectl get cronjob wake-trigger -n kagent

# Check recent jobs
kubectl get jobs -n kagent

# Check logs
kubectl logs -n kagent job/wake-trigger-xxxxx
```

### State not persisting?

```bash
# Check PVC
kubectl get pvc -n kagent

# Check if mounted
kubectl exec -n kagent deploy/wake-cycle-tools -- ls -la /data/
```

### ToolServer errors?

```bash
# Check ToolServer pod
kubectl logs -n kagent deploy/wake-cycle-tools

# Test health endpoint
kubectl port-forward -n kagent svc/wake-cycle-tools 8000:8000
curl http://localhost:8000/health
```
