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
  var elementsLeft = 0;
  var elementsProcessed = 0;
  var lastElementProcessed = null;
  var sessionBegan = null;

  function fmtSeconds(s) {
    var h, m, rv = [];

    if (s >= Infinity) {
      return "\u221e";
    }

    s = Math.round(s);
    h = Math.floor(s / 3600);
    s -= h * 3600;
    m = Math.floor(s / 60);
    s -= m * 60;

    if (h > 0) {
      rv.push("" + h + "h");
    }

    if (m > 0) {
      rv.push("" + m + "m");
    }

    if (s > 0) {
      rv.push("" + s + "s");
    }

    return rv.join(" ");
  }

  function updateProgress() {
    var sessionInProgress = false,
        speed, timeLeft,
        elTotal = elementsLeft + elementsProcessed;

    if (lastElementProcessed !== null) {
      sessionInProgress = moment().diff(lastElementProcessed, 'seconds') < 60;
    }

    if (!sessionInProgress) {
      elementsProcessed = 0;
      lastElementProcessed = null;
      sessionBegan = null;

      setStatus("progressPct", null);
    } else {
      if (sessionBegan === null) {
        sessionBegan = moment();
      }

      setStatus("progressDurationText",
        fmtSeconds(moment().diff(sessionBegan, 'seconds')));
      setStatus("progressProcessed", elementsProcessed);
      setStatus("progressTotal", elTotal);
      if (elementsLeft === 0) {
        setStatus("progressPct", 100);
        setStatus("progressEtaText", "Done!");
      } else {
        setStatus("progressPct",
          (100 * elementsProcessed / elTotal).toFixed(2));
        speed = elementsProcessed / moment().diff(sessionBegan, 'seconds');
        setStatus("progressEtaText", fmtSeconds(elementsLeft / speed));
      }
    }
  }

  window.setInterval(updateProgress, 10000);

  function updateProgressProcessed(nProcessed, nSize) {
    lastElementProcessed = moment();
    elementsProcessed += nProcessed;
    elementsLeft = nSize;
    updateProgress();
  }

  function setStatus(key, val) {
    var msgs = [];

    statusbar[key] = val;

    $("#message").html(soy.renderAsElement(qs.question.statusbar, statusbar));
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
          }
          updateProgressProcessed(0, n);
          setStatus("queueSize", n);
          setStatus("timeUntilNextText", fmtSeconds(first_in));
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
          updateProgressProcessed(1, elementsLeft - 1);
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
      setStatus("answerPct", v);
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
          updateProgressProcessed(1, elementsLeft - 1);
          fetchQuestion();
      });
  }
  function loadQuestion(q) {
    console.log("loadQuestion!");
    console.log(q);
    $("#questionText").html(soy.renderAsElement(
      qs.question.question, {text: q.text}));
    $("#leftLabel").html(soy.renderAsElement(
      qs.question.label, {text: q.labels.low}));
    $("#centerLabel").html(soy.renderAsElement(
      qs.question.label, {text: q.labels.middle || ""}));
    $("#rightLabel").html(soy.renderAsElement(
      qs.question.label, {text: q.labels.high}));
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
    var val = slider.getValue();
    if (val !== null) {
      postAnswer(currentQ, slider.getValue());
      currentQ = null;
    }
  });
  $("#skipButton").click(function() {
    skipQuestion(currentQ);
    currentQ = null;
  });
});
