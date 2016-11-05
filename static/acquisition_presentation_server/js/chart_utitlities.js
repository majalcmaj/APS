/**
 * Created by mc on 05/11/16.
 */
function prepare_chart_data(time, data) {
    return {labels: time, series:[data]}
}

function create_chart(element_locator, data_arr, time_arr) {
    var chart = Chartist.Line(element_locator,
            prepare_chart_data(time_arr, data_arr),
            {
                full_width: true,
                // high: 100,
                // low: 0,
                 axisX: {
                    labelInterpolationFnc: function skipLabels(value, index) {
                      return index % 4  === 0 ? value : null;
                    }
                }
            }
    );
    return chart;
}
    //Chart content updater
function update_chart(chart, append_data, append_time) {
    var current_data = chart.data.series[0];
    append_data.forEach(function (record) {
        current_data.shift();
        current_data.push(record);
    });
    var current_time = chart.data.labels;
    for(i = 0 ; i < append_time.length ; i ++) {
        label = append_time[i];
        current_time.shift();
        current_time.push(label);
    }
    chart.update(prepare_chart_data(current_time, current_data));
}