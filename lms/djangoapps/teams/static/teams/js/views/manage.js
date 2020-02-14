(function(define) {
    'use strict';
    define([
        'backbone',
        'underscore',
        'gettext',
        'edx-ui-toolkit/js/utils/html-utils',
        'common/js/components/utils/view_utils',
        'teams/js/views/team_utils',
        'text!teams/templates/manage.underscore',
        'text!teams/templates/love-chart.underscore'
    ], function(Backbone, _, gettext, HtmlUtils, ViewUtils, TeamUtils, manageTemplate, teammateLoveTableTemplate) {
        var ManageView = Backbone.View.extend({

            srInfo: {
                id: 'heading-manage',
                text: gettext('Manage')
            },

            events: {
                'click #download-team-csv-input': ViewUtils.withDisabledElement('downloadCsv'),
                'change #upload-team-csv-input': ViewUtils.withDisabledElement('uploadCsv'),
                'click #teammate-love-count-all': 'handleCountLoveAllClick',
                'click #teammate-love-count-week': 'handleCountLoveWeekClick'
            },

            initialize: function(options) {
                console.log(options);
                this.teamEvents = options.teamEvents;
                this.csvUploadUrl = options.teamMembershipManagementUrl;
                this.csvDownloadUrl = options.teamMembershipManagementUrl;
                this.teammateLoveCourseCountUrl = options.teammateLoveCourseCountUrl;
            },

            render: function() {
                HtmlUtils.setHtml(
                    this.$el,
                    HtmlUtils.template(manageTemplate)({})
                );
                return this;
            },

            downloadCsv: function() {
                window.location.href = this.csvDownloadUrl;
            },

            uploadCsv: function(event) {
                var file = event.target.files[0];
                var self = this;
                var formData = new FormData();

                formData.append('csv', file);  // xss-lint: disable=javascript-jquery-append
                return $.ajax({
                    type: 'POST',
                    url: self.csvUploadUrl,
                    data: formData,
                    processData: false,  // tell jQuery not to process the data
                    contentType: false   // tell jQuery not to set contentType
                }).done(
                    self.handleCsvUploadSuccess
                ).fail(
                    self.handleCsvUploadFailure
                );
            },

            handleCountLoveClick: function(all) {
                var view = this;
                console.log("in the func");
                $.ajax({
                    type: 'GET',
                    url: this.teammateLoveCourseCountUrl,
                    data: {
                        all: all
                    }
                }).done(function(data) {
                    console.log("good");
                    HtmlUtils.setHtml(
                        view.$('#teammate-love-chart-container'),
                        HtmlUtils.template(teammateLoveTableTemplate)({
                            loves_count: data,
                            table_title: all ? 'All-Time' : 'Weekly'
                        })
                    );
                }).fail(function(data) {
                    console.log('error', data);
                });
            },

            handleCountLoveAllClick: function() {
                this.handleCountLoveClick(true);
            },

            handleCountLoveWeekClick: function() {
                this.handleCountLoveClick(false);
            },

            handleCsvUploadSuccess: function() {
                // This handler is currently unimplemented (TODO MST-44)
                this.teamEvents.trigger('teams:update', {});
            },

            handleCsvUploadFailure: function() {
                // This handler is currently unimplemented (TODO MST-44)
            }
        });
        return ManageView;
    });
}).call(this, define || RequireJS.define);
