# Prometheous

AI-powered documentation generation and vector indexing tool for codebases.

## Overview

Prometheous is a comprehensive tool that combines automated code documentation generation with advanced vector indexing capabilities for Retrieval-Augmented Generation (RAG). It helps developers create beautiful, searchable documentation and enables intelligent code exploration through semantic search.

## Features

- 🤖 **AI-Powered Documentation**: Generate comprehensive documentation from your codebase using advanced language models
- 🔍 **Vector Indexing**: Create semantic search indexes for intelligent code exploration
- 💬 **RAG Chat Interface**: Interactive chat with your codebase using natural language queries
- 🌐 **Beautiful Web UI**: Modern, responsive documentation websites with search functionality
- 🔧 **Flexible Configuration**: Support for multiple AI providers (OpenAI, Ollama, etc.)
- 📦 **Easy Integration**: Simple CLI interface with sensible defaults

## Installation

```bash
pip install prometheous
```

## Quick Start

### Generate Documentation

```bash
# Generate documentation for current directory
prom doc

# Generate documentation with custom paths
prom doc --project-root ./src --doc-root ./docs --project-url https://github.com/user/repo
```

### Create Vector Index

```bash
# Create vector index for documentation
prom vec --source-path ./docs

# Create index with interactive chat
prom vec --source-path ./docs --interactive
```

## Configuration

### Environment Variables

```bash
# OpenAI Configuration
export OPENAI_API_KEY="your-api-key"
export OPENAI_API_BASE="https://api.openai.com/v1"  # or your custom endpoint

# Model Configuration
export PROMETHEOUS_MODEL_NAME="gpt-3.5-turbo"
export PROMETHEOUS_MAX_TOKENS=4096

# Embedding Configuration
export PROMETHEOUS_EMBEDDING_MODEL="text-embedding-ada-002"
export EMBEDDING_DIMENSION=1536

# Ollama Configuration (for local models)
export OLLAMA_BASE_URL="http://localhost:11434"
```

## CLI Reference

### `prom doc` - Generate Documentation

| Option | Description | Default |
|--------|-------------|----------|
| `--project-root, -p` | Project root directory | `.` |
| `--doc-root, -d` | Documentation output directory | `./docs` |
| `--project-url, -u` | Project URL for links | `https://github.com/user/project` |
| `--model-name` | AI model to use | `gpt-3.5-turbo` |
| `--max-tokens` | Maximum tokens per request | `4096` |
| `--headless` | Run without browser preview | `false` |

### `prom vec` - Vector Indexing

| Option | Description | Default |
|--------|-------------|----------|
| `--source-path, -s` | Source directory to index | Required |
| `--cache-dir, -c` | Cache directory for index | `./cache` |
| `--embedding-model` | Embedding model to use | `text-embedding-ada-002` |
| `--embedding-dimension` | Embedding vector dimension | `1536` |
| `--interactive, -i` | Start interactive chat | `false` |

## Examples

### Complete Documentation Workflow

```bash
# 1. Generate documentation
prom doc --project-root ./my-project --doc-root ./documentation

# 2. Create vector index
prom vec --source-path ./documentation --cache-dir ./vector-cache

# 3. Start interactive chat
prom vec --source-path ./documentation --interactive
```

### Using with Local Models (Ollama)

```bash
# Set up Ollama environment
export OLLAMA_BASE_URL="http://localhost:11434"
export OPENAI_API_BASE="http://localhost:11434/v1"
export PROMETHEOUS_MODEL_NAME="llama2"
export PROMETHEOUS_EMBEDDING_MODEL="llama2"

# Generate documentation
prom doc --project-root ./src
```

## Development

For development setup and advanced usage, see:
- [Usage Guide](./usage.txt)
- [Project Understanding](./project_understanding.txt)
- [Legacy Documentation](./README.old.md)

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
