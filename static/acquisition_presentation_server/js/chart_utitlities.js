/**
 * Created by mc on 05/11/16.
 */

var labels_to_skip;
function format_timestamp(unix_timestamp) {
    var date = new Date(unix_timestamp * 1000);
    return date.toISOString().substr(5, 14).replace("T", "\n");
}
function prepare_chart_data(time, data) {
    return {labels: time, series: [data]}
}

function create_chart(element_locator, data_arr, time, title, unit) {
    var time_arr = [];
    for(var i = time[0]; i < time[1]; i += time[2])
        time_arr.push(i);
    var data_length = time_arr.length;
    var labels_to_skip = Math.floor(data_length / 3);
    var options = {
        fullWidth: true,
        axisX: {
            labelInterpolationFnc: function skipLabels(value, index) {
                return ((index % labels_to_skip === 0 && index <= data_length - labels_to_skip) ||
                index === data_length-1) ? format_timestamp(value) : null;
            }
        },
        showPoint: false,
        lineSmooth: Chartist.Interpolation.none({
            fillHoles: false
        }),
        showArea: true,
        plugins: [
            Chartist.plugins.ctAxisTitle({
                axisX: {

                },
                axisY: {
                    axisTitle: title + "[" + unit + "]",
                    axisClass: 'ct-axis-title',
                    offset: {
                        x: 0,
                        y: 20
                    },
                    textAnchor: 'middle',
                    flipTitle: true
                }
            })
        ]
    };
    if (unit == '%') {
        options['high'] = 100;
        options['low'] = 0;
    }
    return Chartist.Line(element_locator,
        prepare_chart_data(time_arr, data_arr),
        options
    );

}
//Chart content updater
function update_chart(chart, append_data, time) {
    var current_data = chart.data.series[0];
    // current_data = current_data.concat(append_data);
    // current_data = current_data.slice(append_data.length);
    var current_time = chart.data.labels;
    var current_index = current_time.length - 1;
    while(current_time[current_index] > time[0]) {
        current_data.pop();
        current_time.pop();
    }
    for(i= time[0], counter=0; i < time[1] ; i += time[2], counter += 1) {
        current_time.shift();
        current_data.shift();
        current_time.push(i);
        current_data.push(append_data[counter]);
    }
    chart.update(prepare_chart_data(current_time, current_data));
}