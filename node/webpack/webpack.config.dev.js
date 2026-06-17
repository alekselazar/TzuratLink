const path = require('path');

module.exports = {
    entry: "./client.js",
    mode: "development",
    devtool: "source-map",
    watch: true,
    output: {
        path: path.resolve(__dirname, '../../static/js'),
        filename: "bundle.js"
    },
    resolve: {
        extensions: ['.js', '.jsx', '.mjs'],
    },
    module: {
        rules: [
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
}
