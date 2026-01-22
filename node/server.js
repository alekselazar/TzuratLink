require('@babel/register')({
    presets: ['@babel/preset-env', '@babel/preset-react'],
    plugins: ['@babel/plugin-syntax-jsx']
});
require('ignore-styles').default(['.css', '.sass', '.scss']);

const express = require('express');
const React = require('react');
const ReactDOMServer = require('react-dom/server');
const ReaderApp = require('./components/ReaderApp').default;
const PDFReader = require('./components/PDFReader').default;

const app = express();
const PORT = 3000;

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// SSR endpoint
app.post('/render', (req, res) => {
    try {
        const { component, props } = req.body;
        
        let AppComponent;
        if (component === 'PDFReader') {
            AppComponent = PDFReader;
        } else {
            AppComponent = ReaderApp;
        }
        
        // Render React component to HTML string
        const html = ReactDOMServer.renderToString(
            React.createElement(AppComponent, props)
        );
        
        res.json({
            html: html,
            props: props
        });
    } catch (error) {
        console.error('SSR Error:', error);
        res.status(500).json({
            error: 'SSR rendering failed',
            message: error.message
        });
    }
});

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({ status: 'ok' });
});

app.listen(PORT, () => {
    console.log(`SSR Server running on port ${PORT}`);
});
