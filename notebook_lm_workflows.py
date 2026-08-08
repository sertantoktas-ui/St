#!/usr/bin/env python3

"""
Google Notebook LM + Claude Code Workflow Integration
Utilities for managing content flow between Claude Code and Notebook LM
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


class NotebookLMPreparer:
    """Prepares Claude Code output for Google Notebook LM ingestion"""

    def __init__(self, output_dir: str = "./notebook-lm-exports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def prepare_markdown_for_notebook(self, content: str, title: str) -> str:
        """Convert markdown to Notebook LM-optimized format"""
        # Ensure document starts with H1
        if not content.startswith("#"):
            content = f"# {title}\n\n{content}"

        # Add metadata section
        metadata = f"""---
title: {title}
created: {datetime.now().isoformat()}
source: Claude Code
---

"""
        return metadata + content

    def chunk_content(self, content: str, max_chunks: int = 5, title: str = "Document") -> List[Dict]:
        """Split large documents into manageable chunks"""
        sections = content.split("\n## ")
        chunk_size = max(1, len(sections) // max_chunks)
        chunks = []

        for i in range(0, len(sections), chunk_size):
            chunk_text = "\n## ".join(sections[i : i + chunk_size])
            chunk_num = len(chunks) + 1
            chunks.append(
                {
                    "name": f"{title}-part-{chunk_num}.md",
                    "content": self.prepare_markdown_for_notebook(
                        chunk_text, f"{title} (Part {chunk_num})"
                    ),
                }
            )

        return chunks

    def export_for_notebook(self, content: str, filename: str = "export.md") -> str:
        """Export content for Notebook LM"""
        filepath = self.output_dir / filename
        filepath.write_text(content, encoding="utf-8")
        print(f"✓ Exported to: {filepath}")
        return str(filepath)

    def generate_import_instructions(self, filenames: List[str]) -> None:
        """Generate step-by-step import instructions"""
        files_list = "\n".join(f"   {i + 1}. {f}" for i, f in enumerate(filenames))

        instructions = f"""# Import Instructions for Google Notebook LM

Follow these steps to import the exported files:

1. Go to https://notebooklm.google.com/
2. Create a new notebook or open existing one
3. Click "Add source" button
4. Upload these files in order:
{files_list}

5. Once uploaded, you can:
   - Generate audio summaries
   - Create study guides
   - Ask questions about the content
   - Download generated content

## Recommended Next Steps
- Listen to audio summary for overview
- Review generated study guide for key points
- Download any generated content back to Claude Code for further processing
- Ask specific questions to test content understanding
"""

        instructions_path = self.output_dir / "IMPORT_INSTRUCTIONS.md"
        instructions_path.write_text(instructions, encoding="utf-8")
        print(f"✓ Import instructions saved to: {instructions_path}")


class NotebookLMProcessor:
    """Processes content downloaded from Google Notebook LM"""

    def __init__(self, input_dir: str = "./notebook-lm-imports"):
        self.input_dir = Path(input_dir)
        self.input_dir.mkdir(parents=True, exist_ok=True)

    def parse_study_guide(self, content: str) -> Dict[str, List[str]]:
        """Parse study guide into structured sections"""
        sections = {}
        current_section = "intro"
        sections[current_section] = []

        for line in content.split("\n"):
            if line.startswith("#"):
                current_section = line.lstrip("#").strip().lower()
                sections[current_section] = []
            elif line.strip():
                if current_section not in sections:
                    sections[current_section] = []
                sections[current_section].append(line)

        return sections

    def convert_faq_to_json(self, faq_content: str) -> List[Dict[str, str]]:
        """Convert Notebook LM FAQ to structured JSON"""
        faqs = []
        items = faq_content.split("\n\n")

        for item in items:
            lines = [line for line in item.strip().split("\n") if line.strip()]
            if len(lines) >= 2:
                question = lines[0].replace("**Q", "").replace("**", "").strip()
                answer = "\n".join(lines[1:]).replace("**A", "").replace("**", "").strip()
                faqs.append({"question": question, "answer": answer})

        return faqs

    def extract_key_points(self, content: str, count: int = 5) -> List[str]:
        """Extract key points from content"""
        points = []
        for line in content.split("\n"):
            if line.strip() and any(line.startswith(c) for c in ["-", "•", "*", " 1."]):
                cleaned = line.lstrip("-•* ").strip()
                cleaned = cleaned.lstrip("0123456789. ")
                if cleaned:
                    points.append(cleaned)
                if len(points) >= count:
                    break
        return points[:count]

    def generate_code_docs(
        self, content: str, language: str = "python"
    ) -> str:
        """Generate code documentation comments"""
        doc_templates = {
            "python": '"""\n{}\n"""',
            "javascript": "/**\n * {}\n */",
            "bash": "# {}",
        }

        template = doc_templates.get(language, doc_templates["python"])
        return template.format(content)

    def export_as_json(
        self, data: Dict, filename: str = "processed.json"
    ) -> str:
        """Export processed data as JSON"""
        filepath = self.input_dir / filename
        filepath.write_text(json.dumps(data, indent=2), encoding="utf-8")
        print(f"✓ Exported JSON to: {filepath}")
        return str(filepath)


class BiDirectionalWorkflow:
    """Manages complete bidirectional workflow between Claude Code and Notebook LM"""

    def __init__(self):
        self.preparer = NotebookLMPreparer()
        self.processor = NotebookLMProcessor()

    def run_full_workflow(self, initial_content: str, title: str) -> Dict:
        """Execute full workflow: Claude Code → Notebook LM → Claude Code"""
        print("\n🚀 Starting bidirectional workflow...\n")

        # Step 1: Prepare content
        print("📝 Step 1: Preparing content for Notebook LM")
        prepared = self.preparer.prepare_markdown_for_notebook(initial_content, title)
        export_path = self.preparer.export_for_notebook(prepared, f"{title}-for-notebook.md")

        # Step 2: Generate instructions
        print("📋 Step 2: Generating import instructions")
        self.preparer.generate_import_instructions([os.path.basename(export_path)])

        # Step 3: Completion message
        print("✅ Step 3: Ready for Notebook LM")
        print("   Please upload the file to Notebook LM and download the generated content")

        return {
            "exported": export_path,
            "instructions": str(
                self.preparer.output_dir / "IMPORT_INSTRUCTIONS.md"
            ),
            "next_step": "Download generated content from Notebook LM and save to imports folder",
        }

    def process_notebook_output(self, notebook_content: str) -> Dict:
        """Process Notebook LM output back into Claude Code format"""
        print("\n📚 Processing Notebook LM output\n")

        return {
            "study_guide": self.processor.parse_study_guide(notebook_content),
            "key_points": self.processor.extract_key_points(notebook_content),
            "faq_data": self.processor.convert_faq_to_json(notebook_content),
            "python_docs": self.processor.generate_code_docs(
                notebook_content, "python"
            ),
            "js_docs": self.processor.generate_code_docs(
                notebook_content, "javascript"
            ),
        }


def demonstrate_workflow():
    """Demonstrate the complete workflow"""
    print("=" * 60)
    print("Claude Code + Google Notebook LM Integration")
    print("=" * 60)

    sample_content = """# Getting Started with Web Development

