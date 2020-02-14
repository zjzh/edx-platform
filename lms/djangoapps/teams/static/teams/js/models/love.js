/**
 * Model for a TeammateLove.
 */
(function(define) {
    'use strict';
    define(['backbone'], function(Backbone) {
        var Love = Backbone.Model.extend({
            defaults: {
                sender: '',
                recipent: '',
                team: '',
                message: '',
                created: '',
            },

            initialize: function(options) {
                this.url = options.url;
            }
        });
        return Love;
    });
}).call(this, define || RequireJS.define);
