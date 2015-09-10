$(function() {
  $(document.body).append(soy.renderAsElement(qs.core.app));

  var statusbar = modules.statusbar({});
  var credentials = modules.login({hook: onLoggedIn});
  var inbox = modules.inbox({
    credentials: credentials,
    showMessage: showMessage,
    onFetched: onFetched,
    onLoginFailure: onLoginFailure,
  });
  var currentItem = null;
  var itemCallbacks = null;

  if (!credentials.ok) {
    $("#qs-modal-login-dialog").modal("show");
  }

  function showMessage(options) {
    var element = soy.renderAsElement(qs.core.message, options),
        timeUntilDecayMs = 2000,
        decayTimeMs = 1000;
    $("#qs-messages").append(element);

    $(element).fadeTo(2000, 1).fadeTo(1000, 0.0, function() {
      $(element).alert("close");
    });
  }

  function onLoginFailure() {
    credentials.logout();
    statusbar.update({username: null});
    showMessage({
      style: "danger",
      header: "Error.",
      text: "Login failed. Please re-enter credentials.",
    });
    setTimeout(function() {
      $("#qs-modal-login-dialog").modal("show");
    }, 1000);
  }

  function dismissCurrentItem() {
    if (itemCallbacks) {
      itemCallbacks.dismiss();
    }
    itemCallbacks = null;
  }

  function loadNextItem() {
    var item = inbox.pop();

    dismissCurrentItem();

    if (!item) {
      showMessage({
        header: "All done.",
        text: "No more items!",
      });
      inbox.askForMore();
      return;
    }

    itemCallbacks = {};

    if (item.type === "question") {
      currentItem = item;
      presentQuestion(currentItem.question);
      return;
    }

    if (item.type === "event" && item.subtype === "append") {
      currentItem = item;
      presentEvent(currentItem.event_append);
      return;
    }

    if (item.type === "event" && item.subtype === "correct") {
      currentItem = item;
      presentEvent(currentItem.event_correct);
      return;
    }

    showMessage({
      style: "danger",
      header: "Not implemented yet!",
      text: "Loaded unknown kind of item: " + item.type,
    });
  }

  function presentEvent(ev, kind) {
    var main = $("#qs-main-widget")[0],
        username = credentials.username,
        t0 = moment(),
        args = {
          "event": ev.name,
          "default_duration": "30",
          "t0": moment(ev.start).format(),
        },
        control;
    
    console.log(ev);

    if (ev.end === "now") {
      args.t1 = "now";
    } else {
      args.t1 = moment(ev.end).format();
    }

    soy.renderElement(
      main,
      qs.core.event_panel,
      args
    );

    control = modules.eventreporting.init(main);

    itemCallbacks.dismiss = function() {
      control.die();
      console.log("dismissed...");
    }

    itemCallbacks.skipCallback = function() {
      showMessage({
        style: "danger",
        header: "Not implemented yet!",
        text: "Skipping for event reporting isn't implemented yet. " +
              "This is not a real skip, it'll come back when you reload.",
      });
      return true;
    }

    itemCallbacks.submitCallback = function() {
      var result = control.result(),
          reqdata = {};

      console.log("submit value:");
      console.log(result);

      if (result === null) {
        showMessage({
          style: "danger",
          header: "Oops.",
          text: "Looks like you forgot to set a value before submitting!",
        });
        return false;
      }

      if (result.result === "yes") {
        reqdata.state = "on";
        reqdata.start = result.t0.format();
        reqdata.end = result.t1.format();
      } else if (result.result == "no") {
        reqdata.state = "off";
        reqdata.start = control.rangestart().format();
        reqdata.end = control.rangeend().format();
      } else if (result.result == "unknown") {
        reqdata.state = "unknown";
        reqdata.start = control.rangestart().format();
        reqdata.end = control.rangeend().format();
      } else {
        showMessage({
          style: "danger",
          header: "Oops.",
          text: "Internal error (unknown result: " + result.result + ")",
        });
        return false;
      }

      console.log("would submit");
      console.log(reqdata);

      var url = "/qs-api/u/" + username + "/events/" + ev.event_type_id + "/report";
      $.ajax(url, {
        username: username,
        password: credentials.password,
        type: "POST",
        contentType: "application/json; charset: utf-8",
        dataType: "json",
        data: JSON.stringify(reqdata),
      }).done(function() {
        console.log("successfully sent report for " + url);
      }).fail(function() {
        console.log("failed sent report for " + url);
        showMessage({
          style: "danger",
          header: "Error.",
          text: "Failed to post report #" + ev.event_type_id,
        });
      });

      return true;
    }
  }

  function presentQuestion(q) {
    var main = $("#qs-main-widget")[0],
        username = credentials.username,
        t0 = moment(),
        control;

    console.log(q);

    soy.renderElement(
      main,
      qs.core.question_panel,
      {
        text: q.text,
        label_low: q.labels.low,
        label_medium: q.labels.middle,
        label_high: q.labels.high,
      }
    );

    control = modules.slider.init(main);

    itemCallbacks.dismiss = function() {
      control.die();
    }

    itemCallbacks.skipCallback = function() {
      var url = "/qs-api/u/" + username + "/questions/" + q.id + "/skip";

      itemCallbacks = null;
      control.die();

      $.ajax(url, {
          username: username,
          password: credentials.password,
          type: "POST",
      }).done(function() {
        console.log("successfully sent skip for q " + q.id);
      }).fail(function() {
        console.log("failed sent skip for q " + q.id);
      });

      return true;
    }

    itemCallbacks.submitCallback = function() {
      var value = control.getValue(),
          t1 = moment();

      if (value === null) {
        showMessage({
          style: "danger",
          header: "Oops.",
          text: "Looks like you forgot to set a value before submitting!",
        });
        return false;
      }

      itemCallbacks = null;
      control.die();

      if (currentItem.question.id !== q.id) {
        console.log("Sanity check failed");
        return;
      }

      var url = "/qs-api/u/" + username + "/questions/" + q.id + "/answer";
      var data = {
        latency_ms: t1.diff(t0, "milliseconds"),
        value: value * 0.01,
      };

      console.log("sending answer for q " + q.id);
      console.log(data);
      
      $.ajax(url, {
        username: username,
        password: credentials.password,
        type: "POST",
        contentType: "application/json; charset: utf-8",
        dataType: "json",
        data: JSON.stringify(data),
      }).done(function() {
        console.log("successfully sent answer for q " + q.id);
      }).fail(function() {
        console.log("failed to send answer for q " + q.id);
        showMessage({
          style: "danger",
          header: "Error.",
          text: "Failed to post answer for question #" + q.id,
        });
      });

      return true;
    }
  }

  function onFetched() {
    var itemsLeft;

    if (!currentItem) {
      loadNextItem();
    }

    itemsLeft = inbox.metadata.size;

    if (itemCallbacks) {
      console.log("yes we have inbox callbacks");
      itemsLeft++;
    }

    console.log("raw inbox size: " + inbox.metadata.size);
    console.log("modified: " + itemsLeft);

    statusbar.update({
      itemsLeft: itemsLeft,
      nextItemAt: inbox.metadata.next_at,
    });
  }

  function onLoggedIn(credentials) {
    statusbar.update({
      username: credentials.username,
      itemsLeft: 0,
      itemsDone: 0,
    });
  }

  $("#qs-id-logout").click(function() {
    credentials.logout();
    statusbar.update({username: null});
    showMessage({
      style: "danger",
      header: "Bye!",
      text: "Logout successful.",
    });
    setTimeout(function() {
      $("#qs-modal-login-dialog").modal("show");
    }, 1000);
  });

  $("#qs-id-force-refetch").click(function() {
    inbox.fetch();
  });

  $("#qs-id-skip-item-button").click(function() {
    if (itemCallbacks) {
      if (itemCallbacks.skipCallback()) {
        statusbar.itemDone();
        $("#qs-main-widget").find(".panel").hide();
        loadNextItem();
      }
    }
  });

  $("#qs-id-submit-item-button").click(function() {
    if (itemCallbacks) {
      if (itemCallbacks.submitCallback()) {
        statusbar.itemDone();
        $("#qs-main-widget").find(".panel").hide();
        loadNextItem();
      }
    }
  });

  $("#new-event-dialog-submit").click(function() {
    var data = {trigger: {}},
        root = $("#qs-modal-new-event-dialog").modal("hide"),
        checked;

    function goodbye(msg) {
      showMessage(msg);
      root.modal("hide");
    }

    function err(reason) {
      goodbye({
        style: "danger",
        header: "Error adding new event.",
        text: reason,
      });
    }

    data.name = root.find("#new-event-dialog-event-name").val();
    if (data.name.length < 1) {
      return err("event name is required");
    }

    checked = root.find("#new-event-dialog-event-track-duration").find("input:checked");
    if (checked.length !== 1) {
      return err("whether or not to track duration must be selected");
    }
    if (checked[0].name !== "yes" && checked[0].name !== "no") {
      return err("not a valid selection for whether or not to track duration");
    }
    data.use_duration = checked[0].name === "yes";

    data.trigger.delay_s = parseInt(
      root.find("#new-event-dialog-frequency").val(), 10);
    if (typeof data.trigger.delay_s !== "number" || !(data.trigger.delay_s > 0)) {
      return err("valid frequency is required");
    }

    $.ajax("/qs-api/u/" + credentials.username + "/events", {
        username: credentials.username,
        password: credentials.password,
        type: "POST",
        contentType: "application/json; charset: utf-8",
        dataType: "json",
        data: JSON.stringify(data),
    }).done(function() {
      goodbye({
        style: "info",
        header: "Success!",
        text: "Added a new event ('" + data.name + "')",
      });
    }).fail(function() {
      err("network or server-side error adding event");
    });
  });

  $("#new-question-dialog-submit").click(function() {
    var data = {};

    function goodbye(msg) {
      showMessage(msg);
      $("#qs-modal-new-question-dialog").modal("hide");
    }

    function err(reason) {
      goodbye({
        style: "danger",
        header: "Error adding new question.",
        text: reason,
      });
    }

    data.question = $("#new-question-dialog-question-text").val();
    if (data.question.length < 1) {
      return err("question text is required");
    }

    data.low = $("#new-question-dialog-low-label").val();
    if (data.low.length < 1) {
      return err("lower-extreme label text is required");
    }

    data.high = $("#new-question-dialog-high-label").val();
    if (data.high.length < 1) {
      return err("upper-extreme label text is required");
    }

    data.middle = $("#new-question-dialog-middle-label").val();
    if (!data.middle) {
      delete data.middle;
    }

    data.delay = $("#new-question-dialog-frequency").val();
    if (data.delay.length < 1) {
      return err("frequency is required");
    }

    $.ajax("/qs-api/u/" + credentials.username + "/questions", {
        username: credentials.username,
        password: credentials.password,
        type: "POST",
        contentType: "application/json; charset: utf-8",
        dataType: "json",
        data: JSON.stringify(data),
    }).done(function() {
      goodbye({
        style: "info",
        header: "Success!",
        text: "Added a new question ('" + data.question + "')",
      });
    }).fail(function() {
      err("network error");
    });

  });

  $("#qs-id-experiment").click(function() {
    dismissCurrentItem();

    var gs = {
      "event": "meditation",
      "default_duration": "30",
    };
    if (Math.random() > 0.5) {
      gs.t0 = moment().subtract(37, "hours").format();
      gs.t1 = moment().subtract(3, "hours").format();
    } else {
      gs.t0 = moment().subtract(37, "seconds").format();
    }
    $("#qs-main").html(soy.renderAsElement(qs.core.event_panel, gs));
    todoInitializeExperiment();
  });
});
