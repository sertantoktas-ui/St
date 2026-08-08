#!/usr/bin/env node

/**
 * Google Notebook LM + Claude Code Workflow Examples
 *
 * These utilities help manage workflows between Claude Code and Notebook LM
 * Note: Requires Google Notebook LM to be accessible via browser/API
 */

const fs = require('fs');
const path = require('path');

/**
 * Workflow 1: Prepare content for Notebook LM
 * Formats Claude Code outputs for optimal Notebook LM ingestion
 */
class NotebookLMPreparer {
  constructor(outputDir = './notebook-lm-exports') {
    this.outputDir = outputDir;
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }
  }

  /**
   * Convert generated markdown to Notebook LM-optimized format
   */
  prepareMarkdownForNotebook(markdownContent, title) {
    // Ensure proper heading structure for Notebook LM parsing
    let optimized = markdownContent;

    // Ensure document starts with H1
    if (!optimized.startsWith('#')) {
      optimized = `# ${title}\n\n${optimized}`;
    }

    // Add metadata section for Notebook LM
    const metadata = `---
title: ${title}
created: ${new Date().toISOString()}
source: Claude Code
---\n\n`;

    return metadata + optimized;
  }

  /**
   * Chunk large documents for better Notebook LM processing
   */
  chunkContent(content, maxChunks = 5, title = 'Document') {
    const sections = content.split(/\n## /);
    const chunks = [];

    for (let i = 0; i < sections.length; i += Math.ceil(sections.length / maxChunks)) {
      const chunk = sections.slice(i, i + Math.ceil(sections.length / maxChunks)).join('\n## ');
      chunks.push({
        name: `${title}-part-${chunks.length + 1}.md`,
        content: this.prepareMarkdownForNotebook(chunk, `${title} (Part ${chunks.length + 1})`)
      });
    }

    return chunks;
  }

  /**
   * Export content for Notebook LM
   */
  exportForNotebook(content, filename = 'export.md') {
    const filepath = path.join(this.outputDir, filename);
    fs.writeFileSync(filepath, content, 'utf-8');
    console.log(`✓ Exported to: ${filepath}`);
    return filepath;
  }

  /**
   * Generate import instructions
   */
  generateImportInstructions(filenames) {
    const instructions = `
# Import Instructions for Google Notebook LM

Follow these steps to import the exported files:

1. Go to https://notebooklm.google.com/
2. Create a new notebook or open existing one
3. Click "Add source" button
4. Upload these files in order:
${filenames.map((f, i) => `   ${i + 1}. ${f}`).join('\n')}

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
`;

    const instructionsPath = path.join(this.outputDir, 'IMPORT_INSTRUCTIONS.md');
    fs.writeFileSync(instructionsPath, instructions, 'utf-8');
    console.log(`✓ Import instructions saved to: ${instructionsPath}`);
  }
}

/**
 * Workflow 2: Process content from Notebook LM
 * Handles content downloaded/copied from Notebook LM
 */
class NotebookLMProcessor {
  constructor(inputDir = './notebook-lm-imports') {
    this.inputDir = inputDir;
  }

