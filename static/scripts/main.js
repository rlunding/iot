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

var stabilize = function () {
    setInterval(function () {
        $.post('/stabilize', function (data, status) {

        });
    }, Math.floor((Math.random() * 5000) + 2000));
};

var succlist = function () {
    setInterval(function () {
        $.post('/succlist', function (data, status) {

        });
    }, Math.floor((Math.random() * 10000) + 5000));
};

// Initialize everything when the browser is ready.
$(document).ready(function() {
    momentjsClasses();
    stabilize();
    succlist();
});