from fabric.api import *

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
      run("source '{}bin/activate'".format(envdir))
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
def pushall():
  execute(pack)
  execute(deploy_app)
  execute(deploy_static)
  execute(restart)
