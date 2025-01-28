# TzuratLink: A Comprehensive Platform for Digital Talmud Study

[Powered by Sefaria](https://camo.githubusercontent.com/ab55fa936da3be90f34d670ef264e00526430ccadec2316e5fe18826f98dcdbe/68747470733a2f2f7777772e736566617269612e6f72672f7374617469632f696d672f706f77657265642d62792d736566617269612d62616467652e706e673f6d "bage")

## Introduction

TzuratLink represents a groundbreaking endeavor to integrate the meticulous study of the Talmud with the vast digital resources available through [Sefaria](https://sefaria.org). This platform, currently in development, aims to leverage cutting-edge technology to enrich traditional Talmud study, making it more accessible and interactive. On this stage we developed Editor App for simple manual linking and now we are working on linking Talmud PDFs to Sefaria texts.

## Project Goals

Our mission is to create a seamless bridge between the physical pages of the Talmud and the digital landscape offered by Sefaria. By developing an intuitive platform that supports detailed study with digital enhancements, we aim to:

- Preserve the layout and feel of Tzurat HaDaf while offering digital interactivity.
- Enable precise text mapping and annotation directly on the Talmudic text.
- Facilitate a deeper connection with the text through links to Sefaria's rich database.

## Backend Architecture

The Django-based backend of TzuratLink is designed to manage complex data structures, user interactions, and integrations with external APIs such as Sefaria.

### Manual Linking Tool
Manual linking tool is represented with ```EditorApp``` React component with django backend ```editor``` app. 
After that we can manually select sentences on the page, linking them to relevant Sefaria references.

### Translations
We are using [OpenAI API](https://platform.openai.com/docs/overview) to generate and then edit translations to talmudic texts. It is part of Editor App.

## Conclusion

TzuratLink, with its deep integration with Sefaria and sophisticated text mapping capabilities, represents a significant advancement in the study of Talmudic texts. Through innovative use of technology, we are not only preserving the traditional study methods but also enhancing them, making Talmud study more interactive, accessible, and engaging. As the project progresses through development, we anticipate TzuratLink will become an indispensable tool for scholars and students alike, embodying the perfect fusion of tradition and digital innovation.
