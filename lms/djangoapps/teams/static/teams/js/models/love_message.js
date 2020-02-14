/**
 * Model for a love message choice.
 */
(function(define) {
    'use strict';
    define(['backbone'], function(Backbone) {
        var LoveMessage = Backbone.Model.extend({
            defaults: {
                text: ''
            },

            initialize: function(options) {
                this.url = options.url;
            }
        });
        return LoveMessage;
    });
}).call(this, define || RequireJS.define);
