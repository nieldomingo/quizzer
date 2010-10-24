/**
 * Copyright (c) 2010, Nathan Bubna
 * Dual licensed under the MIT and GPL licenses:
 *   http://www.opensource.org/licenses/mit-license.php
 *   http://www.gnu.org/licenses/gpl.html
 *
 * This plugin exists to make it trivial to place a "message" (any image,
 * text or arbitrary element) at any corner, edge or center of either
 * the whole page or any other element.  The default placement is
 * 'top-center' for page-level messages or 'top-left' for messages
 * placed relative to a specific element.
 *
 * To place a message at page-level, call:
 * 
 *   $.place('Hello World!');
 *
 * or call:
 *
 *   $('#foo').place({img:'workingIcon.gif', text:'Working...'})
 *
 * to do the same, but locate the message within a specific element(s).
 *
 * You can change any of the default options by altering the $.place
 * properties (or sub-properties), like this:
 *
 *  $.place.img = 'spinner.png';
 *  $.place.align = 'bottom-center';
 *  $.place.classname = 'myPlaceClass';
 *  $.place.css.border = '1px solid #000';
 *
 * All options can also be overridden per-call by passing in
 * an options object with the overriding properties, like so:
 *
 *  $.place({ element:'#cancelButton', css:{border:'1px dotted'} });
 *  $('#foo').place({ img:'place.gif', align:'center'});
 *
 * Also, this plugin supports the metadata plugin as a
 * way to specify options directly in your markuo.
 *
 * When a message is about to be placed, 
 *
 * Be sure to check out the provided demo for an easy overview of the most
 * commonly used options!! Of course, everything in this plugin is easy to
 * configure and/or override with those same techniques.
 *
 * Contributions, bug reports and general feedback on this is welcome.
 *
 * @version 1.0
 * @requires $.measure
 * @supports $.pulse
 * @name place
 * @author Nathan Bubna
 */
