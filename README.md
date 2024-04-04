# TzuratLink: A Comprehensive Platform for Digital Talmud Study

## Introduction

TzuratLink represents a groundbreaking endeavor to integrate the meticulous study of the Talmud with the vast digital resources available through Sefaria. This platform, currently in development, aims to leverage cutting-edge technology to enrich traditional Talmud study, making it more accessible and interactive.

## Project Goals

Our mission is to create a seamless bridge between the physical pages of the Talmud and the digital landscape offered by Sefaria. By developing an intuitive platform that supports detailed study with digital enhancements, we aim to:

- Preserve the layout and feel of Tzurat HaDaf while offering digital interactivity.
- Enable precise text mapping and annotation directly on the Talmudic text.
- Facilitate a deeper connection with the text through links to Sefaria's rich database.

## Backend Architecture

The Django-based backend of TzuratLink is designed to manage complex data structures, user interactions, and integrations with external APIs such as Sefaria.

### Models Overview

Our data schema may include models for Pages, Sentences, and BoundingBoxes, structured to support detailed annotations and linkages.

The example code for models.py:
```python
# models.py
from django.db import models

class Page(models.Model):
    tractate_name = models.CharField(max_length=255)
    page_number = models.IntegerField()
    sefaria_ref = models.CharField(max_length=255)
    pdf_path = models.FileField(upload_to='tractate_pages/')

class Sentence(models.Model):
    page = models.ForeignKey(Page, related_name='sentences', on_delete=models.CASCADE)
    sefaria_ref = models.CharField(max_length=255)
    text = models.TextField()

class BoundingBox(models.Model):
    sentence = models.ForeignKey(Sentence, related_name='bounding_boxes', on_delete=models.CASCADE)
    coordinates = models.JSONField()  # Example: {'x0': 100, 'y0': 200, 'x1': 300, 'y1': 400}
```

### PDF Processing with PDFPlumber

To extract text and its coordinates from Talmud pages, we utilize PDFPlumber, ensuring accuracy and reliability over traditional OCR methods.

For example:
```python
# utils.py
import pdfplumber
from .models import Page, Sentence, BoundingBox

def process_pdf_page(page_id):
    page = Page.objects.get(id=page_id)
    with pdfplumber.open(page.pdf_path.path) as pdf:
        first_page = pdf.pages[0]  # Example for the first page
        sentences = first_page.extract_text().split('.')
        for sentence in sentences:
            # Example process to create a sentence and its bounding boxes
            Sentence.objects.create(page=page, text=sentence, sefaria_ref="ExampleRef")
```
### Manual Linking Tool

After that we can manually select sentences on the page, linking them to relevant Sefaria references.

