// This file was automatically generated from question.soy.
// Please don't edit this file by hand.

/**
 * @fileoverview Templates in namespace qs.question.
 */

goog.provide('qs.question');

goog.require('soy');
goog.require('soydata');


qs.question.question = function(opt_data, opt_ignored) {
  return soydata.VERY_UNSAFE.ordainSanitizedHtml('<p class="qs_survey_question">' + soy.$$escapeHtml(opt_data.text) + '</p>');
};
if (goog.DEBUG) {
  qs.question.question.soyTemplateName = 'qs.question.question';
}


qs.question.label = function(opt_data, opt_ignored) {
  return soydata.VERY_UNSAFE.ordainSanitizedHtml('<p class="qs_survey_question_label">' + soy.$$escapeHtml(opt_data.text) + '</p>');
};
if (goog.DEBUG) {
  qs.question.label.soyTemplateName = 'qs.question.label';
}


qs.question.statusbar = function(opt_data, opt_ignored) {
  return soydata.VERY_UNSAFE.ordainSanitizedHtml(((opt_data.queueSize != null) ? '<p class="qs_statusbar_section"><b>Queue</b>:' + ((opt_data.queueSize == 0) ? 'No items pending (next in ' + soy.$$escapeHtml(opt_data.timeUntilNextText) + ').' : (opt_data.queueSize == 1) ? '1 item pending.' : soy.$$escapeHtml(opt_data.queueSize) + ' items pending.') + '</p>' : '') + ((opt_data.progressPct != null && opt_data.progressEtaText != null && opt_data.progressDurationText != null && opt_data.progressProcessed != null && opt_data.progressTotal != null) ? '<p class="qs_statusbar_section"><b>Session length:</b> ' + soy.$$escapeHtml(opt_data.progressDurationText) + '</p><p class="qs_statusbar_section"><b>Progress</b>: ' + soy.$$escapeHtml(opt_data.progressPct) + '% (' + soy.$$escapeHtml(opt_data.progressProcessed) + '/' + soy.$$escapeHtml(opt_data.progressTotal) + ')</p><p class="qs_statusbar_section"><b>ETA</b>: ' + soy.$$escapeHtml(opt_data.progressEtaText) + '</p>' : '') + ((opt_data.answerPct != null && opt_data.answerTimeMs != null) ? '<p class="qs_statusbar_section"><b>Last answer</b>:' + soy.$$escapeHtml(opt_data.answerPct) + '% (after ' + soy.$$escapeHtml(opt_data.answerTimeMs) + 'ms)</p>' : ''));
};
if (goog.DEBUG) {
  qs.question.statusbar.soyTemplateName = 'qs.question.statusbar';
}

;
// This file was automatically generated from qs.soy.
// Please don't edit this file by hand.

/**
 * @fileoverview Templates in namespace qs.core.
 */

goog.provide('qs.core');

goog.require('soy');
goog.require('soydata');
goog.require('goog.asserts');


qs.core.string = function(opt_data, opt_ignored) {
  goog.asserts.assert(goog.isString(opt_data.text) || (opt_data.text instanceof goog.soy.data.SanitizedContent), "expected param 'text' of type string|goog.soy.data.SanitizedContent.");
  var text = /** @type {string|goog.soy.data.SanitizedContent} */ (opt_data.text);
  return soydata.VERY_UNSAFE.ordainSanitizedHtml(soy.$$escapeHtml(text));
};
if (goog.DEBUG) {
  qs.core.string.soyTemplateName = 'qs.core.string';
}


qs.core.panel = function(opt_data, opt_ignored) {
  goog.asserts.assert(goog.isString(opt_data.title) || (opt_data.title instanceof goog.soy.data.SanitizedContent), "expected param 'title' of type string|goog.soy.data.SanitizedContent.");
  var title = /** @type {string|goog.soy.data.SanitizedContent} */ (opt_data.title);
  goog.asserts.assert((opt_data.content instanceof soydata.SanitizedHtml) || (opt_data.content instanceof soydata.UnsanitizedText) || goog.isString(opt_data.content), "expected param 'content' of type soydata.SanitizedHtml.");
  var content = /** @type {soydata.SanitizedHtml} */ (opt_data.content);
  return soydata.VERY_UNSAFE.ordainSanitizedHtml('<div class="panel panel-default"><div class="panel-heading">' + soy.$$escapeHtml(title) + '</div><div class="panel-body">' + soy.$$escapeHtml(content) + '</div></div>');
};
if (goog.DEBUG) {
  qs.core.panel.soyTemplateName = 'qs.core.panel';
}


