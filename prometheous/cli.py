#!/usr/bin/env python3
"""CLI interface for Prometheous."""

import click
import os
import sys
from pathlib import Path

from .core import DocumentGenerator, VectorIndexer


@click.group()
@click.version_option()
def main():
    """Prometheous: AI-powered documentation generation and vector indexing tool."""
    pass


@main.command()
@click.option(
    "--project-root", 
    "-p", 
    default=".",
    help="Path to the project root directory to document"
)
@click.option(
    "--doc-root", 
    "-d", 
    default="./docs",
    help="Path to output documentation directory"
)
@click.option(
    "--project-url", 
    "-u", 
    default="https://github.com/user/project",
    help="Project URL for documentation links"
)
@click.option(
    "--openai-api-key", 
    envvar="OPENAI_API_KEY",
    help="OpenAI API key (can also be set via OPENAI_API_KEY env var)"
)
@click.option(
    "--openai-api-base", 
    envvar="OPENAI_API_BASE",
    default="https://api.openai.com/v1",
    help="OpenAI API base URL (can also be set via OPENAI_API_BASE env var)"
)
@click.option(
    "--model-name", 
    envvar="PROMETHEOUS_MODEL_NAME",
    default="gpt-3.5-turbo",
    help="Model name to use for documentation generation"
)
@click.option(
    "--max-tokens", 
    envvar="PROMETHEOUS_MAX_TOKENS",
    default=4096,
    type=int,
    help="Maximum tokens for model responses"
)
@click.option(
    "--headless", 
    envvar="HEADLESS",
    default=False,
    is_flag=True,
    help="Run in headless mode (no browser preview)"
)
def doc(project_root, doc_root, project_url, openai_api_key, openai_api_base, 
        model_name, max_tokens, headless):
    """Generate documentation for a codebase."""
    
    # Set environment variables
    if openai_api_key:
        os.environ["OPENAI_API_KEY"] = openai_api_key
    if openai_api_base:
        os.environ["OPENAI_API_BASE"] = openai_api_base
    if model_name:
        os.environ["PROMETHEOUS_MODEL_NAME"] = model_name
    
    os.environ["PROMETHEOUS_MAX_TOKENS"] = str(max_tokens)
    os.environ["PROJECT_ROOT"] = str(Path(project_root).resolve())
    os.environ["DOC_ROOT"] = str(Path(doc_root).resolve())
    os.environ["PROJECT_URL"] = project_url
    os.environ["HEADLESS"] = str(headless).lower()
    
    click.echo(f"🔍 Generating documentation for: {project_root}")
    click.echo(f"📝 Output directory: {doc_root}")
    click.echo(f"🔗 Project URL: {project_url}")
    click.echo(f"🤖 Model: {model_name}")
    
    try:
        generator = DocumentGenerator(
            project_root=project_root,
            doc_root=doc_root,
            project_url=project_url
        )
        generator.generate()
        click.echo("✅ Documentation generation completed successfully!")
        
        if not headless:
            click.echo(f"🌐 Documentation available at: {doc_root}/index.html")
            
    except Exception as e:
        click.echo(f"❌ Error generating documentation: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option(
    "--source-path", 
    "-s", 
    required=True,
    help="Path to the source directory or documentation to index"
)
@click.option(
    "--cache-dir", 
    "-c", 
    default="./cache",
    help="Directory to store vector index cache"
)
@click.option(
    "--openai-api-key", 
    envvar="OPENAI_API_KEY",
    help="OpenAI API key (can also be set via OPENAI_API_KEY env var)"
)
@click.option(
    "--openai-api-base", 
    envvar="OPENAI_API_BASE",
    default="https://api.openai.com/v1",
    help="OpenAI API base URL (can also be set via OPENAI_API_BASE env var)"
)
@click.option(
    "--embedding-model", 
    envvar="PROMETHEOUS_EMBEDDING_MODEL",
    default="text-embedding-ada-002",
    help="Embedding model to use for vector indexing"
)
@click.option(
    "--ollama-base-url", 
    envvar="OLLAMA_BASE_URL",
    help="Ollama base URL for local embeddings"
)
@click.option(
    "--embedding-dimension", 
    envvar="EMBEDDING_DIMENSION",
    default=1536,
    type=int,
    help="Embedding dimension for the chosen model"
)
@click.option(
    "--interactive", 
    "-i", 
    default=False,
    is_flag=True,
    help="Start interactive RAG chat after indexing"
)
def vec(source_path, cache_dir, openai_api_key, openai_api_base, 
        embedding_model, ollama_base_url, embedding_dimension, interactive):
    """Create vector index for codebase and optionally start RAG chat."""
    
    # Set environment variables
    if openai_api_key:
        os.environ["OPENAI_API_KEY"] = openai_api_key
    if openai_api_base:
        os.environ["OPENAI_API_BASE"] = openai_api_base
    if embedding_model:
        os.environ["PROMETHEOUS_EMBEDDING_MODEL"] = embedding_model
    if ollama_base_url:
        os.environ["OLLAMA_BASE_URL"] = ollama_base_url
    
    os.environ["EMBEDDING_DIMENSION"] = str(embedding_dimension)
    
    click.echo(f"🔍 Creating vector index for: {source_path}")
    click.echo(f"💾 Cache directory: {cache_dir}")
    click.echo(f"🧠 Embedding model: {embedding_model}")
    click.echo(f"📐 Embedding dimension: {embedding_dimension}")
    
    try:
        indexer = VectorIndexer(
            source_path=source_path,
            cache_dir=cache_dir,
            embedding_model=embedding_model,
            embedding_dimension=embedding_dimension
        )
        indexer.create_index()
        click.echo("✅ Vector indexing completed successfully!")
        
        if interactive:
            click.echo("🚀 Starting interactive RAG chat...")
            indexer.start_chat()
            
    except Exception as e:
        click.echo(f"❌ Error creating vector index: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
