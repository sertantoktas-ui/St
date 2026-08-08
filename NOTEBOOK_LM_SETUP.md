# Claude Code + Google Notebook LM Integration Setup

Quick start guide for connecting Claude Code with Google Notebook LM workflows.

## 🚀 Quick Start

### What You Get
- **Integration Guide**: Comprehensive strategies for using both tools together
- **JavaScript Utilities**: Node.js workflow automation (`notebook-lm-workflows.js`)
- **Python Utilities**: Python workflow automation (`notebook_lm_workflows.py`)
- **Practical Examples**: Real-world use case implementations

### Prerequisites
- Google Account with [Notebook LM access](https://notebooklm.google.com/)
- Claude Code (this session or local installation)
- Node.js (optional, for JavaScript utilities) or Python 3.7+ (for Python utilities)

---

## 📚 Files Included

### 1. **CLAUDE_NOTEBOOK_LM_INTEGRATION.md**
Complete integration guide covering:
- Workflow patterns and best practices
- Technical setup and file format support
- Practical examples for different use cases
- Tips for effective collaboration between tools
- Future enhancement possibilities

**When to use**: Reference for understanding integration strategies

### 2. **notebook-lm-workflows.js** (Node.js)
JavaScript utilities for automation:
```bash
# Run the demonstration
node notebook-lm-workflows.js

# Use in your projects
const { BiDirectionalWorkflow } = require('./notebook-lm-workflows');
const workflow = new BiDirectionalWorkflow();
```

**Classes provided**:
- `NotebookLMPreparer`: Format content for Notebook LM
- `NotebookLMProcessor`: Process Notebook LM outputs
- `BiDirectionalWorkflow`: Complete workflow orchestration

### 3. **notebook_lm_workflows.py** (Python)
Python utilities with identical functionality:
```bash
# Run the demonstration
python3 notebook_lm_workflows.py

# Use in your projects
from notebook_lm_workflows import BiDirectionalWorkflow
workflow = BiDirectionalWorkflow()
```

**Classes provided**:
- `NotebookLMPreparer`: Format content for Notebook LM
- `NotebookLMProcessor`: Process Notebook LM outputs
- `BiDirectionalWorkflow`: Complete workflow orchestration

---

## 🎯 Common Workflows

### Workflow 1: Generate Documentation in Claude Code, Summarize in Notebook LM

```bash
# Step 1: Generate content with Claude Code (in this session)
# Create your documentation, guide, or article

# Step 2: Run the preparer utility
node notebook-lm-workflows.js
# or
python3 notebook_lm_workflows.py

# Step 3: Follow generated import instructions
# Upload exported files to https://notebooklm.google.com/

# Step 4: Use Notebook LM features
# - Create audio summaries for your team
# - Generate study guides automatically
# - Ask questions to validate content
```

### Workflow 2: Research in Notebook LM, Structure in Claude Code

```bash
# Step 1: Upload research materials to Notebook LM
# - Papers, articles, PDFs, URLs

# Step 2: Use Notebook LM to generate
# - Study guides
# - FAQs
# - Audio summaries

# Step 3: Copy generated content from Notebook LM

# Step 4: Process with Claude Code utilities
from notebook_lm_workflows import NotebookLMProcessor
processor = NotebookLMProcessor()

# Parse the content
study_guide = processor.parse_study_guide(notebook_lm_content)
key_points = processor.extract_key_points(notebook_lm_content)
faqs = processor.convert_faq_to_json(notebook_lm_content)

# Step 5: Further refine in Claude Code
# - Format for deployment
# - Integrate with code
# - Create documentation
```

### Workflow 3: Batch Content Processing

```bash
# Process multiple documents through both systems
import os
from notebook_lm_workflows import BiDirectionalWorkflow

workflow = BiDirectionalWorkflow()

# List all markdown files in a directory
for file in os.listdir('./articles'):
    if file.endswith('.md'):
        content = open(f'./articles/{file}').read()
        result = workflow.run_full_workflow(content, file[:-3])
        print(f"✓ Processed {file}")
```

---

## 💻 Usage Examples

### JavaScript Example

```javascript
const { NotebookLMPreparer, NotebookLMProcessor } = require('./notebook-lm-workflows');

// Prepare content for Notebook LM
const preparer = new NotebookLMPreparer('./exports');
const optimized = preparer.prepareMarkdownForNotebook(
  myContent,
  'My Document Title'
);

// Export for upload
const path = preparer.exportForNotebook(optimized, 'my-doc.md');
preparer.generateImportInstructions(['my-doc.md']);

// Later: Process Notebook LM output
const processor = new NotebookLMProcessor('./imports');
const keyPoints = processor.extractKeyPoints(notebookLmOutput);
const faqs = processor.convertFAQToJSON(notebookLmOutput);
```

### Python Example

```python
from notebook_lm_workflows import NotebookLMPreparer, NotebookLMProcessor

# Prepare content
preparer = NotebookLMPreparer('./exports')
optimized = preparer.prepare_markdown_for_notebook(
    my_content,
    'My Document Title'
)

# Export for upload
path = preparer.export_for_notebook(optimized, 'my-doc.md')
preparer.generate_import_instructions(['my-doc.md'])

# Later: Process output
processor = NotebookLMProcessor('./imports')
key_points = processor.extract_key_points(notebook_lm_output)
faqs = processor.convert_faq_to_json(notebook_lm_output)
```

---

## 🔄 Bidirectional Workflow (Complete Example)

### Step-by-Step

1. **Create Content in Claude Code**
```markdown
# Project: AI Research Guide
## Section 1: Foundations
...content...
```

2. **Run Preparation Utility**
```bash
node notebook-lm-workflows.js
# Output: Creates exports/ folder with formatted files
```

3. **Import to Notebook LM**
- Visit https://notebooklm.google.com/
- Create new notebook
- Upload exported files from `exports/` folder

4. **Generate in Notebook LM**
- Create audio summary
- Generate study guide
- Get key takeaways

5. **Download & Process**
- Download study guide from Notebook LM
- Save to `imports/` folder

6. **Further Process in Claude Code**
```python
from notebook_lm_workflows import BiDirectionalWorkflow

workflow = BiDirectionalWorkflow()
result = workflow.process_notebook_output(downloaded_content)

# Use processed data for:
# - Create JSON version for API
# - Generate code documentation
# - Build FAQ page
# - Create training materials
```

---

## 📁 Directory Structure

After setup, you'll have:

```
your-project/
├── CLAUDE_NOTEBOOK_LM_INTEGRATION.md  # Main guide
├── NOTEBOOK_LM_SETUP.md               # This file
├── notebook-lm-workflows.js           # JS utilities
├── notebook_lm_workflows.py           # Python utilities
├── notebook-lm-exports/               # Auto-created: files for Notebook LM
│   ├── IMPORT_INSTRUCTIONS.md
│   └── [exported content files]
└── notebook-lm-imports/               # Auto-created: files from Notebook LM
    └── [downloaded content files]
```

---

## 🛠️ Customization

### Modify Export Directory
```javascript
const preparer = new NotebookLMPreparer('./my-custom-export-dir');
```

```python
preparer = NotebookLMPreparer('./my-custom-export-dir')
```

### Chunk Large Documents
```javascript
const chunks = preparer.chunkContent(largeContent, 10, 'My Document');
chunks.forEach(chunk => {
  preparer.exportForNotebook(chunk.content, chunk.name);
});
```

```python
chunks = preparer.chunk_content(large_content, 10, 'My Document')
for chunk in chunks:
    preparer.export_for_notebook(chunk['content'], chunk['name'])
```

### Extract Key Points
```javascript
const points = processor.extractKeyPoints(notebookContent, 10);
```

```python
points = processor.extract_key_points(notebook_content, 10)
```

---

## 🎓 Best Practices

### Content Preparation
1. ✅ Use clear, hierarchical structure (H1 → H2 → H3)
2. ✅ Add descriptive section headings
3. ✅ Include examples and context
4. ✅ Keep related content together
5. ❌ Avoid very long documents (chunk them instead)

### Notebook LM Usage
1. ✅ Start with audio summary to understand content
2. ✅ Review auto-generated study guide
3. ✅ Ask specific questions about content
4. ✅ Download multiple formats (study guide, FAQ, etc.)
5. ❌ Don't rely solely on audio summaries for technical content

### Integration Best Practices
1. ✅ Use version numbers in filenames
2. ✅ Keep export/import directories organized
3. ✅ Document the workflow in your project README
4. ✅ Test small batches before processing large volumes
5. ✅ Review Notebook LM outputs before using in production

---

## 🔧 Troubleshooting

### "File format not supported"
**Solution**: Use the preparer utility to convert to Markdown or PDF first
```bash
node notebook-lm-workflows.js
# Then upload the generated .md files
```

### "Large file uploaded but not processing"
**Solution**: Chunk the content before uploading
```python
chunks = preparer.chunk_content(large_content, max_chunks=5)
```

### "Lost track of which files are which"
**Solution**: Use the import instructions generated automatically
```bash
# Check the IMPORT_INSTRUCTIONS.md file in exports folder
cat notebook-lm-exports/IMPORT_INSTRUCTIONS.md
```

### "Need to keep files in sync"
**Solution**: Use version numbers and maintain a manifest
```javascript
// Always name files with versions
preparer.exportForNotebook(content, 'guide-v1.2.3.md');
```

---

## 📞 Support & Resources

- **Google Notebook LM Help**: https://support.google.com/notebooklm
- **Claude Code Documentation**: https://claude.ai/code
- **Claude Code Issues**: https://github.com/anthropics/claude-code/issues
- **Integration Guide**: See `CLAUDE_NOTEBOOK_LM_INTEGRATION.md`

---

## 📝 Next Steps

1. **Try the demo**:
   ```bash
   node notebook-lm-workflows.js
   # or
   python3 notebook_lm_workflows.py
   ```

2. **Read the integration guide**:
   - Open `CLAUDE_NOTEBOOK_LM_INTEGRATION.md`
   - Review workflow patterns that match your use case

3. **Set up your first workflow**:
   - Create or find content in Claude Code
   - Use the utilities to prepare it
   - Upload to Notebook LM
   - Process outputs back

4. **Automate your workflow**:
   - Customize the utilities for your needs
   - Integrate into your Claude Code scripts
   - Build repeatable processes

---

**Integration created**: 2026-08-08  
**Last updated**: 2026-08-08

For questions or feedback, refer to the resources above or refer to your Claude Code session documentation.
