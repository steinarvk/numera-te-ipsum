// This file was automatically generated from question.soy.
// Please don't edit this file by hand.

/**
 * @fileoverview Templates in namespace qs.question.
 */

if (typeof qs == 'undefined') { var qs = {}; }
if (typeof qs.question == 'undefined') { qs.question = {}; }


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
  return soydata.VERY_UNSAFE.ordainSanitizedHtml(((opt_data.queueSize != null) ? '<p class="qs_statusbar_section"><b>Queue</b>:' + ((opt_data.queueSize == 0) ? 'No items pending (next ' + soy.$$escapeHtml(opt_data.timeUntilNextText) + ').' : (opt_data.queueSize == 1) ? '1 item pending.' : soy.$$escapeHtml(opt_data.queueSize) + ' items pending.') + '</p>' : '') + ((opt_data.progressPct != null && opt_data.progressEtaText != null && opt_data.progressDurationText != null && opt_data.progressProcessed != null && opt_data.progressTotal != null) ? '<p class="qs_statusbar_section"><b>Session length:</b> ' + soy.$$escapeHtml(opt_data.progressDurationText) + '</p><p class="qs_statusbar_section"><b>Progress</b>: ' + soy.$$escapeHtml(opt_data.progressPct) + '% (' + soy.$$escapeHtml(opt_data.progressProcessed) + '/' + soy.$$escapeHtml(opt_data.progressTotal) + ')</p><p class="qs_statusbar_section"><b>ETA</b>: ' + soy.$$escapeHtml(opt_data.progressEtaText) + '</p>' : '') + ((opt_data.answerPct != null && opt_data.answerTimeMs != null) ? '<p class="qs_statusbar_section"><b>Last answer</b>:' + soy.$$escapeHtml(opt_data.answerPct) + '% (after ' + soy.$$escapeHtml(opt_data.answerTimeMs) + 'ms)</p>' : ''));
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

if (typeof qs == 'undefined') { var qs = {}; }
if (typeof qs.core == 'undefined') { qs.core = {}; }


qs.core.message = function(opt_data, opt_ignored) {
  return soydata.VERY_UNSAFE.ordainSanitizedHtml('<p><b>Message</b>: ' + soy.$$escapeHtml(opt_data.text) + '</p>');
};
if (goog.DEBUG) {
  qs.core.message.soyTemplateName = 'qs.core.message';
}


qs.core.link = function(opt_data, opt_ignored) {
  return soydata.VERY_UNSAFE.ordainSanitizedHtml('<a href="' + soy.$$escapeHtmlAttribute(soy.$$filterNormalizeUri(opt_data.target)) + '">' + soy.$$escapeHtml(opt_data.text) + '</a>');
};
if (goog.DEBUG) {
  qs.core.link.soyTemplateName = 'qs.core.link';
}