## Introduction
Web development is the process of creating websites and web applications using various technologies.

## Core Technologies

### HTML
HTML (HyperText Markup Language) is the standard markup language for creating web pages. It provides structure and meaning to web content.

### CSS
CSS (Cascading Style Sheets) is used for styling and layout of web documents. It controls visual presentation without affecting content structure.

### JavaScript
JavaScript is a programming language that enables interactive web pages. It runs in the browser and allows for dynamic content updates.

## Key Concepts
- DOM (Document Object Model) - represents the page structure
- Event handling - responds to user interactions
- Asynchronous programming - handles operations that take time
- APIs and REST services - communicate with backend services
- JSON - lightweight data format for data exchange

## Best Practices
1. Write semantic HTML for accessibility
2. Use CSS for presentation, not markup
3. Keep JavaScript modular and reusable
4. Optimize performance for faster load times
5. Ensure accessibility for all users
6. Use version control for collaboration
7. Write tests for reliability
"""

    workflow = BiDirectionalWorkflow()

    # Run workflow
    result = workflow.run_full_workflow(sample_content, "Web Development Guide")

    print("\n✅ Workflow initialized!")
    print(f"   📁 Files exported to: {result['exported']}")
    print(f"   📋 Instructions: {result['instructions']}")
    print(f"   ➡️  Next: {result['next_step']}")

    # Demonstrate processing
    print("\n" + "=" * 60)
    print("Processing Example (once you download from Notebook LM)")
    print("=" * 60)

    sample_notebook_output = """# Study Guide: Web Development

## Key Concepts
- DOM manipulation and event listeners enable interactive pages
- Async/await patterns handle time-consuming operations
- REST API consumption connects frontend to backend services

## Quick Summary
- HTML provides the structural foundation of web pages
- CSS handles all visual styling and responsive design
- JavaScript brings interactivity and dynamic behavior

## Important Points
1. Always use semantic HTML for better accessibility
2. Mobile-first approach for responsive design
3. Minimize JavaScript for better performance
4. Use modern tooling and frameworks
5. Test across different browsers and devices
"""

    processed = workflow.process_notebook_output(sample_notebook_output)

    print("\n📊 Processed data:")
    print(f"   Key points: {processed['key_points'][:3]}")
    print(f"   Study guide sections: {list(processed['study_guide'].keys())[:3]}")
    print(f"   FAQ items: {len(processed['faq_data'])}")


if __name__ == "__main__":
    demonstrate_workflow()