qs.core.slider = function(opt_data, opt_ignored) {
  return soydata.VERY_UNSAFE.ordainSanitizedHtml('<div class="progress qs-progress-slider"><div class="progress-bar qs-progress-slider" role="progressbar" ></div><span class="qs-progress-label"></span></div>');
};
if (goog.DEBUG) {
  qs.core.slider.soyTemplateName = 'qs.core.slider';
}


qs.core.event_panel = function(opt_data, opt_ignored) {
  goog.asserts.assert(goog.isString(opt_data.event) || (opt_data.event instanceof goog.soy.data.SanitizedContent), "expected param 'event' of type string|goog.soy.data.SanitizedContent.");
  var event = /** @type {string|goog.soy.data.SanitizedContent} */ (opt_data.event);
  goog.asserts.assert(goog.isString(opt_data.t0) || (opt_data.t0 instanceof goog.soy.data.SanitizedContent), "expected param 't0' of type string|goog.soy.data.SanitizedContent.");
  var t0 = /** @type {string|goog.soy.data.SanitizedContent} */ (opt_data.t0);
  goog.asserts.assert(opt_data.kind == null || (opt_data.kind instanceof goog.soy.data.SanitizedContent) || goog.isString(opt_data.kind), "expected param 'kind' of type null|string|undefined.");
  var kind = /** @type {null|string|undefined} */ (opt_data.kind);
  goog.asserts.assert(opt_data.t1 == null || (opt_data.t1 instanceof goog.soy.data.SanitizedContent) || goog.isString(opt_data.t1), "expected param 't1' of type null|string|undefined.");
  var t1 = /** @type {null|string|undefined} */ (opt_data.t1);
  goog.asserts.assert(opt_data.default_duration == null || (opt_data.default_duration instanceof goog.soy.data.SanitizedContent) || goog.isString(opt_data.default_duration), "expected param 'default_duration' of type null|string|undefined.");
  var default_duration = /** @type {null|string|undefined} */ (opt_data.default_duration);
  return soydata.VERY_UNSAFE.ordainSanitizedHtml(qs.core.panel(soy.$$augmentMap(opt_data, {title: 'Report binary event', content: soydata.VERY_UNSAFE.$$ordainSanitizedHtmlForInternalBlocks('<div>Event: <span class="qs-event-desc">' + soy.$$escapeHtml(event) + '</span></div><input type="hidden" class="qs-event-t0" value="' + soy.$$escapeHtmlAttribute(t0) + '"/><input type="hidden" class="qs-event-t1" value="' + soy.$$escapeHtmlAttribute(t1) + '"/><input type="hidden" class="qs-event-kind" value="' + soy.$$escapeHtmlAttribute(kind) + '"/><div>Did this occur between: <span class="qs-event-query-begin-time"></span> and <span class="qs-event-query-end-time"></span>, a time span of <span class="qs-event-query-time-duration"></span>?</div><div class="btn-group qs-event-options" data-toggle="buttons"><label class="btn btn-primary"><input type="radio" name="options" class="qs-event-yes-at" autocomplete="off">Yes, at...</label><label class="btn btn-primary"><input type="radio" name="options" class="qs-event-unknown" autocomplete="off">Unsure</label><label class="btn btn-primary"><input type="radio" name="options" class="qs-event-no" autocomplete="off">No</label></div>' + qs.core.modal({title: 'Select start time of event: ' + event, id: 'event-datetimepicker', close_button: true, content: soydata.VERY_UNSAFE.$$ordainSanitizedHtmlForInternalBlocks('<div class="qs-event-datetimepicker"></div>'), footer_content: soydata.VERY_UNSAFE.$$ordainSanitizedHtmlForInternalBlocks('' + qs.core.button({id: 'qs-event-accept-datetimepicker', class: 'qs-event-accept-datetimepicker', style: 'success', text: 'Accept'}))}) + '<div style="display: none;" class="qs-event-yes-details">From<input type="hidden" id="qs-event-start-datetime-hidden"><button type="button" class="btn btn-info qs-event-details-start-time" data-toggle="modal" data-target="#qs-modal-event-datetimepicker" >&lt;time&gt;</button>for <input size="3" type="text" class="qs-event-duration-mins"' + ((default_duration != null) ? 'value="' + soy.$$escapeHtmlAttribute(default_duration) + '"' : '') + '> minutes (until <span class="qs-event-end-time"></span>)</div></div>')})));
};
if (goog.DEBUG) {
  qs.core.event_panel.soyTemplateName = 'qs.core.event_panel';
}


