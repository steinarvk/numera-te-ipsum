var modules = modules || {};
modules.login = function(options) {
  options = options || {};

  var credentials = {ok: false, username: null, password: null};

  function login(username_, password_, acceptHook) {
    if (!username_ || !password_) {
      return false;
    }

    if (username_.length <= 0 && password_.length <= 0) {
      return false;
    }

    // TODO maybe validate

    acceptLogin(username_, password_);
    if (acceptHook) {
      acceptHook();
    }

    return true;
  }

  function acceptLogin(username_, password_) {
    if (Modernizr.localstorage) {
      localStorage["qs-username"] = username_;
      localStorage["qs-password"] = password_;
    }

    credentials.username = username_;
    credentials.password = password_;
    credentials.ok = true;

    if (options.hook) {
      options.hook(credentials);
    }
  }

  function init() {
    $("#login-dialog-submit").on("click", function() {
      login($("#login-dialog-username").val(),
            $("#login-dialog-password").val(),
            function() {
              $("#qs-modal-login-dialog").modal("hide");
              $("#login-dialog-password").val("");
            });
    });

    if (credentials.username) {
      $("#login-dialog-username").val(credentials.username);
    }

    $("#qs-modal-login-dialog").on("shown.bs.modal", function() {
      if (!$("#login-dialog-username")) {
        $("#login-dialog-username").focus();
      } else {
        $("#login-dialog-password").focus();
      }
    });
  }

  if (Modernizr.localstorage) {
    login(localStorage["qs-username"], localStorage["qs-password"]);
  }

  init();

  credentials.logout = function() {
    credentials.username = null;
    credentials.password = null;
    credentials.ok = false;
    if (Modernizr.localstorage) {
      delete localStorage["qs-username"];
      delete localStorage["qs-password"];
    }
  }

  return credentials;
};
