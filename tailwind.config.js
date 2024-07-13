module.exports = {
  mode: 'jit',
  purge: [
    './app/templates/**/*.html',
    './app/static/**/*.js',
  ],
  content: [
    './app/templates/**/*.html',
    './app/static/**/*.js',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}