qs.core.question_panel = function(opt_data, opt_ignored) {
  goog.asserts.assert(goog.isString(opt_data.text) || (opt_data.text instanceof goog.soy.data.SanitizedContent), "expected param 'text' of type string|goog.soy.data.SanitizedContent.");
  var text = /** @type {string|goog.soy.data.SanitizedContent} */ (opt_data.text);
  goog.asserts.assert(opt_data.label_low == null || (opt_data.label_low instanceof goog.soy.data.SanitizedContent) || goog.isString(opt_data.label_low), "expected param 'label_low' of type null|string|undefined.");
  var label_low = /** @type {null|string|undefined} */ (opt_data.label_low);
  goog.asserts.assert(opt_data.label_medium == null || (opt_data.label_medium instanceof goog.soy.data.SanitizedContent) || goog.isString(opt_data.label_medium), "expected param 'label_medium' of type null|string|undefined.");
  var label_medium = /** @type {null|string|undefined} */ (opt_data.label_medium);
  goog.asserts.assert(opt_data.label_high == null || (opt_data.label_high instanceof goog.soy.data.SanitizedContent) || goog.isString(opt_data.label_high), "expected param 'label_high' of type null|string|undefined.");
  var label_high = /** @type {null|string|undefined} */ (opt_data.label_high);
  return soydata.VERY_UNSAFE.ordainSanitizedHtml(qs.core.panel(soy.$$augmentMap(opt_data, {title: 'Question', content: soydata.VERY_UNSAFE.$$ordainSanitizedHtmlForInternalBlocks('<div class="qs-upper-content">' + soy.$$escapeHtml(text) + '</div><div class="qs-lower-content"><table><tr><td colspan="3">' + qs.core.slider(null) + ((label_low != null || label_medium != null || label_high != null) ? '<tr><td class="qs-left-label">' + ((label_low != null) ? soy.$$escapeHtml(label_low) : '') + '<td class="qs-middle-label">' + ((label_medium != null) ? soy.$$escapeHtml(label_medium) : '') + '<td class="qs-right-label">' + ((label_high != null) ? soy.$$escapeHtml(label_high) : '') : '') + '</table></div>')})));
};
if (goog.DEBUG) {
  qs.core.question_panel.soyTemplateName = 'qs.core.question_panel';
}


