var forcePending = false;

$(function() {
  var slider = addSlider($(".choiceSlider"), {
    onChange: function(val) {
      $("#submitButton").prop("disabled", false);
    },
  });
  var currentQ;
  var username, password;
  var t0;
  var statusbar = {};

  function setStatus(key, val) {
    var msgs = [];

    statusbar[key] = val;

    if (statusbar.queueSizeMessage !== undefined) {
      msgs.push(statusbar.queueSizeMessage);
    }

    if (statusbar.answerTimeMs !== undefined) {
      msgs.push("Last answer time: " + statusbar.answerTimeMs + "ms");
    }

    if (statusbar.answer !== undefined) {
      msgs.push("Last answer: " + statusbar.answer + "%");
    }

    $("#message").html(msgs.join(", "));
  }

  function fetchQuestion() {
      var url = "/qs-api/u/" + username + "/pending";
      $("#refetchButton").show();
      $.ajax(url, {
          username: username,
          password: password,
          data: {
            limit: 1,
            force: forcePending,
            types: "question",
          },
      }).done(function(data) {
          var n = data.queue_size,
              now = new Date().getTime() / 1000.0,
              first_in = data.first_trigger - now,
              msg;
          if (n > 0) {
            loadQuestion(data.pending[0].question);
            $("#refetchButton").hide();
            if (n == 1) {
              msg = "1 item pending";
            } else {
              msg = "" + n + " items pending";
            }
          } else if (first_in && first_in > 0) {
            msg = "No items pending (next ";
            if (first_in < 60) {
              msg += "in " + Math.round(first_in) + " seconds";
            } else {
              msg += moment().add(first_in, "seconds").fromNow();
            }
            msg += ")";
          } else {
            msg = "No items pending";
          }
          setStatus("queueSizeMessage", msg);
          t0 = new Date().getTime();
      });
  }
  function skipQuestion(q) {
      var url = "/qs-api/u/" + username + "/questions/" + q.id + "/skip";
      $.ajax(url, {
          username: username,
          password: password,
          type: "POST",
      }).done(function() {
          fetchQuestion();
      });
  }
  function postAnswer(q, v) {
      var url = "/qs-api/u/" + username + "/questions/" + q.id + "/answer";
      var t1 = new Date().getTime(),
          latency = t1 - t0;
      var data = JSON.stringify({
          value: v * 0.01,
          latency_ms: latency,
      });
      setStatus("answer", v);
      setStatus("answerTimeMs", latency);
      $("#surveyForm").hide();
      $.ajax(url, {
          username: username,
          password: password,
          type: "POST",
          contentType: "application/json; charset: utf-8",
          dataType: "json",
          data: data,
      }).done(function() {
          fetchQuestion();
      });
  }
  function loadQuestion(q) {
    $("#questionText").html(q.text);
    $("#leftLabel").html(q.labels.low);
    $("#centerLabel").html(q.labels.middle || "");
    $("#rightLabel").html(q.labels.high);
    $("#surveyForm").show();
    $("#refetchButton").hide();
    slider.reset();
    $("#submitButton").prop("disabled", true);
    currentQ = q;
  }
  $("#authButton").click(function() {
    username = $("#username").val();
    password = $("#password").val();
    $("#authForm").hide();
    $("#refetchButton").show();
    fetchQuestion();
  });
  $("#refetchButton").click(function() {
    fetchQuestion();
  });
  $("#submitButton").click(function() {
    postAnswer(currentQ, slider.getValue());
    currentQ = null;
  });
  $("#skipButton").click(function() {
    skipQuestion(currentQ);
    currentQ = null;
  });
});
