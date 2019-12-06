"use strict";

let d = document;
let body = d.body;

let timelineContainer = d.getElementById("graphTimeline");

class globals {
    static sensor1_cache = new Object();
}

function formatDate(d) {

let monthAdjusted = (parseInt(d.getMonth(), 10) + 1).toString();
let displayDate =   d.getFullYear() + "-" +
            //("00" + d.getMonth()).slice(-2) + "-" +
            ("00" + monthAdjusted).slice(-2) + "-" +
            ("00" + d.getDate()).slice(-2) + " " +
            ("00" + d.getHours()).slice(-2) + ":" +
            ("00" + d.getMinutes()).slice(-2) + ":" +
            ("00" + d.getSeconds()).slice(-2) + "." +
            ("000" + d.getMilliseconds()).slice(-3);
//https://stackoverflow.com/questions/10073699/pad-a-number-with-leading-zeros-in-javascript
return displayDate;
}

function getNewTimeRangeData (p) {
    console.log(formatDate(p.start));
    console.log(formatDate(p.end));

    let start = formatDate(p.start);
    let end = formatDate(p.end);
    let queryString = "./sensor1?start=" + start + "&end=" + end;
    jQuery.getJSON(queryString, function(sensor1_data, status) {
        if (status == "success") {
            console.log(sensor1_data);
            let items = [];
            sensor1_data.sensor1.forEach(function(entry) {
                if (globals.sensor1_cache[entry.index] === undefined) {
                    console.log("->", globals.sensor1_cache[entry.index]);
                    globals.sensor1_cache[entry.index] = 1;

                    let item = {};
                    item['id'] = entry.index;
                    item['x'] = entry.timestamp;
                    item['y'] = entry.temperature;
                    item['group'] = 0;
                    items.push(item);
                    //console.log(item);
                }
            });
            if (items.length > 0) {
                dataset.add(items);
            }
            //console.log(dataset);
            items.length=0; //Tell javascript we are done with this
        } else {
            console.log("Jquery failed to get sensor information");
        }
    });
}


/* example setup code
    https://visjs.github.io/vis-timeline/examples/graph2d/01_basic.html
*/
/*
let items = [
{x: '2014-06-11', y: 10, group: 0},
{x: '2014-06-12', y: 25, group: 0},
{x: '2014-06-13', y: 30, group: 0},
{x: '2014-06-11', y: 10, group: 1},
{x: '2014-06-12', y: 15, group: 1},
{x: '2014-06-13', y: 30, group: 1}
];
*/

//let dataset = new vis.DataSet(items);
let dataset = new vis.DataSet();

let options = {
    start: '2019-12-2 00:00:00',
    end: '2019-12-2 00:30:00'
};
let graph2d = new vis.Graph2d(timelineContainer, dataset, options);

graph2d.on('rangechanged', getNewTimeRangeData);