;(function($) {
    // enforce requirement(s)
    if (!$.measure) throw '$.place plugin requires $.measure plugin to be present';

    // the main interface...
    $.place = function(show, el, opts) {
        $('body').place(show, el, opts);
        return P;
    };
    var P = $.fn.place = function(show, el, opts) {
        opts = P.toOpts(show, el, opts);
        P.plugin.call(this, $.place, opts, function(o) {
            if (o.show === false) {
                o = this.data('place');//find old opts
                if (o) P.unplace.call(this, o);
            } else {
                this.data('place', o);
                P.init.call(this, o);
            }
        });
        return this;
    };

    // all that's configurable...
    $.extend(true, $.place, $.measure, {//include $.measure properties
        version: "1.0",
        // common
        align: 'top-left',
        img: null,
        element: null,
        text: null,
        effect: null,
        // occasional
        classname: 'place',
        imgClass: 'place-img',
        elementClass: 'place-element',
        textClass: 'place-text',
        css: { position:'absolute', whiteSpace:'nowrap', zIndex:1001 },
        cloneEvents: true,
        elementCss: { position:'relative', left:0, top:0 },
        // rare
        initEvent: 'place',
        html: '<div></div>',
        imgHtml: '<img class="place-img-content"/>',
        textHtml: '<span class="place-text-content"></span>',
        resizeEvents: 'resize',
        pageOptions: { align:'top-center' }
    });

    // all that's extensible...
    $.extend(true, $.fn.place, $.fn.measure, {//include $.fn.measure functions
        // functions
        init: function(o) {
            P.initSelf.call(this, o);
            if (o.img) P.initImg.call(this, o);
            if (o.text) P.initText.call(this, o);
            if (o.element) P.initElement.call(this, o);
            $(window).bind(o.resizeEvents, o.resizer = function() { o.resize(o); });
            $(document).bind(o.initEvent, o.initer = function(e, o) {
                $(document).unbind(o.initEvent, o.initer);
                if (o.show === false) {//allow event to be cancelled
                    P.unplace.call(o.self, o);
                } else {
                    P.place.call(o.self, o);
                }
            });
            o.ready = function(){ o.self.trigger(o.initEvent, [o]); };
            if (!o.imgLoading) o.ready();
        },
        initSelf: function(o) {
            o.parent = this;
            o.self = $(o.html).hide().addClass(o.classname).css(o.css).appendTo(this);
            return o.self;
        },
        initImg: function(o) {
            // be sure to wait for img to load
            o.imgContent = $(o.imgHtml).one('load', o.imgLoading = function() {
                o.imgLoading = null;
                if (o.ready) o.ready();
            }).attr('src', o.img);
            o.self.addClass(o.imgClass).append(o.imgContent);
        },
        initText: function(o) {
            o.textContent = $(o.textHtml).text(o.text);
            o.self.addClass(o.textClass).append(o.textContent);
        },
        initElement: function(o) {
            o.elementContent = $(o.element).clone(o.cloneEvents).css(o.elementCss).show();
            o.self.addClass(o.elementClass).append(o.elementContent);
        },
        resize: function(o) {
            o.parent.box = null;
            P.place.call(o.self.hide(), o);
        },
        place: function(o, recalc) {
            var box = o.align, v = 'top', h = 'left';
            if (typeof box == "object") {
                box = $.extend(P.calc.call(this, v, h, o), box);
            } else {
                if (box != 'top-left') {
                    var s = box.split('-');
                    if (s.length == 1) {
                        v = h = s[0];
                    } else {
                        v = s[0]; h = s[1];
                    }
                }
                if (!this.hasClass(v)) this.addClass(v);
                if (!this.hasClass(h)) this.addClass(h);
                box = P.calc.call(this, v, h, o);
            }
            this.show().css(o.box = box);
            if (!recalc && o.effect) {
                this.bind($.pulse.updateEvent, o.replace = function(){
                    P.place.call(o.self, o, true);
                }).pulse(o.effect, o);
            }
        },
        unplace: function(o, method, arg) {
            this.data('place', null);
            if (o.effect) this.unbind($.pulse.updateEvent, o.replace);
            $(window).unbind(o.resizeEvents, o.resizer);
            $(document).unbind(o.initEvent, o.initer);
            if (o.effect) this.pulse(false);
            if (!method) method = o.remove;
            if (method) {
                o.self[method](arg, function() { o.self.remove() });
            } else {
                o.self.remove();
            }
        },
        calc: function(v, h, o) {
            var box = $.extend({}, P.measure.call(o.parent, o)),
                H = $.boxModel ? this.height() : this.innerHeight(),
                W = $.boxModel ? this.width() : this.innerWidth();
            if (v != 'top') {
                var d = box.height - H;
                if (v == 'center') {
                    d /= 2;
                } else if (v != 'bottom') {
                    d = 0;
                } else if ($.boxModel) {
                    d -= css(this, 'paddingTop') + css(this, 'paddingBottom');
                }
                box.top += d;
            }
            if (h != 'left') {
                var d = box.width - W;
                if (h == 'center') {
                    d /= 2;
                } else if (h != 'right') {
                    d = 0;
                } else if ($.boxModel) {
                    d -= css(this, 'paddingLeft') + css(this, 'paddingRight');
                }
                box.left += d;
            }
            box.height = H;
            box.width = W;
            return box;
        },
        toOpts: function(show, el, o) {
            if (typeof show != "boolean") { o = el; el = show; show = undefined; }
            if ($.isPlainObject(el)) {
                o = el; el = null;
            }
            if (!o) o = {};
            if (show !== undefined) o.show = show;
            if (el) {
                if (el.nodeType || el.jquery) {
                    o.element = el;
                } else if (typeof el == "string") {
                    var $el = $(el);
                    if ($el.length > 0) {
                        o.element = $el;
                    } else {
                        o.text = el;
                    }
                }
            }
            return o;
        }
    });
    css = P.getCss;//convenience alias

})(jQuery);
