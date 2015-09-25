var modules = modules || {};
modules.inbox = function(options) {
  var nextAt = null,
      nextFetchAt = null,
      initialFailureDelayMs = 500,
      failureDelayMs = initialFailureDelayMs,
      timerId = setInterval(maybeFetch, 1000),
      askingForMore = true,
      failing = false,
      queue = [],
      ack = [],
      metadata = {};

  function fetch() {
    var fetchUrl = "/qs-api/u/" + options.credentials.username + "/pending";

    askingForMore = false;

    console.log("Fetching: " + fetchUrl);

    $.ajax(fetchUrl, {
      username: options.credentials.username,
      password: options.credentials.password,
      data: {
        types: "question,event",
      },
    }).done(onSuccess).fail(onFailure);
  }

  function wasAcked(item) {
    var i = 0;
    while (i < ack.length) {
      if (_.isEqual(item, ack[i])) {
        return true;
      }
      i++;
    }
    return false;
  }

  function pop() {
    if (queue.length > 0) {
      var rv = queue.shift();
      metadata.size -= 1;
      ack.push(rv);
      return rv;
    }
    return null;
  }

  function onSuccess(data) {
    var nextAcked = [];
    metadata.size = data.queue_size;
    if (data.first_trigger) {
      nextAt = metadata.next_at = moment(data.first_trigger * 1000);
    } else {
      failing = true;
    }
    queue = data.pending;

    failureDelayMs = initialFailureDelayMs;

    console.log("Items acked: " + ack.length);
    while (ack.length > 0 && queue.length > 0) {
      if (wasAcked(queue[0])) {
        console.log("Item was acked:");
        console.log(queue[0]);
        nextAcked.push(queue.shift());
      } else {
        break;
      }
    }
    ack = nextAcked;

    if (options.onFetched) {
      options.onFetched();
    }
  }

  function onFailure(req, desc, err) {
    if (req.status === 401) {
      options.onLoginFailure();
    } else {
      options.showMessage({
        style: "danger",
        header: "Error",
        text: "There was an error.",
      });
    }
    failureDelayMs *= 2;
    nextFetchAt = moment().add(failureDelayMs, "milliseconds");
  }

  function askForMore() {
    askingForMore = true;
  }

  function maybeFetch() {
    if (!options.credentials.ok) {
      return;
    }

    if (failing) {
      return;
    }

    if (!askingForMore) {
      return;
    }

    if (nextAt) {
      console.log("triggering fetch in: " + nextAt.diff(moment(), "seconds"));
      nextFetchAt = nextAt;
    }

    if (nextFetchAt !== null && moment() < nextFetchAt) {
      return;
    }

    console.log("ready for fetch");

    fetch();
  }

  return {
    pop: pop,
    metadata: metadata,
    fetch: fetch,
    askForMore: askForMore,
  };
};
