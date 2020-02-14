/**
 * View for an individual team.
 */
(function(define) {
    'use strict';
    define([
        'backbone',
        'underscore',
        'gettext',
        'edx-ui-toolkit/js/utils/html-utils',
        'teams/js/views/team_discussion',
        'common/js/components/utils/view_utils',
        'teams/js/views/team_utils',
        'text!teams/templates/team-profile.underscore',
        'text!teams/templates/team-member.underscore',
        'text!teams/templates/love-display.underscore'
    ],
        function(Backbone, _, gettext, HtmlUtils, TeamDiscussionView, ViewUtils, TeamUtils,
                  teamTemplate, teamMemberTemplate, loveDisplayTemplate) {
            var TeamProfileView = Backbone.View.extend({

                errorMessage: gettext('An error occurred. Try again.'),

                events: {
                    'click .leave-team-link': 'leaveTeam',
                    'click .send-love-btn': 'sendLove'
                },

                initialize: function(options) {
                    this.teamEvents = options.teamEvents;
                    this.context = options.context;
                    this.setFocusToHeaderFunc = options.setFocusToHeaderFunc;

                    this.countries = TeamUtils.selectorOptionsArrayToHashWithBlank(this.context.countries);
                    this.languages = TeamUtils.selectorOptionsArrayToHashWithBlank(this.context.languages);
                    this.topic = options.topic;

                    this.listenTo(this.model, 'change', this.render);
                },

                render: function() {
                    var memberships = this.model.get('membership'),
                        discussionTopicID = this.model.get('discussion_topic_id'),
                        isMember = TeamUtils.isUserMemberOfTeam(memberships, this.context.userInfo.username),
                        isAdminOrStaff = this.context.userInfo.privileged || this.context.userInfo.staff,
                        isInstructorManagedTopic = TeamUtils.isInstructorManagedTopic(this.topic.attributes.type);

                    var showLeaveLink = isMember && (isAdminOrStaff || !isInstructorManagedTopic);

                    HtmlUtils.setHtml(
                        this.$el,
                        HtmlUtils.template(teamTemplate)({
                            courseID: this.context.courseID,
                            discussionTopicID: discussionTopicID,
                            readOnly: !(this.context.userInfo.privileged || isMember),
                            country: this.countries[this.model.get('country')],
                            language: this.languages[this.model.get('language')],
                            membershipText: TeamUtils.teamCapacityText(memberships.length, this.context.maxTeamSize),
                            isMember: isMember,
                            showLeaveLink: showLeaveLink,
                            hasCapacity: memberships.length < this.context.maxTeamSize,
                            hasMembers: memberships.length >= 1
                        })
                    );
                    this.discussionView = new TeamDiscussionView({
                        el: this.$('.discussion-module'),
                        readOnly: !isMember
                    });
                    this.discussionView.render();

                    this.renderTeamMembers();

                    this.renderLove();

                    this.setFocusToHeaderFunc();
                    return this;
                },

                renderTeamMembers: function() {
                    var view = this;
                    _.each(this.model.get('membership'), function(membership) {
                        HtmlUtils.append(
                            view.$('.members-info'),
                            HtmlUtils.template(teamMemberTemplate)({
                                imageUrl: membership.user.profile_image.image_url_medium,
                                username: membership.user.username,
                                memberProfileUrl: '/u/' + membership.user.username
                            })
                        );
                    });
                },

                renderLove: function() {
                    var view = this;
                    $.ajax({
                        type: 'GET',
                        url: view.context.teammateLoveUrl.replace('team_id', view.model.get('id'))
                    }).done(function(data) {
                        HtmlUtils.append(
                            view.$('.teammate-love'),
                            HtmlUtils.template(loveDisplayTemplate)({
                                received_loves: data.results,
                                memberships: view.model.get('membership'),
                                messages: view.context.teammateLoveMessages,
                                username: view.context.userInfo.username
                            })
                        );
                    }).fail(function(data) {
                        TeamUtils.parseAndShowMessage(data, view.errorMessage);
                    });
                },

                selectText: function(event) {
                    event.preventDefault();
                    $(event.currentTarget).select();
                },

                sendLove: function(event) {
                    event.preventDefault();
                    var view = this;
                    var messageSelection = this.$('#love-message-select option:selected');
                    var teammateSelection = this.$('#love-teammate-select option:selected');
                    ViewUtils.confirmThenRunOperation(
                        gettext('Send Teammate Love?'),
                        gettext('Message: "') + messageSelection.text() + gettext('" Recipient: ') + teammateSelection.text(),
                        gettext('Confirm'),
                        function() {
                            $.ajax({
                                type: 'POST',
                                url: view.context.teammateLoveUrl.replace('team_id', view.model.get('id')),
                                data: {
                                    recipient: teammateSelection.val(),
                                    message_id: messageSelection.val()
                                }
                            }).done(function() {
                                TeamUtils.showMessage('Teammate Love Sent!', 'success');
                            }).fail(function(data) {
                                TeamUtils.showMessage(data.responseJSON[0]);
                            });
                        }
                    );
                },

                leaveTeam: function(event) {
                    event.preventDefault();
                    var view = this; // eslint-disable-line vars-on-top
                    ViewUtils.confirmThenRunOperation(
                        gettext('Leave this team?'),
                        gettext("If you leave, you can no longer post in this team's discussions." +
                            'Your place will be available to another learner.'),
                        gettext('Confirm'),
                        function() {
                            $.ajax({
                                type: 'DELETE',
                                url: view.context.teamMembershipDetailUrl.replace('team_id', view.model.get('id'))
                            }).done(function() {
                                view.model.fetch()
                                    .done(function() {
                                        view.teamEvents.trigger('teams:update', {
                                            action: 'leave',
                                            team: view.model
                                        });
                                    });
                            }).fail(function(data) {
                                TeamUtils.parseAndShowMessage(data, view.errorMessage);
                            });
                        }
                    );
                }
            });

            return TeamProfileView;
        });
}).call(this, define || RequireJS.define);
