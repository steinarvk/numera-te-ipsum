from fabric.api import *

import glob

@task
def setupdeps():
  sudo("apt-get install libyaml-dev")

@task
def restart():
  sudo("/etc/init.d/nginx restart", shell=False)
  sudo("/sbin/restart uwsgi", shell=False)

@task
def pack():
  local("python setup.py sdist --formats=gztar", capture=False)
  local("rm -rf QuantifiedSelfServer.egg-info/")

@task
def download_soy():
  local("mkdir -p soylib/")
  with lcd("soylib"):
    local("wget \"https://dl.google.com/closure-templates/closure-templates-for-javascript-latest.zip\"")
    local("unzip closure-templates-for-javascript-latest.zip")

@task
def soygen():
  sources = ",".join(glob.glob("soy/*.soy"))
  local("java -jar soylib/SoyToJsSrcCompiler.jar --outputPathFormat closurejs/gen/templates.js --shouldProvideRequireSoyNamespaces --shouldGenerateJsdoc --srcs " + sources)

@task
def jscompile():
  local("java -jar closurejs/compiler.jar --js closurejs/gen/*.js --js closurejs/src/*.js --js closurejs/closure-library/closure/goog/ --closure_entry_point qs.main --js soylib/soyutils_usegoog.js --compilation_level SIMPLE --js_output_file static/jsgen/templates.js")

@task
def deploy_app():
  dist = local("python setup.py --fullname", capture=True).strip()
  deploydir = "/tmp/deploy.{}.generated/".format(dist)
  envdir = "/var/www/qs/env/"
  deployfile = deploydir + dist + ".tar.gz"
  run("rm -rf '{}'".format(deploydir))
  run("mkdir -p '{}'".format(deploydir))
  put("dist/{}.tar.gz".format(dist), deployfile)
  with cd(deploydir):
    run("tar xvfz '{}'".format(deployfile))
    with cd(dist):
      run("{}bin/python setup.py install --force".format(envdir))

@task
def deploy_static():
  local_filename = "dist/qs-static-files.tar.gz"
  remote_filename = "/tmp/qs-static-files.tar.gz"
  deploydir = "/var/www/qs/static/"
  local("tar cvfz '{}' static/".format(local_filename))
  put(local_filename, remote_filename)
  run("rm -rf /var/www/qs/static.new")
  run("mkdir /var/www/qs/static.new")
  run("tar xvfz '{}' -C /var/www/qs/static.new".format(remote_filename))
  run("rm -rf /var/www/qs/static.backup")
  run("mv /var/www/qs/static /var/www/qs/static.backup || true")
  run("mv /var/www/qs/static.new/static /var/www/qs/static")

@task
def upgrade_production_db():
  run("rm -rf /tmp/quantifiedself.db-upgrade.generated")
  run("mkdir -p /tmp/quantifiedself.db-upgrade.generated")
  local("git archive master -o dist/quantifiedself-full-archive.tar.gz") 
  put("dist/quantifiedself-full-archive.tar.gz",
      "/tmp/quantifiedself.db-upgrade.generated/qs-archive.tar.gz")
  with cd("/tmp/quantifiedself.db-upgrade.generated"):
    run("tar xvfz qs-archive.tar.gz")
    run("virtualenv env")
    envdir = "/tmp/quantifiedself.db-upgrade.generated/env/"
    run("{}bin/pip install pyyaml alembic".format(envdir)) # urgh! TODO
    run("{}bin/python setup.py install".format(envdir))
    run("PYTHONPATH=$PYTHONPATH:. QS_CONFIG_FILE=/var/www/qs/config.yaml {}bin/alembic upgrade head".format(envdir))


@task
def pushall():
  execute(pack)
  execute(deploy_app)
  execute(deploy_static)
  execute(restart)
