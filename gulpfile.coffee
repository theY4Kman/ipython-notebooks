gulp = require 'gulp'
watch = require 'gulp-watch'
shell = require 'gulp-shell'
livereload = require 'gulp-livereload'


gulp.task 'default', ['watch']


gulp.task 'build', ->
  gulp.src('*/*.ipynb')
      .pipe(shell('ipython3 nbconvert "<%= file.path %>"'))


gulp.task 'watch', ->
  gulp.watch('*/*.ipynb', ['build'])
