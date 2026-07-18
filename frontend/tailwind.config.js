/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'navy-deep': 'var(--navy-deep)',
        navy: 'var(--navy)',
        sand: 'var(--sand)',
        gold: 'var(--gold)',
        sky: 'var(--sky)',
        ink: 'var(--ink)',
        muted: 'var(--muted)',
      },
      fontFamily: {
        display: ['var(--font-display)', 'serif'],
        body: ['var(--font-body)', 'sans-serif'],
        mono: ['var(--font-mono)', 'monospace'],
      },
    },
  },
  plugins: [],
}
