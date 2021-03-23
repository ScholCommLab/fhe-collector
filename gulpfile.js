var gulp = require('gulp');
var browserSync = require('browser-sync').create();
var reload = browserSync.reload;
var exec = require('child_process').exec;
var env = require('gulp-env');


gulp.task('watch', function () {
    gulp.watch("app/templates/*.html").on('change', reload);
    gulp.watch("app/static/**/*.*").on('change', reload);
});

gulp.task('browser-sync', (cb) => {
    browserSync.init({
        proxy: "localhost:5000"
    });
    cb();
});

gulp.task('runserver', (cb) => {
    exec('flask run', function (err, stdout, stderr) {
        console.log(stdout);
        console.log(stderr);
    });
    cb();
});

// gulp.task('nodemon', (cb) => {
//     env({
//         vars: {
//             FLASK_ENV : 'development'
//             FLASK_APP : 'main:app'
//         }
//     });
//     cb();
// });

gulp.task('default', gulp.series('runserver', 'browser-sync', 'watch'));