Example for code, that will exapt data from us and parse it for future linking:
```jsx
// ManualLinkingTool.jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const PDFLoader = () => {
  const [pdfUrl, setPdfUrl] = useState('');
  const [tractateName, setTractateName] = useState('');
  const [pageNumber, setPageNumber] = useState('');
  const [category, setCategory] = useState('');
  const [sentences, setSentences] = useState([]);
  const [selectedSentence, setSelectedSentence] = useState('');
  const [boundingBoxes, setBoundingBoxes] = useState([]);
  const [selectedSentences, setSelectedSentences] = useState([]);

  useEffect(() => {
    // Fetch sentences from Sefaria when the user's input changes
    if (pdfUrl && tractateName && pageNumber && category) {
      fetchSentences();
    }
  }, [pdfUrl, tractateName, pageNumber, category]);

  const fetchSentences = async () => {
    try {
      // Make a request to the Sefaria API to fetch sentences based on user input
      const response = await axios.get(
        `https://api.sefaria.org/${category}/${tractateName}.${pageNumber}?context=0`
      );

      // Extract sentences from the response
      const retrievedSentences = response.data.text;

      // Set the retrieved sentences in the state
      setSentences(retrievedSentences);
    } catch (error) {
      console.error('Error fetching sentences:', error);
    }
  };

  const handleSentenceSelect = (sentence) => {
    // Set the currently selected sentence
    setSelectedSentence(sentence);
  };

  const handleBoundingBoxAdd = (boundingBox) => {
    // Add the bounding box to the list
    setBoundingBoxes((prevBoundingBoxes) => [...prevBoundingBoxes, boundingBox]);
  };

  const handleBoundingBoxSave = () => {
    // Save the selected sentence and its corresponding bounding boxes
    const selectedSentenceWithBoundingBoxes = {
      sentence: selectedSentence,
      boundingBoxes: boundingBoxes,
    };

    // Add it to the list of selected sentences
    setSelectedSentences((prevSelectedSentences) => [
      ...prevSelectedSentences,
      selectedSentenceWithBoundingBoxes,
    ]);

    // Clear the selected sentence and bounding boxes
    setSelectedSentence('');
    setBoundingBoxes([]);
  };

  const handleStartOver = () => {
    // Clear all input fields and data to start over
    setPdfUrl('');
    setTractateName('');
    setPageNumber('');
    setCategory('');
    setSentences([]);
    setSelectedSentence('');
    setBoundingBoxes([]);
    setSelectedSentences([]);
  };

  return (
    <div>
      {pdfUrl === '' ? (
        <div>
          <h2>Enter Information to Load PDF</h2>
          <div>
            <label>PDF URL:</label>
            <input
              type="text"
              value={pdfUrl}
              onChange={(e) => setPdfUrl(e.target.value)}
            />
          </div>
          <div>
            <label>Tractate Name:</label>
            <input
              type="text"
              value={tractateName}
              onChange={(e) => setTractateName(e.target.value)}
            />
          </div>
          <div>
            <label>Page Number:</label>
            <input
              type="text"
              value={pageNumber}
              onChange={(e) => setPageNumber(e.target.value)}
            />
          </div>
          <div>
            <label>Category:</label>
            <input
              type="text"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
            />
          </div>
          <button onClick={handlePdfLoad}>Load PDF</button>
        </div>
      ) : (
        <div style={{ display: 'flex' }}>
          <div style={{ flex: 1 }}>
            {/* PDF Viewer Component */}
            {/* You can use 'react-pdf' or any other PDF viewer library here */}
          </div>
          <div style={{ flex: 1 }}>
            <h2>Available Sentences</h2>
            <ul>
              {sentences.map((sentence, index) => (
                <li
                  key={index}
                  onClick={() => handleSentenceSelect(sentence)}
                  style={{ cursor: 'pointer' }}
                >
                  {sentence}
                  {selectedSentence === sentence && (
                    <div>
                      <button onClick={() => handleBoundingBoxAdd()}>Add Bounding Box</button>
                      <button onClick={() => handleBoundingBoxSave()}>Save Bounding Boxes</button>
                    </div>
                  )}
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {selectedSentences.length > 0 && (
        <div>
          <h3>Selected Sentences</h3>
          <ul>
            {selectedSentences.map((item, index) => (
              <li key={index}>
                <p>{item.sentence}</p>
                <ul>
                  {item.boundingBoxes.map((bbox, bboxIndex) => (
                    <li key={bboxIndex}>
                      Bounding Box: {bbox.top}%, {bbox.left}%, {bbox.width}%, {bbox.height}%
                    </li>
                  ))}
                </ul>
              </li>
            ))}
          </ul>
          <button onClick={handleStartOver}>Start Over</button>
        </div>
      )}
    </div>
  );
};

export default PDFLoader;

```

## Frontend Development

Using React, we've built an interactive frontend that renders PDFs, displays bounding boxes, and allows users to interact with the text.

### Interactive PDF Viewer

Our PDF viewer component displays the digitized Talmud pages and overlays interactive bounding boxes for each sentence.

```jsx
// PDFViewer.jsx
import React, { useState, useEffect } from 'react';
import { fetchPageData } from './api';  // Assume this function is implemented to fetch page details

const PDFViewer = ({ tractateName, pageNumber }) => {
    const [pageData, setPageData] = useState(null);

    useEffect(() => {
        fetchPageData(tractateName, pageNumber).then(setPageData);
    }, [tractateName, pageNumber]);

    return (
        <div>
            {pageData ? (
                <div>
                    <img src={`data:image/png;base64,${pageData.pdfBase64}`} alt="Page view" />
                    {/* Logic to render bounding boxes goes here */}
                </div>
            ) : (
                <p>Loading...</p>
            )}
        </div>
    );
};
```

## Conclusion

TzuratLink, with its deep integration with Sefaria and sophisticated text mapping capabilities, represents a significant advancement in the study of Talmudic texts. Through innovative use of technology, we are not only preserving the traditional study methods but also enhancing them, making Talmud study more interactive, accessible, and engaging. As the project progresses through development, we anticipate TzuratLink will become an indispensable tool for scholars and students alike, embodying the perfect fusion of tradition and digital innovation.
