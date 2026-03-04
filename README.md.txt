# JIRA-To-CodeRepo Agentic AI System

An end-to-end **Agentic AI pipeline** that converts a **Jira ticket into
actual code changes** inside a GitHub repository using semantic code
understanding, vector search, and automated Git operations.

This project demonstrates how AI agents can automate parts of the
**Software Development Life Cycle (SDLC)**.

The system reads a Jira ticket, identifies impacted code using a
semantic vector knowledge base, proposes modifications, and commits
changes to GitHub.

------------------------------------------------------------------------

# Problem Statement

In modern agile environments, developers spend significant time
performing repetitive activities:

-   Reading Jira tickets
-   Understanding legacy code
-   Identifying impacted files
-   Writing boilerplate modifications
-   Creating branches
-   Committing changes

These tasks are manual, slow, and error‑prone.

### Objective

Build an **Agentic AI workflow** capable of:

1.  Understanding Jira tickets
2.  Performing semantic code search
3.  Detecting impacted classes and methods
4.  Generating code modification proposals
5.  Committing updates automatically to GitHub

This enables **autonomous SDLC assistance**.

------------------------------------------------------------------------

# Architecture Overview

High-level workflow

Jira Ticket → Jira Agent → Impact Detection Engine → LLM Proposal
Generator → Git Agent → GitHub Repository

Core Infrastructure

Docker\
Redis\
Celery\
Qdrant\
Prometheus

------------------------------------------------------------------------

# Technology Stack

## Docker

Provides a reproducible execution environment.

Benefits: - Environment isolation - Dependency consistency - Simplified
deployment

## Qdrant (Vector Database)

Stores **semantic embeddings of code chunks**.

Used for: - Semantic code search - Impact detection

## Redis

Used as a **message broker** for Celery.

Responsibilities: - Queue management - Task distribution

## Celery

Handles asynchronous workloads such as:

-   Repository indexing
-   Embedding generation
-   Impact analysis

## Prometheus

Provides monitoring and observability for:

-   Worker performance
-   Service health
-   Metrics tracking

------------------------------------------------------------------------

# Repository Structure

agents/
  ---- orchestrator.py
  ---- jira_agent.py
  ---- impact_agent.py
  ---- git_agent.py
  ---- proposal_agent.py

workers/
   ---- tasks.py
   ---- indexer.py
   ---- dependency_graph.py
  ---- impact.py
  ---- impact_engine.py

tools/
---- git_tool.py

monitoring /
--- metrics.py

docker-compose.yml
Dockerfile
requirements.txt
.env


------------------------------------------------------------------------

# Git Repository Used

Base Repository
https://github.com/iluwatar/java-design-patterns

Forked Repository
https://github.com/pankaj8blr/java-design-patterns

------------------------------------------------------------------------

# Jira Configuration
Jira Instance: https://pankaj8blr-agenticai.atlassian.net
Example Ticket:  SCRUM-5
Ticket URL : https://pankaj8blr-agenticai.atlassian.net/browse/SCRUM-5

------------------------------------------------------------------------

# Environment Configuration

Create a `.env` file

OPENAI_API_KEY=your_openai_key
GITHUB_USERNAME=pankaj8blr\
GITHUB_TOKEN=ghp_xxxxxx
JIRA_BASE_URL=https://pankaj8blr-agenticai.atlassian.net\
JIRA_EMAIL=your_email\
JIRA_API_TOKEN=your_jira_token
REPO_PATH=/app/java_repo

------------------------------------------------------------------------

# Docker Setup

## Build Containers

Standard build
      docker compose build

Clean rebuild
      docker compose build --no-cache

Use no-cache when dependencies or environment variables change.

## Start Services
docker compose up -d

Verify running containers

docker ps

Expected containers

worker\
redis\
qdrant\
prometheus

------------------------------------------------------------------------

# Indexing the Code Repository

Enter worker container

docker compose exec worker bash

Start python

python

Run indexing

from workers.tasks import index_repo_task
index_repo_task.delay("/app/java_repo")

This step:

1.  Parses Java source files
2.  Extracts methods
3.  Generates semantic summaries
4.  Creates embeddings
5.  Stores vectors in Qdrant

------------------------------------------------------------------------

# Running the Agentic Workflow

Start Python

python

Run orchestrator

from agents.orchestrator import run_full_agentic_flow
run_full_agentic_flow("SCRUM-5")

------------------------------------------------------------------------

# Workflow Breakdown

## 1. Chunking

Java files are parsed and split into methods.

Each method is stored with:

-   Code
-   Summary
-   Embedding

Stored in Qdrant.

## 2. Jira Context Extraction

Jira agent retrieves ticket summary and description via Jira REST API.

## 3. Impact Analysis

Impact engine:

1.  Converts Jira text → embedding
2.  Queries Qdrant
3.  Retrieves relevant code chunks

## 4. Proposal Generation

LLM generates code modifications using:

-   Jira context
-   Existing method implementation

## 5. GitHub Integration

Git agent:

-   Creates branch
-   Writes modified files
-   Adds commits
-   Pushes branch

## 6. Commit Changes

Changes pushed to GitHub branch:

ai-auto-update

Developers can review via Pull Request.

------------------------------------------------------------------------

# Common Issues & Fixes

Docker not running → start Docker Desktop

tree-sitter build failure → install build-essential in Dockerfile

Qdrant 404 → ensure collection creation before upsert

Git authentication failure → use GitHub PAT with repo permission

Jira permission error → ensure API user has Browse Project permission

------------------------------------------------------------------------

# Source Code

Full project available at

https://github.com/pankaj8blr/JIRA-To-CodeRepo-AgenticAI

------------------------------------------------------------------------

# Future Improvements

Possible extensions

-   Automatic Pull Request creation
-   Jira status automation
-   Slack / Teams notifications
-   Multi-repository indexing
-   Kubernetes deployment
-   Security scanning agent
-   Test generation agent
-   CI/CD pipeline integration

------------------------------------------------------------------------

# Conclusion

This project demonstrates how Agentic AI can automate key SDLC stages.

Capabilities implemented:

-   Semantic code knowledge base
-   Vector-based impact detection
-   AI-generated code modification
-   Automated Git operations
-   Fully containerized architecture

This serves as a foundation for building **Autonomous Engineering
Platforms**.
