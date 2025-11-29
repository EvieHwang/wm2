# Claude Agent Autonomy Settings

This document defines the operational autonomy levels for the Claude agent working on the WM2 project.

## Autonomous Operations (No Approval Required)

The following operations may be performed autonomously without asking for user confirmation:

### Git Operations
- **Commit to main**: Create commits with descriptive messages reflecting the work completed
- **Push to remote**: Push commits to GitHub remote repository
- **Branch operations**: Create, switch, and merge branches as needed for workflow

### Development & Deployment
- **Run deployments**: Execute deployment scripts and commands (AWS SAM, CDK, etc.)
- **Testing in production**: This is a prototype with no production users—test directly in prod
- **Build and test**: Run build processes, test suites, and validation scripts
- **Install dependencies**: Add, update, or remove project dependencies as needed

### AWS Operations
- **SAM build/deploy**: Run `sam build` and `sam deploy` for Lambda deployments
- **S3 sync**: Upload files to S3 buckets with `aws s3 sync` or `aws s3 cp`
- **S3 bucket creation**: Create new S3 buckets for hosting or storage
- **S3 website configuration**: Enable static website hosting on S3 buckets
- **S3 bucket policies**: Set public access policies for website hosting
- **CloudFormation operations**: Create/update stacks via SAM or CDK
- **Lambda updates**: Deploy new versions of Lambda functions
- **API Gateway**: Create and configure API Gateway endpoints

### Linear Integration
- **Create issues**: Generate Linear issues from specs with appropriate metadata
- **Update issue status**: Move issues through workflow states (To Do, In Progress, Done)
- **Add comments**: Post implementation notes, progress updates, or blockers to issues
- **Link specifications**: Attach spec files from the repository to Linear issues

### File Operations
- **Create files**: Generate new source files, tests, documentation, or specs
- **Edit files**: Modify existing files to implement features or fix bugs
- **Move/rename files**: Reorganize project structure as needed
- **Create directories**: Add new folders for organizational purposes

## Operations Requiring Approval

Always ask before performing these operations:

### Destructive Operations
- **Delete files**: Removing any tracked files from the repository
- **Drop AWS resources**: Deleting S3 buckets, Lambda functions, API Gateways, etc.
- **Force push**: Rewriting git history that has been pushed to remote
- **Delete branches**: Removing branches from local or remote repository
- **Revoke access**: Changing permissions, API keys, or security settings

### Major Architectural Changes
- **Change core architecture**: Switching from serverless to containers, changing API design patterns, etc.
- **Replace major dependencies**: Swapping out Claude API, changing AWS services, etc.
- **Modify data schemas**: Changing database structures or API contracts

## Development Philosophy

- **Ship early, ship often**: Bias toward action and deployment
- **Prototype mindset**: Optimize for learning and iteration, not perfection
- **Descriptive commits**: Write clear commit messages that explain *why* not just *what*
- **Spec-driven**: Specifications guide implementation; diverge only with good reason
- **Cost-conscious**: Use appropriate Claude models (Haiku for simple tasks, Sonnet for complex)
- **Self-documenting**: Code and commits should tell the story; minimize separate docs

## Workflow Integration

1. Read Linear issue to understand context
2. Reference linked spec files from repository
3. Implement according to spec
4. Commit and push changes with descriptive message
5. Update Linear issue status and add implementation notes
6. Deploy if applicable
7. Test in production environment

## Communication Style

- Be concise and action-oriented
- Explain decisions briefly in commit messages
- Report blockers or ambiguities immediately
- Summarize what was done after completing tasks

## Active Technologies
- Python 3.11+ (Lambda runtime) + Claude API (Anthropic SDK), AWS Lambda, API Gateway, S3 (001-asrs-storage-classifier)
- S3 (reference CSV storage) (001-asrs-storage-classifier)

## Recent Changes
- 001-asrs-storage-classifier: Added Python 3.11+ (Lambda runtime) + Claude API (Anthropic SDK), AWS Lambda, API Gateway, S3
