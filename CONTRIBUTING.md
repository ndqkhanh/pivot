# Contributing to Pivot

Thank you for your interest in contributing to Pivot! This document provides guidelines and instructions for contributing.

---

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [Making Changes](#making-changes)
5. [Submitting Changes](#submitting-changes)
6. [RFC Process](#rfc-process)
7. [Community](#community)

---

## Code of Conduct

Pivot follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

---

## Getting Started

### Ways to Contribute

- **Code:** Implement features, fix bugs, improve performance
- **Documentation:** Write guides, improve API docs, create examples
- **Testing:** Write tests, report bugs, validate fixes
- **Design:** UI/UX improvements, architecture proposals
- **Community:** Answer questions, review PRs, help newcomers

### Good First Issues

Look for issues labeled `good-first-issue` or `help-wanted` on GitHub.

---

## Development Setup

### Prerequisites

- **Go 1.21+** (for gateway, eval, replay engines)
- **Python 3.11+** (for SDK and eval authoring)
- **Node.js 20+** (for console UI)
- **Docker & Docker Compose** (for local development)
- **Make** (for build automation)

### Clone and Setup

```bash
# Clone repository
git clone https://github.com/pivot-ai/pivot.git
cd pivot

# Install dependencies
make install

# Start local development environment
docker-compose up -d

# Run tests
make test

# Run linters
make lint
```

### Project Structure

```
pivot/
├── docs/              # Documentation
├── spec/              # Specifications (OTel, schemas, policies)
├── gateway/           # Go: Gateway/Collector
├── sdk/               # SDKs (Python, TypeScript, Java, Go)
├── eval/              # Evaluation engine
├── replay/            # Replay engine
├── policy-pack/       # Policy packs
├── console/           # Next.js UI
├── integrations/      # Framework integrations
├── benchmarks/        # Benchmark adapters
└── tests/             # Integration tests
```

---

## Making Changes

### Branch Naming

- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation
- `refactor/description` - Code refactoring
- `test/description` - Test improvements

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Tests
- `chore`: Maintenance

**Examples:**
```
feat(sdk): add Anthropic SDK instrumentation

Implements auto-instrumentation for anthropic.Anthropic class.
Captures all message calls with full provenance.

Closes #123
```

### Code Style

**Go:**
- Follow [Effective Go](https://golang.org/doc/effective_go.html)
- Run `gofmt` and `golangci-lint`
- Write tests for all public APIs

**Python:**
- Follow [PEP 8](https://pep8.org/)
- Use `black` for formatting
- Use `ruff` for linting
- Type hints required

**TypeScript:**
- Follow [TypeScript Style Guide](https://google.github.io/styleguide/tsguide.html)
- Use `prettier` for formatting
- Use `eslint` for linting

### Testing

**Unit Tests:**
```bash
# Go
make test-go

# Python
make test-python

# TypeScript
make test-ts
```

**Integration Tests:**
```bash
make test-integration
```

**Coverage:**
- Minimum 80% coverage for new code
- Run `make coverage` to check

---

## Submitting Changes

### Pull Request Process

1. **Fork the repository**
2. **Create a feature branch**
3. **Make your changes**
4. **Write/update tests**
5. **Update documentation**
6. **Run tests and linters**
7. **Commit with DCO sign-off** (see below)
8. **Push to your fork**
9. **Open a Pull Request**

### Developer Certificate of Origin (DCO)

All commits must be signed off with DCO:

```bash
git commit -s -m "feat: add new feature"
```

This adds a `Signed-off-by` line to your commit message:

```
Signed-off-by: Your Name <your.email@example.com>
```

By signing off, you certify that you have the right to submit the code under the Apache 2.0 license.

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings
- [ ] Tests added/updated
- [ ] All tests pass
- [ ] DCO sign-off included
```

### Review Process

1. **Automated checks** run (tests, linters, coverage)
2. **Maintainer review** (1-2 maintainers)
3. **Address feedback**
4. **Approval** (requires 1 maintainer approval)
5. **Merge** (squash and merge)

---

## RFC Process

For significant changes, submit an RFC (Request for Comments):

### When to Write an RFC

- New major features
- Breaking changes
- Architecture changes
- API changes
- New dependencies

### RFC Template

```markdown
# RFC-XXXX: Title

**Status:** Draft | Review | Accepted | Rejected  
**Author:** Your Name  
**Created:** YYYY-MM-DD

## Summary
One-paragraph explanation

## Motivation
Why is this needed?

## Proposal
Detailed design

## Alternatives
What other approaches were considered?

## Unresolved Questions
What needs to be figured out?
```

### RFC Process

1. **Create RFC** in `docs/rfcs/XXXX-title.md`
2. **Open PR** with RFC
3. **Discussion** (2-week minimum)
4. **Revisions** based on feedback
5. **Decision** by maintainers
6. **Implementation** if accepted

---

## Community

### Communication Channels

- **GitHub Issues:** Bug reports, feature requests
- **GitHub Discussions:** Questions, ideas, general discussion
- **Discord:** Real-time chat (coming soon)
- **Twitter/X:** [@pivot_ai](https://twitter.com/pivot_ai) (coming soon)

### Meetings

- **Weekly Office Hours:** Thursdays 10am PT (coming soon)
- **Monthly Community Call:** First Wednesday of month (coming soon)

### Recognition

Contributors are recognized in:
- `CONTRIBUTORS.md` file
- Release notes
- Annual contributor report
- Conference talks and blog posts

---

## Questions?

- Open a [GitHub Discussion](https://github.com/pivot-ai/pivot/discussions)
- Join our Discord (coming soon)
- Email: contributors@pivot.ai (coming soon)

---

**Thank you for contributing to Pivot!** 🚀
