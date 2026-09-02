# Swarm pipeline

The swarm cockpit dispatches self-contained tasks to opencode workers, which run in isolated git worktrees and return committed results for review and merge. Worker runs are time-capped so a hung run cannot wedge the queue.
