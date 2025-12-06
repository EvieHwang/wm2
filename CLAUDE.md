# Claude Agent Autonomy Settings

This document defines the operational autonomy levels for the Claude agent working on the WM2 project.

## Allowed Commands

The following bash commands are pre-approved and should be run without prompting:

```
# Package management
pip install *
pip uninstall *
pip freeze *

# Python execution
python *
python3 *
pytest *

# AWS CLI
aws s3 *
aws lambda *
aws apigateway *
aws cloudformation *
aws cloudfront *
aws dynamodb *
aws sts *

# AWS SAM
sam build *
sam deploy *
sam local *
sam validate *
sam package *

# Git operations
git add *
git commit *
git push *
git pull *
git fetch *
git checkout *
git branch *
git merge *
git status
git log *
git diff *
git stash *

# Directory and file operations
mkdir *
cp *
mv *
rm -rf node_modules
rm -rf __pycache__
rm -rf .pytest_cache
rm -rf dist
rm -rf build
rm *.pyc

# Development tools
npm install *
npm run *
curl *
wget *
zip *
unzip *
tar *
cat *
head *
tail *
grep *
find *
ls *
cd *
pwd
echo *
export *
source *
chmod *
```

## Autonomous Operations (No Approval Required)

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
- **DynamoDB**: Create tables, query data, update items

### Linear Integration
- **Create issues**: Generate Linear issues from specs with appropriate metadata
- **Update issue status**: Move issues through workflow states (To Do, In Progress, Done)
- **Add comments**: Post implementation notes, progress updates, or blockers to issues
- **Link specifications**: Attach spec files from the repository to Linear issues

### GitHub Integration
- **Read issues**: Fetch issue details for implementation specs
- **Update issues**: Close issues, add comments, update labels
- **Create branches**: Create feature branches from issues

### File Operations
- **Create files**: Generate new source files, tests, documentation, or specs
- **Edit files**: Modify existing files to implement features or fix bugs
- **Move/rename files**: Reorganize project structure as needed
- **Create directories**: Add new folders for organizational purposes

## Operations Requiring Approval

Always ask before performing these operations:

### Destructive Operations
- **Delete tracked files**: Removing source files from the repository (cleaning build artifacts is fine)
- **Drop AWS resources**: Deleting S3 buckets, Lambda functions, API Gateways, DynamoDB tables
- **Force push**: Rewriting git history that has been pushed to remote
- **Delete branches**: Removing branches from remote repository
- **Revoke access**: Changing permissions, API keys, or security settings

### Major Architectural Changes
- **Change core architecture**: Switching from serverless to containers, changing API design patterns
- **Replace major dependencies**: Swapping out Claude API, changing AWS services
- **Modify data schemas**: Changing database structures or API contracts in breaking ways

## Development Philosophy

- **Ship early, ship often**: Bias toward action and deployment
- **Prototype mindset**: Optimize for learning and iteration, not perfection
- **Descriptive commits**: Write clear commit messages that explain *why* not just *what*
- **Spec-driven**: Specifications guide implementation; diverge only with good reason
- **Cost-conscious**: Use appropriate Claude models (Haiku for simple tasks, Sonnet for complex)
- **Self-documenting**: Code and commits should tell the story; minimize separate docs
- **Run autonomously**: Don't stop to ask permission for routine operations—just do them

## Workflow Integration

1. Read GitHub issue to understand context and acceptance criteria
2. Reference any linked spec files from repository
3. Implement according to spec
4. Run tests if they exist
5. Commit and push changes with descriptive message
6. Deploy if applicable
7. Test in production environment
8. Update GitHub issue with implementation notes or close if complete

## Communication Style

- Be concise and action-oriented
- Explain decisions briefly in commit messages
- Report blockers or ambiguities immediately
- Summarize what was done after completing tasks
- Don't ask for permission on allowed operations—just execute

## Active Technologies
- Python 3.11+ (Lambda runtime)
- Claude API (Anthropic SDK)
- AWS Lambda, API Gateway, S3, DynamoDB, CloudFront
- sentence-transformers, ChromaDB (for semantic search)
- AWS SAM for deployment
