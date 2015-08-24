var modules = modules || {};
modules.statusbar = function(options) {
  var sessionIdleLimitSeconds = 60,
      state = {};

  function setProgressBar(ok, left, done) {
    var args = {}, now = moment();

    if (ok) {
      $("#qs-id-queue-progress-bar").width(100 * done/(left+done) + "%");
      args.done = "" + done;
      args.total = "" + (left + done);
    }

    if (!left && state.nextItemAt) {
      args.next_in = modules.util.formatTimeDiff(now, state.nextItemAt);
    }

    soy.renderElement($("#qs-id-queue-progress-label")[0],
      qs.core.queue_progress_bar_label,
      args);
  }

  function update(diff) {
    console.log(diff);
    jQuery.extend(state, diff);
    render();
  }

  function renderTimers() {
    var estTotal = "N/A",
        spent = "N/A",
        latency = "N/A",
        now = moment(),
        sessionTimeoutRate = null;

    if (!state.sessionOngoing) {
      if (state.sessionStart && state.sessionEnd) {
        estTotal = "finished";
        spent = modules.util.formatTimeDiff(state.sessionStart, state.sessionEnd);
      } else {
        estTotal = spent = "no session";
      }

      sessionTimeoutRate = 0.0;
    } else {
      if (state.sessionRefresh) {
        sessionTimeoutRate = 1.0 - now.diff(state.sessionRefresh, "milliseconds") / (1000 * sessionIdleLimitSeconds);
        sessionTimeoutRate = Math.max(0, Math.min(1, sessionTimeoutRate));
      }

      if (state.sessionStart) {
        spent = modules.util.formatTimeDiff(state.sessionStart, now);
      }

      if (state.sessionStart && state.sessionEstimatedEnd) {
        estTotal = modules.util.formatTimeDiff(state.sessionStart,
          state.sessionEstimatedEnd);
      }
    }

    if (state.itemLatencyMs) {
      latency = (state.itemLatencyMs/1000.0).toFixed(2) + "s";
    }

    $("#qs-id-session-timeout-progress-bar").width(100 * sessionTimeoutRate + "%");

    soy.renderElement(
      $("#qs-id-last-item-processing-time")[0],
      qs.core.session_timer_label,
      {
        key: "Last",
        value: latency,
      }
    );

    soy.renderElement(
      $("#qs-id-session-time-spent")[0],
      qs.core.session_timer_label,
      {
        key: "Spent",
        value: spent,
      });

    soy.renderElement(
      $("#qs-id-session-estimated-time-left")[0],
      qs.core.session_timer_label,
      {
        key: "Total",
        value: estTotal,
      });
  }

  function renderUsername() {
    var text = state.username || "<no user>";

    soy.renderElement($("#qs-header-username-label")[0],
      qs.core.username_label,
      {username: text});
  }

  function renderQueueProgress() {
    if (state.itemsLeft >= 0 && state.itemsDone >= 0) {
      setProgressBar(true, state.itemsLeft, state.itemsDone);
    } else {
      setProgressBar(false, null, null);
    }
  }

  function render() {
    renderTimers();
    renderUsername();
    renderQueueProgress();
  }

  function get() {
    return state;
  }

  function setupQueue(total, done) {
    state.itemsDone = done || 0;
    state.itemsLeft = total - state.itemsDone;
    render();
  }

  function itemDone() {
    var now = moment();

    if (!state.sessionOngoing) {
      startSession();
    }
    
    state.itemLatencyMs = now.diff(state.sessionRefresh, "milliseconds");
    state.itemsLeft -= 1;
    state.itemsDone += 1;
    state.sessionRefresh = now;

    if (state.itemsLeft <= 0) {
      endSession();
    }

    render();
  }

  function startSession() {
    state.sessionStart = moment();
    state.sessionRefresh = moment();
    state.sessionOngoing = true;
    state.itemsDone = 0;
    calculate();
    render();
  }

  function endSession() {
    state.sessionOngoing = false;
    state.sessionEnd = moment();
    calculate();
    render();
  }

  function calculate() {
    var now = moment(),
        itemsPerSecond,
        secondsLeft;

    if (!state.sessionOngoing) {
      return;
    }

    state.sessionLengthMs = now.diff(state.sessionStart, "milliseconds");
    state.sessionTimeSinceRefreshMs = now.diff(state.sessionRefresh, "milliseconds");

    itemsPerMs = state.itemsDone / state.sessionLengthMs;
    state.sessionEstimatedEnd = now.add(state.itemsLeft / itemsPerMs, "milliseconds");

    if (state.sessionTimeSinceRefresh > sessionIdleLimitSeconds) {
      endSession();
    }
  }

  setInterval(function() {
    calculate();
    render();
  }, 250);

  return {
    current: get,
    update: update,
    setupQueue: setupQueue,
    itemDone: itemDone,
  };
};
