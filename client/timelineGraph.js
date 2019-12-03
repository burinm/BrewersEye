"use strict";

let d = document;
let body = d.body;

let timelineContainer = d.getElementById("graphTimeline");

function formatDate(d) {
let displayDate =   d.getFullYear() + "-" +
            ("00" + d.getMonth()).slice(-2) + "-" +
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
}


/* example setup code
    https://visjs.github.io/vis-timeline/examples/graph2d/01_basic.html
*/
let items = [
{x: '2014-06-11', y: 10, group: 0},
{x: '2014-06-12', y: 25, group: 0},
{x: '2014-06-13', y: 30, group: 0},
{x: '2014-06-11', y: 10, group: 1},
{x: '2014-06-12', y: 15, group: 1},
{x: '2014-06-13', y: 30, group: 1}
];

let dataset = new vis.DataSet(items);
dataset.add({x: '2014-06-01', y: 1, group: 0});
dataset.add({x: '2014-06-01', y: 1, group: 0});
dataset.add({x: '2014-06-01', y: 1, group: 0});
dataset.add({x: '2014-06-01', y: 1, group: 0});
dataset.add({x: '2014-06-01', y: 1, group: 0});
console.log(dataset);

let options = {
    start: '2014-06-10',
    end: '2014-06-18'
};
let graph2d = new vis.Graph2d(timelineContainer, dataset, options);

graph2d.on('rangechanged', getNewTimeRangeData);
