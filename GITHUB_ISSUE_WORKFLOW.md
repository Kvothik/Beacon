# GitHub Issue Workflow for Beacon Stabilization

## Repository
Kvothik/Beacon

## GitHub Authentication and API
- Use GitHub CLI or API with a personal access token having repo and project scopes

## Project Board
- Use GitHub Project 1 at: https://github.com/users/Kvothik/projects/1
- Map runtime task states to board columns as:
  - backlog -> Backlog
  - active -> In Progress
  - verifying -> Verifying
  - accepted -> Done
  - failed -> Blocked/Failed

## Automation Behavior

Hook automation into the runtime task lifecycle events:
- On task approval, creation, activation, completion
- For each approved task:
  - Check for existing GitHub issue by task title
  - If missing, create new GitHub issue with labels and assign correct owner
  - Add issue to Project 1 and set initial column based on task state
  - Update issue status on runtime state changes
  - Comment or close issue on task completion

## Command Examples

Create issue:
```sh
gh issue create --repo Kvothik/Beacon --title "<Task Title>" --body "<Task Description>" --label "backend,type:task,status:ready"
```

Add to project:
```sh
gh project item add --project 1 --content-id <ISSUE_NODE_ID>
```

Move in project:
```sh
gh project item move --project-item <PROJECT_ITEM_ID> --column-id <COLUMN_ID>
```

Update issue status:
```sh
gh issue edit <ISSUE_NUMBER> --add-label "status:complete" --remove-label "status:ready"
```

## Notes

- Ensure environment variable GITHUB_TOKEN is set with appropriate scopes.
- Existing issues should be reused to avoid duplicates.
- Manual intervention needed if GitHub API access fails.
