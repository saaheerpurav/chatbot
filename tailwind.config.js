module.exports = {
  mode: 'jit',
  purge: [
    './templates/**/*.html',
    './static/**/*.js',
  ],
  content: [
    './templates/**/*.html',
    './static/**/*.js',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}