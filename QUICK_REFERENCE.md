# Claude Code + Notebook LM - Quick Reference Card

## 🚀 30-Second Start

```bash
# Option 1: JavaScript
node notebook-lm-workflows.js

# Option 2: Python
python3 notebook_lm_workflows.py
```

## 📋 Three-Step Workflow

### Step 1: Prepare (Claude Code)
```python
from notebook_lm_workflows import NotebookLMPreparer
preparer = NotebookLMPreparer()
content = preparer.prepare_markdown_for_notebook(your_text, "Title")
preparer.export_for_notebook(content, "file.md")
```

### Step 2: Process (Notebook LM)
1. Go to https://notebooklm.google.com/
2. Create notebook → Add source → Upload files
3. Generate: Audio summary, Study guide, FAQs

### Step 3: Refine (Claude Code)
```python
from notebook_lm_workflows import NotebookLMProcessor
processor = NotebookLMProcessor()
points = processor.extract_key_points(notebook_output)
faq = processor.convert_faq_to_json(notebook_output)
```

---

## 🎯 Use Cases

| Use Case | Flow | Tools |
|----------|------|-------|
| **Documentation** | Code → Notebook (audio summary) → Deploy | Preparer + Notebook LM |
| **Research** | Research → Notebook (study guide) → Code (refine) | Notebook LM + Processor |
| **Training** | Content → Notebook (FAQ) → Code (format) | Preparer + Processor |
| **Batch Processing** | Multiple docs → Notebook → Code | Both utilities |

---

## 💡 Common Commands

### Export Content
```javascript
// JavaScript
preparer.exportForNotebook(content, "doc.md");
preparer.generateImportInstructions(["doc.md"]);

// Python
preparer.export_for_notebook(content, "doc.md")
preparer.generate_import_instructions(["doc.md"])
```

### Process Notebook Output
```javascript
// JavaScript
processor.extractKeyPoints(content, 5)
processor.convertFAQToJSON(content)
processor.parseStudyGuide(content)

// Python
processor.extract_key_points(content, 5)
processor.convert_faq_to_json(content)
processor.parse_study_guide(content)
```

### Chunk Large Files
```javascript
// JavaScript
preparer.chunkContent(largeContent, 5, "Title")

// Python
preparer.chunk_content(large_content, 5, "Title")
```

---

## 📁 Key Directories

```
notebook-lm-exports/    → Files to upload to Notebook LM
notebook-lm-imports/    → Files downloaded from Notebook LM
```

---

## ✨ Pro Tips

1. **Use audio summaries** for quick overview of large documents
2. **Ask Notebook LM questions** to validate your content
3. **Download study guides** for structured analysis
4. **Chunk large files** (>20 pages) before uploading
5. **Maintain version numbers** in filenames
6. **Process outputs with Python** for automation

---

## 🔗 Links

| Resource | URL |
|----------|-----|
| Notebook LM | https://notebooklm.google.com/ |
| Documentation | `CLAUDE_NOTEBOOK_LM_INTEGRATION.md` |
| Setup Guide | `NOTEBOOK_LM_SETUP.md` |
| Python Utils | `notebook_lm_workflows.py` |
| JS Utils | `notebook-lm-workflows.js` |

---

## ❓ Quick Troubleshoot

| Problem | Solution |
|---------|----------|
| File won't upload | Convert to Markdown using preparer |
| Large file slow | Chunk it: `chunkContent(file, 5)` |
| Lost files | Check `IMPORT_INSTRUCTIONS.md` |
| Format issues | Run `prepare_markdown_for_notebook()` |

---

**Print this card • Bookmark this file • Share with your team**

Last updated: 2026-08-08
