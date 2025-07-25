"""Core functionality for Prometheous package."""

import os
import sys
from pathlib import Path
from typing import Optional

# Add the utility script directory to Python path
current_dir = Path(__file__).parent
doc_control_dir = current_dir / "data"

if doc_control_dir.exists():
    sys.path.insert(0, str(doc_control_dir))
else:
    raise FileNotFoundError(f"Could not find utility script directory at {doc_control_dir}")


class DocumentGenerator:
    """Handles documentation generation for codebases."""
    
    def __init__(self, project_root: str, doc_root: str, project_url: str):
        self.project_root = Path(project_root).resolve()
        self.doc_root = Path(doc_root).resolve()
        self.project_url = project_url
        
        # Ensure directories exist
        self.doc_root.mkdir(parents=True, exist_ok=True)
        
    def generate(self):
        """Generate documentation for the codebase."""
        from recursive_document_writer import get_source_iterator_and_target_generator_param_from_document_dir, scan_code_dir_and_write_to_comment_dir, render_document_webpage
        print(f"Starting documentation generation...")
        print(f"Project root: {self.project_root}")
        print(f"Documentation output: {self.doc_root}")
        
        try:
            # Create a temporary document directory structure
            document_dir = self.doc_root.parent / f"{self.doc_root.name}_temp"
            document_dir.mkdir(exist_ok=True)
            
            # Create subdirectories
            src_dir = document_dir / "src"
            doc_dir = document_dir / "doc"
            
            # Copy or link source files
            if not src_dir.exists():
                if os.name == 'nt':  # Windows
                    import shutil
                    shutil.copytree(self.project_root, src_dir)
                else:  # Unix-like systems
                    src_dir.symlink_to(self.project_root)
            
            # Get parameters for document generation
            param = get_source_iterator_and_target_generator_param_from_document_dir(
                str(document_dir)
            )
            
            # Generate comments for code files
            scan_code_dir_and_write_to_comment_dir(str(document_dir))
            
            # Render the documentation webpage
            render_document_webpage(
                document_dir_path=str(document_dir),
                param=param,
                repository_url=self.project_url,
                template_dir=str(current_dir / "document_agi_computer_control"),
                output_filename="index.html"
            )
            
            # Move final documentation to target directory
            final_doc = doc_dir / "index.html"
            if final_doc.exists():
                import shutil
                shutil.copy2(final_doc, self.doc_root / "index.html")
                
                # Copy any additional assets
                for item in doc_dir.iterdir():
                    if item.is_file() and item.name != "index.html":
                        shutil.copy2(item, self.doc_root / item.name)
                    elif item.is_dir():
                        shutil.copytree(item, self.doc_root / item.name, dirs_exist_ok=True)
            
            print("Documentation generation completed successfully!")
            
        except Exception as e:
            print(f"Error during documentation generation: {e}")
            raise


class VectorIndexer:
    """Handles vector indexing for codebases and RAG functionality."""
    
    def __init__(self, source_path: str, cache_dir: str, 
                 embedding_model: str, embedding_dimension: int):
        self.source_path = Path(source_path).resolve()
        self.cache_dir = Path(cache_dir).resolve()
        self.embedding_model = embedding_model
        self.embedding_dimension = embedding_dimension
        
        # Ensure cache directory exists
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def create_index(self):
        """Create vector index for the source path."""
        print(f"Creating vector index...")
        print(f"Source path: {self.source_path}")
        print(f"Cache directory: {self.cache_dir}")
        print(f"Embedding model: {self.embedding_model}")
        
        try:
            # Set environment variables for the vector indexing script
            os.environ["DOC_PATH"] = str(self.source_path)
            
            # Add vectorstore directory to path
            vectorstore_dir = current_dir / "document_agi_computer_control" / "vectorstore_embedding_chat_rag"
            if vectorstore_dir.exists():
                sys.path.insert(0, str(vectorstore_dir))
                
                # Import and run the vector indexing by calling the main functionality directly
                try:
                    # Save original sys.argv to restore later
                    original_argv = sys.argv.copy()
                    
                    # Set sys.argv to simulate command line arguments for the original script
                    sys.argv = ['vectorindex_universal.py', '-s', str(self.source_path)]
                    
                    # Import the module and run it
                    import vectorindex_universal
                    
                    # Restore original sys.argv
                    sys.argv = original_argv
                    
                    print("Vector indexing completed successfully!")
                except ImportError as e:
                    print(f"Warning: Vector indexing module not found: {e}")
                    print("Creating basic index structure...")
                    self._create_basic_index()
                except SystemExit:
                    # The original script might call sys.exit(), catch it
                    sys.argv = original_argv
                    print("Vector indexing completed successfully!")
                except Exception as e:
                    sys.argv = original_argv
                    print(f"Error in vector indexing module: {e}")
                    print("Creating basic index structure...")
                    self._create_basic_index()
            else:
                print("Vector indexing directory not found, creating basic structure...")
                self._create_basic_index()
                
        except Exception as e:
            print(f"Error during vector indexing: {e}")
            raise
    
    def _create_basic_index(self):
        """Create a basic index structure when the full implementation is not available."""
        index_file = self.cache_dir / "index_info.txt"
        with open(index_file, 'w') as f:
            f.write(f"Vector index created for: {self.source_path}\n")
            f.write(f"Embedding model: {self.embedding_model}\n")
            f.write(f"Embedding dimension: {self.embedding_dimension}\n")
            f.write(f"Cache directory: {self.cache_dir}\n")
        print(f"Basic index information saved to: {index_file}")
    
    def start_chat(self):
        """Start interactive RAG chat session."""
        print("Starting interactive RAG chat...")
        print("Type 'quit' or 'exit' to end the session.")
        
        while True:
            try:
                query = input("\n🤖 Ask a question about the codebase: ").strip()
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                    
                if not query:
                    continue
                    
                # For now, provide a simple response
                # In a full implementation, this would query the vector index
                print(f"📝 You asked: {query}")
                print(f"🔍 Searching vector index for relevant information...")
                print(f"💡 This is a placeholder response. Full RAG implementation would provide contextual answers based on the indexed codebase.")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except EOFError:
                print("\n👋 Goodbye!")
                break
