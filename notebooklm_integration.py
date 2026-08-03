"""
NotebookLM Integration Module
Provides document analysis and insight generation similar to Google NotebookLM
using Claude API within the personal assistant.
"""

import os
import json
from pathlib import Path
from anthropic import Anthropic

class NotebookLMIntegration:
    """Integration for document analysis similar to Google NotebookLM"""

    def __init__(self, api_key=None):
        """Initialize the NotebookLM integration"""
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.client = Anthropic(api_key=self.api_key)
        self.documents = {}
        self.conversations = {}

    def add_document(self, doc_id, content, title=""):
        """Add a document for analysis"""
        self.documents[doc_id] = {
            "title": title,
            "content": content,
            "created_at": str(Path.cwd())
        }
        return f"Document '{title}' added successfully"

    def generate_summary(self, doc_id):
        """Generate a summary of the document"""
        if doc_id not in self.documents:
            return "Document not found"

        doc = self.documents[doc_id]
        response = self.client.messages.create(
            model="claude-opus-4-1",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": f"""Provide a concise summary of this document:

Title: {doc['title']}

Content:
{doc['content']}

Format the response as:
- Main Points (3-5 bullets)
- Key Insights
- Action Items (if applicable)"""
                }
            ]
        )
        return response.content[0].text

    def generate_outline(self, doc_id):
        """Generate a structured outline of the document"""
        if doc_id not in self.documents:
            return "Document not found"

        doc = self.documents[doc_id]
        response = self.client.messages.create(
            model="claude-opus-4-1",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": f"""Create a detailed hierarchical outline for this document:

Title: {doc['title']}

Content:
{doc['content']}

Format as nested bullets showing the document structure."""
                }
            ]
        )
        return response.content[0].text

    def ask_document(self, doc_id, question):
        """Ask questions about a specific document"""
        if doc_id not in self.documents:
            return "Document not found"

        doc = self.documents[doc_id]
        if doc_id not in self.conversations:
            self.conversations[doc_id] = []

        conversation = self.conversations[doc_id]
        conversation.append({
            "role": "user",
            "content": question
        })

        # Build context with document
        messages = [
            {
                "role": "user",
                "content": f"""You are analyzing the following document:

Title: {doc['title']}

Content:
{doc['content']}

Now answer questions about it."""
            }
        ]
        messages.extend(conversation)

        response = self.client.messages.create(
            model="claude-opus-4-1",
            max_tokens=1024,
            messages=messages
        )

        answer = response.content[0].text
        conversation.append({
            "role": "assistant",
            "content": answer
        })

        return answer

    def compare_documents(self, doc_ids, analysis_type="differences"):
        """Compare multiple documents"""
        if not all(doc_id in self.documents for doc_id in doc_ids):
            return "One or more documents not found"

        docs_content = "\n\n".join([
            f"--- Document: {self.documents[doc_id]['title']} ---\n{self.documents[doc_id]['content']}"
            for doc_id in doc_ids
        ])

        prompts = {
            "differences": "Highlight the key differences between these documents",
            "similarities": "Identify common themes and similarities",
            "synthesis": "Synthesize information from all documents into a unified perspective"
        }

        prompt = prompts.get(analysis_type, prompts["differences"])

        response = self.client.messages.create(
            model="claude-opus-4-1",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": f"""{prompt}:

{docs_content}"""
                }
            ]
        )
        return response.content[0].text

    def export_analysis(self, doc_id, format_type="markdown"):
        """Export document analysis in various formats"""
        if doc_id not in self.documents:
            return "Document not found"

        summary = self.generate_summary(doc_id)
        outline = self.generate_outline(doc_id)
        doc = self.documents[doc_id]

        if format_type == "markdown":
            content = f"""# {doc['title']}

## Summary
{summary}

## Outline
{outline}

## Original Content
{doc['content']}
"""
        else:
            content = json.dumps({
                "title": doc["title"],
                "summary": summary,
                "outline": outline,
                "original_content": doc["content"]
            }, indent=2)

        return content

# Integration with existing assistant
def create_notebooklm_tools():
    """Create tools for the assistant to use NotebookLM features"""
    return [
        {
            "name": "add_document",
            "description": "Add a document for analysis (similar to NotebookLM)",
            "input_schema": {
                "type": "object",
                "properties": {
                    "doc_id": {
                        "type": "string",
                        "description": "Unique identifier for the document"
                    },
                    "content": {
                        "type": "string",
                        "description": "The document content to analyze"
                    },
                    "title": {
                        "type": "string",
                        "description": "Document title"
                    }
                },
                "required": ["doc_id", "content", "title"]
            }
        },
        {
            "name": "analyze_document",
            "description": "Generate summary and outline of a document",
            "input_schema": {
                "type": "object",
                "properties": {
                    "doc_id": {
                        "type": "string",
                        "description": "Document ID"
                    },
                    "analysis_type": {
                        "type": "string",
                        "enum": ["summary", "outline"],
                        "description": "Type of analysis"
                    }
                },
                "required": ["doc_id", "analysis_type"]
            }
        },
        {
            "name": "ask_about_document",
            "description": "Ask questions about a document's content",
            "input_schema": {
                "type": "object",
                "properties": {
                    "doc_id": {
                        "type": "string",
                        "description": "Document ID"
                    },
                    "question": {
                        "type": "string",
                        "description": "Question about the document"
                    }
                },
                "required": ["doc_id", "question"]
            }
        }
    ]
