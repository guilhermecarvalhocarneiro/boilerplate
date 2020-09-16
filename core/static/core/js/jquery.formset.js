/**
 * jQuery Formset 1.3-pre
 * @author Stanislaus Madueke (stan DOT madueke AT gmail DOT com)
 * @requires jQuery 1.2.6 or later
 *
 * Copyright (c) 2009, Stanislaus Madueke
 * All rights reserved.
 *
 * Licensed under the New BSD License
 * See: http://www.opensource.org/licenses/bsd-license.php
 *
 *Atualizado por Lucas S da Silva
 * Atualizado para funcionar com multiplos tipos de inlines e corrigido alguns detalhes para funcionar com esse projeto
 *
 *
 */

(function($) {
    $.fn.formset = function(opts)
    {
        var options = $.extend({}, $.fn.formset.defaults, opts),
            flatExtraClasses = options.extraClasses.join(' '),
            totalForms = $('#id_' + options.prefix + '-TOTAL_FORMS'),
            maxForms = $('#id_' + options.prefix + '-MAX_NUM_FORMS'),
            minForms = $('#id_' + options.prefix + '-MIN_NUM_FORMS'),
            childElementSelector = 'input,select,textarea,label,div',
            $$ = $(this),

            applyExtraClasses = function(row, ndx) {
                if (options.extraClasses) {
                    row.removeClass(flatExtraClasses);
                    row.addClass(options.extraClasses[ndx % options.extraClasses.length]);
                }
            },

            updateElementIndex = function(elem, prefix, ndx) {
                var idRegex = new RegExp(prefix + '-(\\d+|__prefix__)-'),
                    replacement = prefix + '-' + ndx + '-';
                if (elem.attr("for")) elem.attr("for", elem.attr("for").replace(idRegex, replacement));
                if (elem.attr('id')) elem.attr('id', elem.attr('id').replace(idRegex, replacement));
                if (elem.attr('name')) elem.attr('name', elem.attr('name').replace(idRegex, replacement));
            },

            hasChildElements = function(row) {
                return row.find(childElementSelector).length > 0;
            },

            showAddButton = function() {
                len_delete_checked = $('.' + options.formCssClass + ':hidden').not('.formset-custom-template').filter('.' + options.prefix).length;
                return maxForms.length == 0 ||   // For Django versions pre 1.2
                    (maxForms.val() == '' || maxForms.val() - (totalForms.val() - len_delete_checked) > 0);
            },

            /**
            * Indicates whether delete link(s) can be displayed - when total forms > min forms
            */
            showDeleteLinks = function() {
                 len_delete_checked = $('.' + options.formCssClass + ':hidden').not('.formset-custom-template').filter('.' + options.prefix).length;
                return minForms.length == 0 ||   // For Django versions pre 1.7
                    (minForms.val() == '' || ((totalForms.val() - len_delete_checked) - minForms.val() > 0));
            },

            insertDeleteLink = function(row) {
                var delCssSelector = options.deleteCssClass.trim().replace(/\s+/g, '.');
                var addCssSelector = options.addCssClass.trim().replace(/\s+/g, '.');
                if (row.is('TR')) {
                    // If the forms are laid out in table rows, insert
                    // the remove button into the last table cell:
                    row.children(':last').append('<a class="' + options.deleteCssClass + '" href="javascript:void(0)">' + options.deleteText + '</a>');
                } else if (row.is('UL') || row.is('OL')) {
                    // If they're laid out as an ordered/unordered list,
                    // insert an <li> after the last list item:
                    row.append('<li><a class="' + options.deleteCssClass + '" href="javascript:void(0)">' + options.deleteText + '</a></li>');
                } else {
                    // Otherwise, just insert the remove button as the
                    // last child element of the form's container:
                    row.append(' <div class="col-12 p-0 text-right"><a class="' + options.deleteCssClass + '" href="javascript:void(0)">' + options.deleteText + '</a></div>');
                }
                // Check if we're under the minimum number of forms - not to display delete link at rendering
                if (!showDeleteLinks()) {
                    row.find('a.' + delCssSelector).hide();
                }

                row.find('a.' + delCssSelector).click(function () {
                    var row = $(this).parents('.' + options.formCssClass);
                    var siblingsRow = row.siblings('.' + options.formCssClass).not(options.formTemplate);
                    var del = row.find('input:hidden[id $= "-DELETE"]');
                    //alterado pois o botão agora está dentro de uma div
                    var buttonRow = $("." + addCssSelector + ', .' + options.formCssClass + '-add', row.siblings());
                    var forms;
                    if (del.length) {
                        // We're dealing with an inline formset.
                        // Rather than remove this form from the DOM, we'll mark it as deleted
                        // and hide it, then let Django handle the deleting:
                        del.val('on');
                        row.hide();
                        forms = $('.' + options.formCssClass).not(':hidden').filter('.' + options.prefix);
                    } else {
                        row.remove();
                    }
                    //retirei as 2 linhas de codigos abaixo do else, para funcionar corretamente a contagem incluindo os inlines ja existentes, porem ocutos
                    // Update the TOTAL_FORMS count:
                    // coloquei para contar apenas os inlines visiveis, para funcionar de forma correta o minForms
                    forms = $('.' + options.formCssClass).not('.formset-custom-template').filter('.' + options.prefix);
                    totalForms.val(forms.length);
                    for (var i = 0, formCount = forms.length; i < formCount; i++) {
                        // Apply `extraClasses` to form rows so they're nicely alternating:
                        applyExtraClasses(forms.eq(i), i);
                        if (!del.length) {
                            // Also update names and IDs for all child controls (if this isn't
                            // a delete-able inline formset) so they remain in sequence:
                            forms.eq(i).find(childElementSelector).each(function () {
                                updateElementIndex($(this), options.prefix, i);
                            });
                        }
                    }
                    // Check if we've reached the minimum number of forms - hide all delete link(s)
                    if (!showDeleteLinks()) {
                        $('a.' + delCssSelector, siblingsRow).each(function () {
                            $(this).hide();
                        });
                    }
                    // Check if we need to show the add button:
                    if (buttonRow.is(':hidden') && showAddButton()) buttonRow.show();
                    // If a post-delete callback was provided, call it with the deleted form:
                    if (options.removed) options.removed(row);
                    return false;
                });
            };

        $$.each(function(i) {
            var row = $(this),
                del = row.find('input:checkbox[id $= "-DELETE"]');
            if (del.length) {
                // If you specify "can_delete = True" when creating an inline formset,
                // Django adds a checkbox to each form in the formset.
                // Replace the default checkbox with a hidden field:
                if (del.is(':checked')) {
                    // If an inline formset containing deleted forms fails validation, make sure
                    // we keep the forms hidden (thanks for the bug report and suggested fix Mike)
                    del.before('<input type="hidden" name="' + del.attr('name') +'" id="' + del.attr('id') +'" value="on" />');
                    row.hide();
                } else {
                    del.before('<input type="hidden" name="' + del.attr('name') +'" id="' + del.attr('id') +'" />');
                }
                // Hide any labels associated with the DELETE checkbox:
                $('label[for="' + del.attr('id') + '"]').hide();
                del.remove();
            }
            if (hasChildElements(row)) {
                row.addClass(options.formCssClass);
                if (row.is(':visible')) {
                    // só add o botão de delete caso tenha permissão
                    if (row.find('input:hidden[id $= "-DELETE"]').length > 0)
                        insertDeleteLink(row);
                    applyExtraClasses(row, i);
                }
            }
        });

        if ($$.length) {
            var hideAddButton = !showAddButton(),
                addButton, template;
            if (options.formTemplate) {
                // If a form template was specified, we'll clone it to generate new form instances:
                template = (options.formTemplate instanceof $) ? options.formTemplate : $(options.formTemplate);
                template.removeAttr('id').addClass(options.formCssClass + ' formset-custom-template');
                template.find(childElementSelector).each(function() {
                    updateElementIndex($(this), options.prefix, '__prefix__');
                });
                //retirei e coloco no evento de add inlines (Fiz isso pois tirei o clone(true) e ai não funcionava mais por aqui)
                // insertDeleteLink(template);
            } else {
                // Otherwise, use the last form in the formset; this works much better if you've got
                // extra (>= 1) forms (thnaks to justhamade for pointing this out):

                // retirei o clone (true), porque dá problemas quando se quer mascaras em campos do inline
                template = $('.' + options.formCssClass + ':last').clone().removeAttr('id');
                template.find('input:hidden[id $= "-DELETE"]').remove();
                // Clear all cloned fields, except those the user wants to keep (thanks to brunogola for the suggestion):
                template.find(childElementSelector).not(options.keepFieldValues).each(function() {
                    var elem = $(this);
                    // If this is a checkbox or radiobutton, uncheck it.
                    // This fixes Issue 1, reported by Wilson.Andrew.J:
                    if (elem.is('input:checkbox') || elem.is('input:radio')) {
                        elem.attr('checked', false);
                    } else {
                        elem.val('');
                    }
                });
            }
            // FIXME: Perhaps using $.data would be a better idea?
            options.formTemplate = template;

            var addCssSelector = options.addCssClass.trim().replace(/\s+/g, '.');
            if ($$.is('TR')) {
                // If forms are laid out as table rows, insert the
                // "add" button in a new table row:
                var numCols = $$.eq(0).children().length,   // This is a bit of an assumption :|
                    buttonRow = $('<tr><td colspan="' + numCols + '"><a class="' + options.addCssClass + '" href="javascript:void(0)">' + options.addText + '</a></tr>')
                                .addClass(options.formCssClass + '-add');
                $$.parent().append(buttonRow);
                if (hideAddButton) buttonRow.hide();
                addButton = buttonRow.find('a');
            } else {
                // Otherwise, insert it immediately after the last form:
                // Atualizado com um container de div a mais
                $$.filter(':last').after('<div class="col-12"><a class="' + options.addCssClass + '" href="javascript:void(0)">' + options.addText + '</a></div>');
                var divButton = $$.filter(':last').next();
                // busca no container da div a tag a
                addButton = divButton.find('a')
                if (hideAddButton) addButton.hide();
            }
            addButton.click(function() {
                var formCount = parseInt(totalForms.val());
                var row = options.formTemplate.filter('.'+options.prefix).clone().removeClass('formset-custom-template');
                var buttonRow = $($(this).parents('tr.' + options.formCssClass + '-add').get(0) || this);
                var delCssSelector = options.deleteCssClass.trim().replace(/\s+/g, '.');
                applyExtraClasses(row, formCount);
                //alterado pois o botão agora está dentro de uma div
                row.insertBefore(buttonRow.parent()).show();
                row.find(childElementSelector).each(function() {
                    updateElementIndex($(this), options.prefix, formCount);
                });
                totalForms.val(formCount + 1);
                insertDeleteLink(row);
                // pega inlines irmaos
                irmaos = row.siblings('.'+options.formCssClass+':not(.formset-custom-template)');
                // verifica se tem a permisão de deletar.
                var del = irmaos.find('input:hidden[id $= "-DELETE"]');
                // Check if we're above the minimum allowed number of forms -> show all delete link(s)
                if (showDeleteLinks() && del.length > 0 ){
                    var siblingsRow =  row.siblings('.'+options.formCssClass).not(options.formTemplate);
                    $('a.' + delCssSelector, siblingsRow).each(function(){$(this).show();});
                }
                // Check if we've exceeded the maximum allowed number of forms:
                if (!showAddButton()) buttonRow.hide();
                // If a post-add callback was supplied, call it with the added form:
                if (options.added) options.added(row);
                return false;
            });
        }

        return $$;
    };

    /* Setup plugin defaults */
    $.fn.formset.defaults = {
        prefix: 'form',                             // The form prefix for your django formset
        formTemplate: '.formset-custom-template',   // The jQuery selection cloned to generate new form instances
        addText: 'add another',                     // Text for the add link
        deleteText: 'remove',                       // Text for the delete link
        addCssClass: 'add-row',                     // CSS class applied to the add link
        deleteCssClass: 'delete-row',               // CSS class applied to the delete link
        formCssClass: 'dynamic-form',               // CSS class applied to each form in a formset
        extraClasses: [],                           // Additional CSS classes, which will be applied to each form in turn
        keepFieldValues: '',                        // jQuery selector for fields whose values should be kept when the form is cloned
        added: null,                                // Function called each time a new form is added
        removed: null                               // Function called each time a form is deleted
    };
})(jQuery);
