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

function create_chart(element_locator, data_arr, time_arr, title, unit) {
    var data_length = time_arr.length;
    var labels_to_skip = Math.floor(data_length / 3);
    var options = {
        full_width: true,
        axisX: {
            labelInterpolationFnc: function skipLabels(value, index) {
                return index % labels_to_skip === 0 ? format_timestamp(value) : null;
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
function update_chart(chart, append_data, append_time) {
    var current_data = chart.data.series[0];
    append_data.forEach(function (record) {
        current_data.shift();
        current_data.push(record);
    });
    var current_time = chart.data.labels;
    for (i = 0; i < append_time.length; i++) {
        label = append_time[i];
        current_time.shift();
        current_time.push(label);
    }
    chart.update(prepare_chart_data(current_time, current_data));
}