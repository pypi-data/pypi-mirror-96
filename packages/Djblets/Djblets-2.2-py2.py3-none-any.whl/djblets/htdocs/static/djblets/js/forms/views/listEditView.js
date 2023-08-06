'use strict';

(function () {

    var entryTemplate = _.template('<li class="djblets-c-list-edit-widget__entry"\n    data-list-index="<%- index %>">\n <input type="text"<%= inputAttrs %>>\n <a href="#" class="djblets-c-list-edit-widget__remove-item"\n    role="button" title="<%- removeText %>">\n   <span class="fa fa-times"></span>\n </a>\n</li>');

    /**
     * A view for editing a list of elements.
     *
     * This is the JavaScript view for
     * :py:class:`djblets.forms.widgets.ListEditWidget`.
     */
    Djblets.Forms.ListEditView = Backbone.View.extend({
        events: {
            'click .djblets-c-list-edit-widget__add-item': '_addItem',
            'click .djblets-c-list-edit-widget__remove-item': '_removeItem',
            'blur .djblets-c-list-edit-widget__input': '_onBlur'
        },

        /**
         * Initialize the view.
         *
         * Args:
         *     options (object):
         *         The view options.
         *
         * Option Args:
         *     inputAttrs (string):
         *         The attributes that should be added to each ``<input>`` element.
         *
         *     removeText (string):
         *         The localized text for removing an item.
         *
         *     sep (string):
         *         The list separator. It will be used to join the list of values
         *         into a string.
         */
        initialize: function initialize(options) {
            this._inputAttrs = options.inputAttrs;
            this._removeText = options.removeText;
            this._sep = options.sep;
            this._values = [];
        },


        /**
         * Render the view.
         *
         * Since most of the view is rendered by Django, this just sets up some
         * event listeners.
         *
         * Returns:
         *     Djblets.Forms.ListEditView:
         *     This view.
         */
        render: function render() {
            var _this = this;

            this.$el.data('djblets-list-edit-view', this);

            this._$list = this.$el.children('.djblets-c-list-edit-widget__entries');
            this._$list.find('.djblets-c-list-edit-widget__input').each(function (idx, el) {
                return _this._values.push($(el).val());
            });
            this._$addBtn = this.$el.children('.djblets-c-list-edit-widget__add-item');
            this._$hidden = this.$el.children('.djblets-c-list-edit-widget__value');

            return this;
        },


        /**
         * Add an item to the list.
         *
         * Args:
         *     e (Event):
         *         The click event that triggered this event handler.
         */
        _addItem: function _addItem(e) {
            var _this2 = this;

            e.preventDefault();
            e.stopPropagation();

            var $entry = $(entryTemplate({
                index: this._values.length,
                inputAttrs: this._inputAttrs,
                removeText: this._removeText
            })).insertBefore(this._$addBtn);

            $entry.find('.djblets-c-list-edit-widget__add-item').on('click', function (e) {
                return _this2._addItem(e);
            }).end().find('.djblets-c-list-edit-widget__input').on('change', function (e) {
                return _this2._onBlur(e);
            }).end();

            this._values.push('');
        },


        /**
         * Remove an item.
         *
         * When there is only a single item in the list, we clear it instead of
         * removing it so there is always at least one ``<input>`` element and
         * value in the list.
         *
         * Args:
         *     e (Event):
         *         The click event that triggered this event handler.
         */
        _removeItem: function _removeItem(e) {
            e.preventDefault();
            e.stopPropagation();

            var $target = $(e.target);
            var $entry = $target.closest('.djblets-c-list-edit-widget__entry');
            var index = $entry.attr('data-list-index');

            if (this._values.length > 1) {
                $entry.remove();
                this._values.splice(index, 1);
                this._$list.find('.djblets-c-list-edit-widget__entry').each(function (idx, el) {
                    return $(el).attr('data-list-index', idx);
                });
            } else {
                this._values[index] = '';
                $target.siblings('.djblets-c-list-edit-widget__input').val('');
            }

            this._$hidden.val(this._values.filter(function (v) {
                return v.length > 0;
            }).join(this._sep));
        },


        /**
         * Update the internal values when a field changes.
         *
         * Args:
         *     e (Event):
         *         The blur event.
         */
        _onBlur: function _onBlur(e) {
            var $target = $(e.target);
            var index = $target.closest('.djblets-c-list-edit-widget__entry').attr('data-list-index');

            this._values[index] = $target.val();
            this._$hidden.val(this._values.filter(function (v) {
                return v.length > 0;
            }).join(this._sep));
        }
    });
})();

//# sourceMappingURL=listEditView.js.map