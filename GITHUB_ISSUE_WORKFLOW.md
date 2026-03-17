# GitHub Issue Workflow for Beacon Stabilization

## Repository
Kvothik/Beacon

## GitHub Authentication
- Use GitHub CLI or API with token having repo and project scopes
- Verify with `gh auth status`

## Project Board
- Target GitHub Project: https://github.com/users/Kvothik/projects/1 (Project ID via GraphQL or CLI)
- Columns correspond to runtime states:
  - Backlog column for backlog tasks
  - In Progress column for active tasks
  - Verifying column for verifying tasks
  - Done column for accepted tasks
  - Blocked/Failed column for failed tasks

## Commands

### Create issue
```sh
gh issue create --repo Kvothik/Beacon --title "<Task Title>" \
--body "<Task Description>" --label "backend,type:task,status:ready"
```

### Add issue to project board
Project 1 ID and column IDs required.
```sh
gh project item add --project 1 --content-id <ISSUE_NODE_ID>
```

### Set project board status
```sh
gh project item move --project-item <PROJECT_ITEM_ID> --column-id <COLUMN_ID>
```

### Update issue status
```sh
gh issue edit <ISSUE_NUMBER> --add-label "status:complete" --remove-label "status:ready"
```

## Automation
- Query runtime tasks in backlog or active state
- Find corresponding GitHub issues by title
- Create missing issues and add to board
- Update board item status based on runtime state

## Examples (runtime backlog tasks)
- Create initial test suites (QA)
- Improve project documentation (Architecture)
- Implement missing document upload route (Backend)

---
