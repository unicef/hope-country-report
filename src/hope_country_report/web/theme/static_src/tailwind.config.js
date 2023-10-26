/**
 * This is a minimal config.
 *
 * If you need the full config, get it from here:
 * https://unpkg.com/browse/tailwindcss@latest/stubs/defaultConfig.stub.js
 */
const { colors: defaultColors } = require('tailwindcss/defaultTheme')

module.exports = {
    darkMode: 'class',
    content: [
        /**
         * HTML. Paths to Django template files that will contain Tailwind CSS classes.
         */

        /*  Templates within theme app (<tailwind_app_name>/templates), e.g. base.html. */
        // '../templates/**/*.html',

        /*
         * Main templates directory of the project (BASE_DIR/templates).
         * Adjust the following line to match your project structure.
         */
        // '../../templates/**/*.html',

        /*
         * Templates in other django apps (BASE_DIR/<any_app_name>/templates).
         * Adjust the following line to match your project structure.
         */
        // '../../**/templates/**/*.html',
        // '../**/templates/**/*.html',
        '../../**/templates/**/*.html',
        // '../../../**/templates/**/*.html',
        // '../../../../**/templates/**/*.html',
        // '/Users/sax/Documents/data/PROGETTI/UNICEF/hope-country-report/src/hope_country_report/web/templates/**/*.html',
        /**
         * JS: If you use Tailwind CSS in JavaScript, uncomment the following lines and make sure
         * patterns match your project structure.
         */
        /* JS 1: Ignore any JavaScript in node_modules folder. */
        // '!../../**/node_modules',
        /* JS 2: Process all JavaScript files in the project. */
        // '../../**/*.js',

        /**
         * Python: If you use Tailwind CSS classes in Python, uncomment the following line
         * and make sure the pattern below matches your project structure.
         */
        // '../../**/*.py'
    ],
    theme: {
        extend: {
            colors: {
                unicef: {
                    blue: '#00ADEF',
                    dark: '#003C8F',
                    gray: '#233944',
                },
            //     primary: {
            //         50: '#eff6ff',
            //         100: '#dbeafe',
            //         200: '#bfdbfe',
            //         300: '#93c5fd',
            //         400: '#60a5fa',
            //         500: '#3b82f6',
            //         600: '#2563eb',
            //         700: '#1d4ed8',
            //         800: '#1e40af',
            //         900: '#1e3a8a',
            //     },
            //     secondary: {
            //         50: '#f8fafc',
            //         100: '#f1f5f9',
            //         200: '#e2e8f0',
            //         300: '#cbd5e1',
            //         400: '#94a3b8',
            //         500: '#64748b',
            //         600: '#475569',
            //         700: '#334155',
            //         800: '#1e293b',
            //         900: '#0f172a',
            //     },
            },
        },
        screens: {
            'sm': '640px',
            // => @media (min-width: 640px) { ... }

            'md': '768px',
            // => @media (min-width: 768px) { ... }

            'lg': '1024px',
            // => @media (min-width: 1024px) { ... }

            'xl': '1280px',
            // => @media (min-width: 1280px) { ... }

            '2xl': '1536px',
            // => @media (min-width: 1536px) { ... }
        }
    },
    plugins: [
        /**
         * '@tailwindcss/forms' is the forms plugin that provides a minimal styling
         * for forms. If you don't like it or have own styling for forms,
         * comment the line below to disable '@tailwindcss/forms'.
         */
        require('@tailwindcss/forms'),
        require('@tailwindcss/typography'),
        require('@tailwindcss/line-clamp'),
        require('@tailwindcss/aspect-ratio'),
    ],
}
