// Format datetimes in multiple ways, depending on which CSS class is set on it.
var momentjsClasses = function () {
    var $fromNow = $('.from-now');
    var $shortDate = $('.short-date');
    var $longDate = $('.long-date');

    $fromNow.each(function (i, e) {
        (function updateTime() {
            var time = moment($(e).data('datetime'));
            $(e).text(time.fromNow());
            $(e).attr('title', time.format('MMMM Do YYYY, h:mm:ss a Z'));
            setTimeout(updateTime, 1000);
        })();
    });

    $shortDate.each(function (i, e) {
        var time = moment($(e).data('datetime'));
        $(e).text(time.format('MMM Do YYYY'));
        $(e).attr('title', time.format('MMMM Do YYYY, h:mm:ss a Z'));
    });

    $longDate.each(function (i, e) {
        var time = moment($(e).data('datetime'));
        $(e).text(time.format('MMM Do YYYY, h:mm:ss'));
        $(e).attr('title', time.format('MMMM Do YYYY, h:mm:ss a Z'));
    });
};

// Initialize everything when the browser is ready.
$(document).ready(function() {
    momentjsClasses();
});