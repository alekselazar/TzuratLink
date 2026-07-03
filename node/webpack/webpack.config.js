const path = require('path');

module.exports = (env, argv) => {
    const isProduction = argv.mode === 'production';

    return {
        entry: "./client.js",
        mode: isProduction ? "production" : "development",
        devtool: isProduction ? false : "source-map",
        watch: process.env.WATCH === 'true',
        output: {
            path: path.resolve(__dirname, '../../static/js'),
            filename: "bundle.js"
        },
        resolve: {
            extensions: ['.js', '.jsx', '.mjs'],
        },
        module: {
            rules: [
                // Allow webpack to process .mjs files from node_modules (needed for pdfjs-dist v4)
                {
                    test: /\.mjs$/,
                    include: /node_modules/,
                    type: 'javascript/auto',
                },
                {
                    test: /\.(js|jsx)$/,
                    exclude: /node_modules/,
                    use: {
                        loader: 'babel-loader'
                    }
                },
                {
                    test: /\.css$/,
                    use: [
                        { loader: 'style-loader' },
                        { loader: 'css-loader' }
                    ]
                }
            ]
        },
        watchOptions: {
            ignored: /node_modules/,
            aggregateTimeout: 300,
            poll: 1000
        }
    };
}