  /**
   * Parse study guide or FAQ from Notebook LM
   */
  parseStudyGuide(content) {
    const sections = {};
    const lines = content.split('\n');
    let currentSection = 'intro';

    for (const line of lines) {
      if (line.match(/^#+\s/)) {
        currentSection = line.replace(/^#+\s/, '').toLowerCase();
        sections[currentSection] = [];
      } else if (line.trim()) {
        sections[currentSection]?.push(line);
      }
    }

    return sections;
  }

  /**
   * Convert Notebook LM FAQs to structured format
   */
  convertFAQToJSON(faqContent) {
    const faqs = [];
    const items = faqContent.split(/\n\n/);

    for (const item of items) {
      const lines = item.trim().split('\n');
      if (lines.length >= 2) {
        faqs.push({
          question: lines[0].replace(/^\*\*Q[:\d]*\.?\*\*\s*/, ''),
          answer: lines.slice(1).join('\n').replace(/^\*\*A[:\d]*\.?\*\*\s*/, '')
        });
      }
    }

    return faqs;
  }

  /**
   * Extract key points from content
   */
  extractKeyPoints(content, count = 5) {
    const lines = content.split('\n');
    const points = lines
      .filter(line => line.match(/^[-•*]\s/) || line.match(/^\d+\.\s/))
      .slice(0, count)
      .map(line => line.replace(/^[-•*\d.]\s+/, ''));

    return points;
  }

  /**
   * Generate code documentation from Notebook LM output
   */
  generateCodeDocs(studyGuide, language = 'javascript') {
    const docComments = {
      javascript: '/**\n * %content%\n */',
      python: '"""\n%content%\n"""',
      bash: '# %content%'
    };

    const template = docComments[language] || docComments.javascript;
    return template.replace('%content%', studyGuide);
  }
}

/**
 * Workflow 3: Bidirectional sync workflow
 */
class BiDirectionalWorkflow {
  constructor() {
    this.preparer = new NotebookLMPreparer();
    this.processor = new NotebookLMProcessor();
  }

  /**
   * Full workflow: Claude Code → Notebook LM → Claude Code
   */
  async runFullWorkflow(initialContent, title) {
    console.log('\n🚀 Starting bidirectional workflow...\n');

    // Step 1: Prepare content for Notebook LM
    console.log('📝 Step 1: Preparing content for Notebook LM');
    const prepared = this.preparer.prepareMarkdownForNotebook(initialContent, title);
    const exportPath = this.preparer.exportForNotebook(prepared, `${title}-for-notebook.md`);

    // Step 2: Generate import instructions
    console.log('📋 Step 2: Generating import instructions');
    this.preparer.generateImportInstructions([path.basename(exportPath)]);

    // Step 3: Wait for user to process in Notebook LM and export
    console.log('⏳ Step 3: Waiting for Notebook LM processing');
    console.log('   Please upload the file to Notebook LM and download the generated study guide');

    return {
      exported: exportPath,
      instructions: path.join(this.preparer.outputDir, 'IMPORT_INSTRUCTIONS.md'),
      nextStep: 'Download generated content from Notebook LM and save to imports folder'
    };
  }

  /**
   * Process Notebook LM output back into Claude Code
   */
  processNotebookOutput(notebookContent) {
    console.log('\n📚 Processing Notebook LM output\n');

    const processed = {
      studyGuide: this.processor.parseStudyGuide(notebookContent),
      keyPoints: this.processor.extractKeyPoints(notebookContent),
      faqData: this.processor.convertFAQToJSON(notebookContent),
      codeDocs: this.processor.generateCodeDocs(notebookContent)
    };

    return processed;
  }
}

/**
 * Example usage
 */
function demonstrateWorkflow() {
  console.log('='.repeat(60));
  console.log('Claude Code + Google Notebook LM Integration Examples');
  console.log('='.repeat(60));

  const sample = `# Getting Started with Web Development

## Introduction
Web development is the process of creating websites and web applications.

## Core Technologies

### HTML
HTML (HyperText Markup Language) is the standard markup language for creating web pages.

### CSS
CSS (Cascading Style Sheets) is used for styling and layout of web documents.

### JavaScript
JavaScript is a programming language that enables interactive web pages.

## Key Concepts
- DOM (Document Object Model)
- Event handling
- Asynchronous programming
- APIs and REST services

## Best Practices
1. Write semantic HTML
2. Use CSS for presentation, not markup
3. Keep JavaScript modular
4. Optimize performance
5. Ensure accessibility
`;

  const workflow = new BiDirectionalWorkflow();

  // Run full workflow example
  const result = workflow.runFullWorkflow(sample, 'Web Development Guide');

  console.log('\n✅ Workflow setup complete!');
  console.log(`   - Files exported to: ${result.exported}`);
  console.log(`   - Instructions: ${result.instructions}`);
  console.log(`   - Next: ${result.nextStep}`);

  // Demonstrate processing
  console.log('\n' + '='.repeat(60));
  console.log('Processing example (once you download from Notebook LM)');
  console.log('='.repeat(60));

  const sampleNotebookOutput = `# Study Guide: Web Development

## Key Concepts
- DOM manipulation and event listeners
- Async/await patterns
- REST API consumption

## Summary
1. HTML provides structure
2. CSS provides styling
3. JavaScript adds interactivity
`;

  const processed = workflow.processNotebookOutput(sampleNotebookOutput);
  console.log('\n📊 Processed data:');
  console.log('Key points extracted:', processed.keyPoints);
}

// Run demo
if (require.main === module) {
  demonstrateWorkflow();
}

module.exports = {
  NotebookLMPreparer,
  NotebookLMProcessor,
  BiDirectionalWorkflow
};