qs.core.button = function(opt_data, opt_ignored) {
  goog.asserts.assert(goog.isString(opt_data.text) || (opt_data.text instanceof goog.soy.data.SanitizedContent), "expected param 'text' of type string|goog.soy.data.SanitizedContent.");
  var text = /** @type {string|goog.soy.data.SanitizedContent} */ (opt_data.text);
  goog.asserts.assert(opt_data.style == null || (opt_data.style instanceof goog.soy.data.SanitizedContent) || goog.isString(opt_data.style), "expected param 'style' of type null|string|undefined.");
  var style = /** @type {null|string|undefined} */ (opt_data.style);
  goog.asserts.assert(opt_data.id == null || (opt_data.id instanceof goog.soy.data.SanitizedContent) || goog.isString(opt_data.id), "expected param 'id' of type null|string|undefined.");
  var id = /** @type {null|string|undefined} */ (opt_data.id);
  goog.asserts.assert(opt_data.show_modal == null || (opt_data.show_modal instanceof goog.soy.data.SanitizedContent) || goog.isString(opt_data.show_modal), "expected param 'show_modal' of type null|string|undefined.");
  var show_modal = /** @type {null|string|undefined} */ (opt_data.show_modal);
  goog.asserts.assert(opt_data.dismiss == null || goog.isBoolean(opt_data.dismiss), "expected param 'dismiss' of type boolean|null|undefined.");
  var dismiss = /** @type {boolean|null|undefined} */ (opt_data.dismiss);
  goog.asserts.assert(opt_data['class'] == null || (opt_data['class'] instanceof goog.soy.data.SanitizedContent) || goog.isString(opt_data['class']), "expected param 'class' of type null|string|undefined.");
  var param$class = /** @type {null|string|undefined} */ (opt_data['class']);
  return soydata.VERY_UNSAFE.ordainSanitizedHtml('<button type="button" class="btn btn-' + ((style != null) ? soy.$$escapeHtmlAttribute(style) : 'default') + ' btn-lg ' + ((param$class != null) ? soy.$$escapeHtmlAttribute(param$class) : '') + ' "' + ((show_modal != null) ? 'data-toggle="modal" data-target="#qs-modal-' + soy.$$escapeHtmlAttribute(show_modal) + '"' : '') + ((dismiss) ? 'data-dismiss="modal"' : '') + ((id != null) ? 'id="' + soy.$$escapeHtmlAttribute(id) + '"' : '') + '>' + soy.$$escapeHtml(text) + '</button>');
};
if (goog.DEBUG) {
  qs.core.button.soyTemplateName = 'qs.core.button';
}


qs.core.new_event_dialog = function(opt_data, opt_ignored) {
  goog.asserts.assert(goog.isString(opt_data.id) || (opt_data.id instanceof goog.soy.data.SanitizedContent), "expected param 'id' of type string|goog.soy.data.SanitizedContent.");
  var id = /** @type {string|goog.soy.data.SanitizedContent} */ (opt_data.id);
  return soydata.VERY_UNSAFE.ordainSanitizedHtml(qs.core.modal({title: 'Add new event', id: id, close_button: true, content: soydata.VERY_UNSAFE.$$ordainSanitizedHtmlForInternalBlocks('<table><tr><td>Event name (short):<td><input type="text" id="' + soy.$$escapeHtmlAttribute(id) + '-event-name" /><tr><td>Track duration?<td><div class="btn-group qs-event-options" id="' + soy.$$escapeHtmlAttribute(id) + '-event-track-duration" data-toggle="buttons"><label class="btn btn-primary"><input type="radio" name="yes" autocomplete="off">Yes</label><label class="btn btn-primary"><input type="radio" name="yes" autocomplete="off">No</label></div><tr><td>Polling frequency:<td><select id="' + soy.$$escapeHtmlAttribute(id) + '-frequency"><option value="3600">Every hour</option><option value="7200">Every two hours</option><option value="14400">Every four hours</option><option value="28800">Every eight hours</option><option value="86400">Every day</option><option value="172800">Every other day</option><option value="604800">Every week</option><option value="1209600">Every other week</option><option value="2592000">Every month</option></select></table>'), footer_content: soydata.VERY_UNSAFE.$$ordainSanitizedHtmlForInternalBlocks('' + qs.core.button({id: id + '-submit', class: 'qs-submit-new-question', style: 'success', text: 'Submit'}))}));
};
if (goog.DEBUG) {
  qs.core.new_event_dialog.soyTemplateName = 'qs.core.new_event_dialog';
}


