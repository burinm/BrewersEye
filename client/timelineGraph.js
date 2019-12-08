"use strict";

let d = document;
let body = d.body;

let graph2dContainer = d.getElementById("graph2dGraph");
let timelineContainer = d.getElementById("timelineGraph");

const sensorEnum = {
    FERMENTER_TEMP: 0,
    AMBIENT_TEMP: 1,
    BUBBLES_AVG: 2
}

class globals {
    //Set if we've fetched this data already
    static sensor_cache = [];
}



function graphAddItem(value, timestamp, group, index) {
    let item = {};
    item['x'] = timestamp 
    item['y'] = value;
    item['group'] = group;
    dataset.add(item);
    globals.sensor_cache[group][index] = 1;
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

    if (p.manual === undefined) {
        //Update timeline graph data too
        p.manual = true;
        getNewTimelineData(p);
        timeline.setWindow(p.start, p.end);
    }

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
            //console.log(sensor1_data);
            let items = [];
            sensor1_data.sensor1.forEach(function(entry) {
                if (globals.sensor_cache[sensorEnum.FERMENTER_TEMP][entry.index] === undefined) {
                    globals.sensor_cache[sensorEnum.FERMENTER_TEMP][entry.index] = 1;

                    let item = {};
                    //item['id'] = entry.index; --can't use with groups
                    item['x'] = entry.timestamp;
                    item['y'] = entry.temperature;
                    item['group'] = sensorEnum.FERMENTER_TEMP;
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
                if (globals.sensor_cache[sensorEnum.AMBIENT_TEMP][entry.index] === undefined) {
                    globals.sensor_cache[sensorEnum.AMBIENT_TEMP][entry.index] = 1;

                    let item = {};
                    //item['id'] = entry.index; --can't use with groups
                    item['x'] = entry.timestamp;
                    item['y'] = entry.temperature;
                    item['group'] = sensorEnum.AMBIENT_TEMP; //Note different group
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

function getNewTimelineData(p) {
    console.log(formatDate(p.start));
    console.log(formatDate(p.end));

    if (p.manual === undefined) {
        //Update temperarute graph data too
        p.manual = true;
        getNewTimeRangeData(p);
        graph2d.setWindow(p.start, p.end);
    }


    /* Bubble average uses a different strategy.

        Display average bubbles over each hour in timeline
        cache is marked with the top of the hour that is loaded

        TODO: We are adding an hour's worth of seconds - will this
              blow up and return a time that isn't exactly an hour?
              i.e. leap seconds, etc..
    */

    /* Round to nearest hour
        https://stackoverflow.com/questions/10789384/round-a-date-to-the-nearest-5-minutes-in-javascript
    */
    let an_hour = 60 * 60 * 1000;
    let start_nearest_hour = new Date(Math.round(p.start.getTime() / an_hour) * an_hour);

    let debugger_count = 0;
    for (let chunk = start_nearest_hour.getTime(); chunk < p.end.getTime(); chunk += an_hour) {
        debugger_count += 1;
        if (debugger_count > 100) break;

        let chunk_date = formatDate(new Date(chunk));
        let end_date = formatDate(new Date(chunk + an_hour));

        console.log("->" + chunk_date + "," + end_date);

        let queryString = "./bubbles?start=" + chunk_date + "&end=" + end_date + "&mod=1";
        jQuery.getJSON(queryString, function(bubbles_data, status) {
            if (status == "success") {
                let average_count = 0;
                let average_total = 0;

                //Use just the fist index of the query to mark cache
                let first_entry = bubbles_data.bubbles[0];
                if (first_entry !== undefined) {
                    if (globals.sensor_cache[sensorEnum.BUBBLES_AVG][first_entry.index] === undefined) {
                        globals.sensor_cache[sensorEnum.BUBBLES_AVG][first_entry.index] = 1;

                        bubbles_data.bubbles.forEach(function(entry) {
                            average_total += entry.average;
                            average_count += 1;
                        });


                        let average_bpm = 0;
                        if (average_count > 0) {
                            average_bpm = average_total / average_count;
                            average_bpm = Math.round(average_bpm / 10);
                        }

                        console.log("avg count " + average_count + " avg=" + average_bpm);

                        let item = {};
                        item['start'] = first_entry.timestamp; //Only entering on the hour
                        item['content'] = average_bpm.toString();
                        item['group'] = 0; //TODO make timeline ENUM
                        item['editable'] = false; //Note different group

                        dataset2.add(item);
                    }
                } // else is already in cache
            } else {
                console.log("Jquery failed to get bubbles information");
            }
        });
    }

}

//Setup caches
globals.sensor_cache[sensorEnum.FERMENTER_TEMP] = new Object;
globals.sensor_cache[sensorEnum.AMBIENT_TEMP] = new Object;
globals.sensor_cache[sensorEnum.BUBBLES_AVG] = new Object;

let now_date = Date.now();
let eightHours = (60 * 60 * 8) * 1000;
let start_date = new Date(now_date - eightHours);
let end_date = new Date(now_date);

console.log("Start charts at:", start_date);
console.log("End charts at:", end_date);

/* graph2d - example setup code
    https://visjs.github.io/vis-timeline/examples/graph2d/01_basic.html
*/
let dataset = new vis.DataSet();

let options = {
    start: start_date,
    end: end_date,
    style: 'line',
    dataAxis: {
     left: {
      title: { text: "Temp C" },
      range: { max: 30, min: 0 }
     },
/*
     right: { //grrr, seems to be broken
      title: { text: "bubbles" },
      range: { max: 100, min: 0 }
     }
*/
    },
    showMajorLabels: false,
    showMinorLabels: false,
    legend: true
};


let graph2d = new vis.Graph2d(graph2dContainer, dataset, options);

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
graph2d.setGroups(groups);

graph2d.on('rangechanged', getNewTimeRangeData);

/* Timeline - https://almende.github.io/vis/docs/timeline/
*/

let dataset2 = new vis.DataSet();
let options2 = {
    locales: { myEN: {current: 'current', time: 'time'}},
    locale: 'myEN',
    start: start_date,
    end: end_date,
    orientation: 'top',
    //editable: { add: true, remove: true},
    editable: true,
    selectable: true,

    onUpdate: function(item, callback) {
        // https://almende.github.io/vis/docs/timeline/index.html#Events
        item.content = prompt('Edit item:', item.content);
        if (item.content != null) {
            callback(item); // send back adjusted item
        }
        else {
            callback(null); // cancel updating the item
        }
    },

    onAdd: function(item, callback) {
        // https://almende.github.io/vis/docs/timeline/index.html#Events
        item.content = prompt('Add event:', item.content);
        item.editable = true;
        if (item.content != null) {
            callback(item); // send back adjusted item
        }
        else {
            callback(null); // cancel updating the item
        }
    },

    onDropObjectOnItem: function(o, item) {
        console.log("onDropObjectOnItem - do nothing");
    },

    onMove: function(item, callback) {
        console.log("onMove - do nothing");
        callback(null);
    },

};


let timeline = new vis.Timeline(timelineContainer, dataset2, options2);

let groups2 = new vis.DataSet();

groups2.add(
 { id: 0, content: '<p style="margin: 0;">Bubble</p> \
                    <p style="margin: 0;">avg</p>',
   visible: true,
 }
);

groups2.add(
 { id: 1, content: 'Events&nbsp;', visible: true } // nbsp hack to set column width
);

timeline.setGroups(groups2);
timeline.on('rangechanged', getNewTimelineData);
timeline.on('select', function(items, event){
    console.log(items);
});

export {graphAddItem, sensorEnum};
