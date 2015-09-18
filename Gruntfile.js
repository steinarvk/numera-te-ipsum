module.exports = function(grunt) {
  grunt.initConfig({
    pkg: grunt.file.readJSON("package.json"),
    bower_concat: {
      all: {
        dest: "static/jsgen/packages.js",
        cssDest: "static/cssgen/packages.css",
      },
    },
  });

  grunt.loadNpmTasks("grunt-bower-concat");
}