qs.core.new_question_dialog = function(opt_data, opt_ignored) {
  goog.asserts.assert(goog.isString(opt_data.id) || (opt_data.id instanceof goog.soy.data.SanitizedContent), "expected param 'id' of type string|goog.soy.data.SanitizedContent.");
  var id = /** @type {string|goog.soy.data.SanitizedContent} */ (opt_data.id);
  return soydata.VERY_UNSAFE.ordainSanitizedHtml(qs.core.modal({title: 'Add new question', id: id, close_button: true, content: soydata.VERY_UNSAFE.$$ordainSanitizedHtmlForInternalBlocks('<table><tr><td>Question text:<td><input type="text" id="' + soy.$$escapeHtmlAttribute(id) + '-question-text" /><tr><td>Low-extreme label:<td><input type="text" id="' + soy.$$escapeHtmlAttribute(id) + '-low-label" /><tr><td>High-extreme label:<td><input type="text" id="' + soy.$$escapeHtmlAttribute(id) + '-high-label" /><tr><td>Middle label (optional):<td><input type="text" id="' + soy.$$escapeHtmlAttribute(id) + '-middle-label" /><tr><td>Question frequency:<td><select id="' + soy.$$escapeHtmlAttribute(id) + '-frequency"><option value="1h">Every hour</option><option value="2h">Every two hours</option><option value="4h">Every four hours</option><option value="8h">Every eight hours</option><option value="1d">Every day</option><option value="2d">Every other day</option><option value="7d">Every week</option><option value="14d">Every other week</option><option value="30d">Every month</option></select></table>'), footer_content: soydata.VERY_UNSAFE.$$ordainSanitizedHtmlForInternalBlocks('' + qs.core.button({id: id + '-submit', class: 'qs-submit-new-question', style: 'success', text: 'Submit'}))}));
};
if (goog.DEBUG) {
  qs.core.new_question_dialog.soyTemplateName = 'qs.core.new_question_dialog';
}


qs.core.login_dialog = function(opt_data, opt_ignored) {
  goog.asserts.assert(goog.isString(opt_data.id) || (opt_data.id instanceof goog.soy.data.SanitizedContent), "expected param 'id' of type string|goog.soy.data.SanitizedContent.");
  var id = /** @type {string|goog.soy.data.SanitizedContent} */ (opt_data.id);
  return soydata.VERY_UNSAFE.ordainSanitizedHtml(qs.core.modal({title: 'Login', id: id, content: soydata.VERY_UNSAFE.$$ordainSanitizedHtmlForInternalBlocks('<table><tr><td>Username:<td><input type="text" id="' + soy.$$escapeHtmlAttribute(id) + '-username" /><tr><td>Password:<td><input type="password" id="' + soy.$$escapeHtmlAttribute(id) + '-password" /></table>' + qs.core.button({id: id + '-submit', class: 'qs-login-button', text: 'Login'}))}));
};
if (goog.DEBUG) {
  qs.core.login_dialog.soyTemplateName = 'qs.core.login_dialog';
}


qs.core.modal = function(opt_data, opt_ignored) {
  goog.asserts.assert(goog.isString(opt_data.title) || (opt_data.title instanceof goog.soy.data.SanitizedContent), "expected param 'title' of type string|goog.soy.data.SanitizedContent.");
  var title = /** @type {string|goog.soy.data.SanitizedContent} */ (opt_data.title);
  goog.asserts.assert((opt_data.content instanceof soydata.SanitizedHtml) || (opt_data.content instanceof soydata.UnsanitizedText) || goog.isString(opt_data.content), "expected param 'content' of type soydata.SanitizedHtml.");
  var content = /** @type {soydata.SanitizedHtml} */ (opt_data.content);
  goog.asserts.assert(goog.isString(opt_data.id) || (opt_data.id instanceof goog.soy.data.SanitizedContent), "expected param 'id' of type string|goog.soy.data.SanitizedContent.");
  var id = /** @type {string|goog.soy.data.SanitizedContent} */ (opt_data.id);
  goog.asserts.assert(opt_data.footer_content == null || (opt_data.footer_content instanceof soydata.SanitizedHtml) || (opt_data.footer_content instanceof soydata.UnsanitizedText) || goog.isString(opt_data.footer_content), "expected param 'footer_content' of type soydata.SanitizedHtml|string|undefined.");
  var footer_content = /** @type {soydata.SanitizedHtml|string|undefined} */ (opt_data.footer_content);
  goog.asserts.assert(opt_data.close_button == null || goog.isBoolean(opt_data.close_button), "expected param 'close_button' of type boolean|null|undefined.");
  var close_button = /** @type {boolean|null|undefined} */ (opt_data.close_button);
  return soydata.VERY_UNSAFE.ordainSanitizedHtml('<div class="modal" tabindex="-1" id="qs-modal-' + soy.$$escapeHtmlAttribute(id) + '" role="dialog" aria-hidden="true" ><div class="modal-dialog" role="document"><div class="modal-content"><div class="modal-header"><button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&#215;</span></button><h5 class="modal-title">' + soy.$$escapeHtml(title) + '</h5></div><div class="modal-body">' + soy.$$escapeHtml(content) + '</div><div class="modal-footer"' + ((! (close_button || footer_content != null)) ? 'hidden="true"' : '') + '>' + ((footer_content != null) ? soy.$$escapeHtml(footer_content) : '') + ((close_button) ? qs.core.button({text: 'Close', dismiss: true}) : '') + '</div></div></div></div>');
};
if (goog.DEBUG) {
  qs.core.modal.soyTemplateName = 'qs.core.modal';
}


