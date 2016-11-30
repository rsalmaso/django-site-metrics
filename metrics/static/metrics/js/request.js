var monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

$(document).ready(function() {
    $("abbr.timeago").timeago();

    $(".btn-graph").on("click", function() {
      var days = $(this).data("days");
      if (days) {
        history.pushState(null, null, "?graph=" + days);
        loadTrafficGraph(days);
      }
      return false;
    });
});

function showTooltip(x, y, contents) {
    $("#tooltip").remove();
    
    $('<div id="tooltip">' + contents + '</div>').css( {
        position: 'absolute',
        display: 'none',
        top: y + 5,
        left: x + 5,
        border: '1px solid #ccc',
        padding: '5px',
        'background-color': '#7CA0C7',
        'color': '#fff',
        opacity: 0.80
    }).appendTo("body").fadeIn(200);
}

var previousPoint = null;
var date = new Date();

function trafficGraph(placeholder, data) {
    var plot = $.plot(placeholder, data, {xaxis:{mode:'time'}, points:{show:true}, lines:{show:true}, grid:{hoverable:true}});
    
    placeholder.bind("plothover", function (event, pos, item) {
        if (item) {
            if (previousPoint != item.datapoint) {
                previousPoint = item.datapoint;
                
                date.setTime(item.datapoint[0]).toString;
                showTooltip(item.pageX, item.pageY, item.series.label + ' on ' + monthNames[date.getMonth()] + ' ' + date.getDate() + ' is ' + item.datapoint[1]);
            }
        } else {
            $("#tooltip").remove();
            previousPoint = null;
        }
    });
}
