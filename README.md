# TzuratLink: A Comprehensive Platform for Digital Talmud Study

![Powered by Sefaria](/static/img/sefaria-badge.png)

## Introduction

TzuratLink represents a groundbreaking endeavor to integrate the meticulous study of the Talmud with the vast digital resources available through [Sefaria](https://sefaria.org). This platform, currently in development, aims to leverage cutting-edge technology to enrich traditional Talmud study, making it more accessible and interactive. Pages are stored as structured, word-level blocks (rather than page images), with segments linked to Sefaria references for click-to-view commentary.

## Project Goals

Our mission is to create a seamless bridge between the physical pages of the Talmud and the digital landscape offered by Sefaria. By developing an intuitive platform that supports detailed study with digital enhancements, we aim to:

- Preserve the layout and feel of Tzurat HaDaf while offering digital interactivity.
- Enable precise text mapping and annotation directly on the Talmudic text.
- Facilitate a deeper connection with the text through links to Sefaria's rich database.

## Backend Architecture

The Django-based backend of TzuratLink is designed to manage complex data structures, user interactions, and integrations with external APIs such as Sefaria. The frontend is a client-rendered React app (built with webpack, served as a static bundle); Google OAuth sign-in is also integrated.

## Deployment

For production deployment (settings, environment variables, Gunicorn, and reverse proxy), see [DEPLOYMENT.md](DEPLOYMENT.md).

## Conclusion

TzuratLink, with its deep integration with Sefaria and sophisticated text mapping capabilities, represents a significant advancement in the study of Talmudic texts. Through innovative use of technology, we are not only preserving the traditional study methods but also enhancing them, making Talmud study more interactive, accessible, and engaging. As the project progresses through development, we anticipate TzuratLink will become an indispensable tool for scholars and students alike, embodying the perfect fusion of tradition and digital innovation.