qs.core.session_timer_label = function(opt_data, opt_ignored) {
  goog.asserts.assert(goog.isString(opt_data.key) || (opt_data.key instanceof goog.soy.data.SanitizedContent), "expected param 'key' of type string|goog.soy.data.SanitizedContent.");
  var key = /** @type {string|goog.soy.data.SanitizedContent} */ (opt_data.key);
  goog.asserts.assert(goog.isString(opt_data.value) || (opt_data.value instanceof goog.soy.data.SanitizedContent), "expected param 'value' of type string|goog.soy.data.SanitizedContent.");
  var value = /** @type {string|goog.soy.data.SanitizedContent} */ (opt_data.value);
  return soydata.VERY_UNSAFE.ordainSanitizedHtml('<span class="qs-session-timer-label"><strong>' + soy.$$escapeHtml(key) + ': </strong> ' + soy.$$escapeHtml(value) + '</span>');
};
if (goog.DEBUG) {
  qs.core.session_timer_label.soyTemplateName = 'qs.core.session_timer_label';
}


qs.core.session_timers = function(opt_data, opt_ignored) {
  return soydata.VERY_UNSAFE.ordainSanitizedHtml('<div class="progress"><div class="progress-bar" role="progressbar" id="qs-id-session-timeout-progress-bar" ></div></div><div id="qs-id-session-estimated-time-left"></div><div id="qs-id-session-time-spent"></div><div id="qs-id-last-item-processing-time"></div>');
};
if (goog.DEBUG) {
  qs.core.session_timers.soyTemplateName = 'qs.core.session_timers';
}


qs.core.queue_progress_bar_label = function(opt_data, opt_ignored) {
  opt_data = opt_data || {};
  goog.asserts.assert(opt_data.done == null || (opt_data.done instanceof goog.soy.data.SanitizedContent) || goog.isString(opt_data.done), "expected param 'done' of type null|string|undefined.");
  var done = /** @type {null|string|undefined} */ (opt_data.done);
  goog.asserts.assert(opt_data.total == null || (opt_data.total instanceof goog.soy.data.SanitizedContent) || goog.isString(opt_data.total), "expected param 'total' of type null|string|undefined.");
  var total = /** @type {null|string|undefined} */ (opt_data.total);
  goog.asserts.assert(opt_data.next_in == null || (opt_data.next_in instanceof goog.soy.data.SanitizedContent) || goog.isString(opt_data.next_in), "expected param 'next_in' of type null|string|undefined.");
  var next_in = /** @type {null|string|undefined} */ (opt_data.next_in);
  return soydata.VERY_UNSAFE.ordainSanitizedHtml((next_in != null) ? 'No items, next in: ' + soy.$$escapeHtml(next_in) : (done != null && total != null) ? soy.$$escapeHtml(done) + ' out of ' + soy.$$escapeHtml(total) : 'N/A');
};
if (goog.DEBUG) {
  qs.core.queue_progress_bar_label.soyTemplateName = 'qs.core.queue_progress_bar_label';
}


qs.core.queue_progress_bar = function(opt_data, opt_ignored) {
  return soydata.VERY_UNSAFE.ordainSanitizedHtml('<div class="progress qs-queue-progress-bar"><div class="progress-bar qs-queue-progress-bar" role="progressbar" id="qs-id-queue-progress-bar" ></div><span id="qs-id-queue-progress-label"></span></div>');
};
if (goog.DEBUG) {
  qs.core.queue_progress_bar.soyTemplateName = 'qs.core.queue_progress_bar';
}


