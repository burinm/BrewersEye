"use strict";

let d = document;
let body = d.body;

let timelineContainer = d.getElementById("graphTimeline");

class globals {
    //Set if we've fetched this data already
    static sensor1_cache = new Object();
    static sensor2_cache = new Object();
}

function formatDate(d) {

// Javascript is wierd, January = 0, December = 11
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

    //Get time window in seconds
    let timeDiff = Math.round((p.end.getTime()/1000) - (p.start.getTime()/1000));
    console.log("Timeframe is", timeDiff, "seconds");
    //let timeMod = Math.pow(2,Math.floor(timeDiff / 400));
    let timeMod = Math.ceil(timeDiff / 400 * .3);
    console.log("TimeMod is every ", timeMod, "th entry");

    let start = formatDate(p.start);
    let end = formatDate(p.end);

    let queryString = "./sensor1?start=" + start + "&end=" + end + "&mod=" + timeMod;
    jQuery.getJSON(queryString, function(sensor1_data, status) {
        if (status == "success") {
            console.log(sensor1_data);
            let items = [];
            sensor1_data.sensor1.forEach(function(entry) {
                if (globals.sensor1_cache[entry.index] === undefined) {
                    console.log("->", globals.sensor1_cache[entry.index]);
                    globals.sensor1_cache[entry.index] = 1;

                    let item = {};
                    //item['id'] = entry.index; --can't use with groups
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
            console.log("Jquery failed to get sensor1 information");
        }
    });

    queryString = "./sensor2?start=" + start + "&end=" + end + "&mod=" + timeMod;
    jQuery.getJSON(queryString, function(sensor2_data, status) {
        if (status == "success") {
            let items = [];
            sensor2_data.sensor2.forEach(function(entry) {
                if (globals.sensor2_cache[entry.index] === undefined) {
                    globals.sensor2_cache[entry.index] = 1;

                    let item = {};
                    //item['id'] = entry.index; --can't use with groups
                    item['x'] = entry.timestamp;
                    item['y'] = entry.temperature;
                    item['group'] = 1; //Note different group
                    items.push(item);
                }
            });
            if (items.length > 0) {
                dataset.add(items);
            }
            items.length=0; //Tell javascript we are done with this
        } else {
            console.log("Jquery failed to get sensor2 information");
        }
    });
}


/* example setup code
    https://visjs.github.io/vis-timeline/examples/graph2d/01_basic.html
*/
let dataset = new vis.DataSet();

let options = {
    start: '2019-12-2 00:00:00',
    end: '2019-12-2 00:30:00',
    style: 'line',
    dataAxis: {
     left: {
      range: { max: 30, min: 0 }
     },
     right: {
      title: { text: "bubbles" },
      range: { max: 100, min: 0 }
     }
    },
    legend: true
};

let groups = new vis.DataSet();
groups.add({
    id: 1,
    style: 'bar',
    options: {
        drawPoints: {
            size:10,
            style: 'square'
        }
    }
});

let graph2d = new vis.Graph2d(timelineContainer, dataset, options);

graph2d.setGroups(groups);

graph2d.on('rangechanged', getNewTimeRangeData);