qs.core.username_label = function(opt_data, opt_ignored) {
  goog.asserts.assert(goog.isString(opt_data.username) || (opt_data.username instanceof goog.soy.data.SanitizedContent), "expected param 'username' of type string|goog.soy.data.SanitizedContent.");
  var username = /** @type {string|goog.soy.data.SanitizedContent} */ (opt_data.username);
  return soydata.VERY_UNSAFE.ordainSanitizedHtml('<div class="qs-username-label">' + ((username) ? soy.$$escapeHtml(username) : '(not logged in)') + '</div>');
};
if (goog.DEBUG) {
  qs.core.username_label.soyTemplateName = 'qs.core.username_label';
}


qs.core.header = function(opt_data, opt_ignored) {
  return soydata.VERY_UNSAFE.ordainSanitizedHtml('<nav class="navbar navbar-default navbar-fixed-top"><div class="container"><div class="qs-vertical-header-group qs-vertical-header-group-wide">' + qs.core.session_timers(null) + '</div><div class="qs-vertical-header-group qs-vertical-header-group-wide">' + qs.core.queue_progress_bar(null) + '</div><div class="qs-vertical-header-group"><div id="qs-header-username-label"></div><div class="btn-group"><button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false" >Options<span class="caret"></span></button><ul class="dropdown-menu"><li><a data-toggle="modal" data-target="#qs-modal-login-dialog">Login</a></li><li><a id="qs-id-force-refetch">Force re-fetch</a></li><li><a data-toggle="modal" data-target="#qs-modal-new-question-dialog">New question</a></li><li><a data-toggle="modal" data-target="#qs-modal-new-event-dialog">New event</a></li><li><a data-toggle="modal" id="qs-id-logout">Log out</a></li><li><a id="qs-id-experiment">Experiment!</a></li></ul></div></div></div></nav>');
};
if (goog.DEBUG) {
  qs.core.header.soyTemplateName = 'qs.core.header';
}


qs.core.message = function(opt_data, opt_ignored) {
  goog.asserts.assert(goog.isString(opt_data.text) || (opt_data.text instanceof goog.soy.data.SanitizedContent), "expected param 'text' of type string|goog.soy.data.SanitizedContent.");
  var text = /** @type {string|goog.soy.data.SanitizedContent} */ (opt_data.text);
  goog.asserts.assert(opt_data.header == null || (opt_data.header instanceof goog.soy.data.SanitizedContent) || goog.isString(opt_data.header), "expected param 'header' of type null|string|undefined.");
  var header = /** @type {null|string|undefined} */ (opt_data.header);
  goog.asserts.assert(opt_data.style == null || (opt_data.style instanceof goog.soy.data.SanitizedContent) || goog.isString(opt_data.style), "expected param 'style' of type null|string|undefined.");
  var style = /** @type {null|string|undefined} */ (opt_data.style);
  return soydata.VERY_UNSAFE.ordainSanitizedHtml('<div class="alert alert-' + ((style != null) ? soy.$$escapeHtmlAttribute(style) : 'info') + ' alert-dismissible" role="alert">' + ((header != null) ? '<strong>' + soy.$$escapeHtml(header) + '</strong> ' : '') + soy.$$escapeHtml(text) + '<button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button></div>');
};
if (goog.DEBUG) {
  qs.core.message.soyTemplateName = 'qs.core.message';
}


qs.core.app = function(opt_data, opt_ignored) {
  return soydata.VERY_UNSAFE.ordainSanitizedHtml(qs.core.login_dialog({id: 'login-dialog'}) + qs.core.new_question_dialog({id: 'new-question-dialog'}) + qs.core.new_event_dialog({id: 'new-event-dialog'}) + '<div id="qs-container">' + qs.core.header(null) + '<div id="qs-main"><div id="qs-messages"></div><div id="qs-main-widget"></div></div><div id="qs-footer"><div class="btn-group group-dropdown">' + qs.core.button({style: 'success', id: 'qs-id-submit-item-button', class: 'qs-footer-button', text: 'Submit'}) + qs.core.button({style: 'info', id: 'qs-id-edit-item-button', class: 'qs-footer-button', text: 'Edit'}) + qs.core.button({style: 'danger', id: 'qs-id-skip-item-button', class: 'qs-footer-button', text: 'Skip'}) + '</div></div></div>');
};
if (goog.DEBUG) {
  qs.core.app.soyTemplateName = 'qs.core.app';
}
