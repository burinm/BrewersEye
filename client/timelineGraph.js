/* timelineGraph.js - Query data from mySQL and fill in chart
    burin (c) 2019

    There are two displays working here, a graph2d and a timeline.
    graph 2d is filled out with ambient, fermentation, and bubble data.
    Timeline is also filled out with bubble data and custom events.

    There is an attempt to cache the data lookups by marking their
    unique index in an array as visited. This keeps us from loading
    the data twiced into the graph/timeline.

    TODO: This, however, needs to be changed for the bubble lookup,
    because it is still querying the database, even if it already
    has the data (perhaps purge bubble data, and only ever averge 10?)

    Whenever a graph event occurs, the timeframe of the current
    display is sent. The current strategy is to divide the timeline
    into reasonable sized pieces for that resolution and use the "mod"
    modifier in mySQL to only return each nth piece.

    This strategy works well for zooming out.

    To try and display the bubble data, data is only queried on
    the hour, and the last hour's worth of data is retrieved to
    calculate an average.
*/

"use strict";

let graph2dContainer = document.getElementById("graph2dGraph");
let timelineContainer = document.getElementById("timelineGraph");

//Represents group in the graph object, and the cache index
const sensorEnum = {
    FERMENTER_TEMP: 0,
    AMBIENT_TEMP: 1,
    BUBBLES_AVG: 2
}

class globals {
    /* Set if we've fetched this data already
            2d array - [group][index]
    */
    static sensor_cache = [];
}

//Helper to add an item to the graph2d object
function graphAddItem(value, timestamp, group, index) {
    let item = {};
    item['x'] = timestamp;
    item['y'] = value;
    item['group'] = group;
    dataset.add([item]);
    globals.sensor_cache[group][index] = 1;
}

//Helper to format the date as mySQL requires in queries
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

//Over a timeframe, find the amount to skip over so that queries will be fast
function getTimeMod(start, end) {

    //Get time window in seconds
    let timeDiff = Math.round((end.getTime()/1000) - (start.getTime()/1000));

    /* Eyeballed this when zooming out the graph, and from the data density.
        timeMod = ~250 entries retrieved
    */
    let timeMod = Math.ceil(timeDiff / 400 * .3);
    console.log("Timeframe is", timeDiff, "seconds, TimeMod is every ", timeMod, "th entry");
return timeMod;
}

// Given a timerange, fill graph2d with data from mySQL
function getNewTimeRangeData (p) {
    //console.log(formatDate(p.start));
    //console.log(formatDate(p.end));

    if (p.manual === undefined) {
        //Update timeline graph data too
        p.manual = true;
        getNewTimelineData(p);
        timeline.setWindow(p.start, p.end);
    }

    let timeMod = getTimeMod(p.start, p.end);
    let start = formatDate(p.start);
    let end = formatDate(p.end);

    /* sensor 1 fetch - fermenter temperature */
    let queryString = "./sensor1?start=" + start + "&end=" + end + "&mod=" + timeMod;
    jQuery.getJSON(queryString, function(sensor1_data, status) {
        if (status == "success") {
            let items = [];
            console.log("returned " +  sensor1_data.sensor1.length + " sensor1 entries");
            sensor1_data.sensor1.forEach(function(entry) {
                if (globals.sensor_cache[sensorEnum.FERMENTER_TEMP][entry.index] === undefined) {
                    globals.sensor_cache[sensorEnum.FERMENTER_TEMP][entry.index] = 1;

                    let item = {};
                    //item['id'] = entry.index; --can't use with groups
                    item['x'] = entry.timestamp;
                    item['y'] = entry.temperature;
                    item['group'] = sensorEnum.FERMENTER_TEMP;
                    items.push(item);
                }
            });
            if (items.length > 0) {
                dataset.add(items);
            }
            items.length=0; //Tell javascript we are done with this?
        } else {
            console.log("Jquery failed to get sensor1 information");
        }
    });

    /* sensor 2 fetch  - ambient temperature */
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

/* Given a timerange, fill timeline with bubble averages on the hour,
    also put bubble averages into graph2d
*/
function getNewTimelineData(p) {
    //console.log(formatDate(p.start));
    //console.log(formatDate(p.end));

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

    let timeMod = Math.ceil(getTimeMod(p.start, p.end) / 100);
    console.log("Bubble timeMod=" + timeMod);
    let debugger_count = 0;
    let actual_query_count = 0;
    for (let chunk = start_nearest_hour.getTime(); chunk < p.end.getTime(); chunk += an_hour) {
        debugger_count += 1;

        // TODO - this is just a performance hack for Demo, fix caching
        if (actual_query_count > 25) break;

        //Timemod is used here to grab every nth hour
        if (debugger_count % timeMod == 0) {
            actual_query_count += 1;

            let chunk_date = formatDate(new Date(chunk));
            let end_date = formatDate(new Date(chunk + an_hour));

            //console.log("->" + chunk_date + "," + end_date);

            //Gather all the values over this hour
            let queryString = "./bubbles?start=" + chunk_date + "&end=" + end_date + "&mod=1";
            jQuery.getJSON(queryString, function(bubbles_data, status) {
                if (status == "success") {
                    let average_count = 0;
                    let average_total = 0;

                    //Use just the first index of the query to mark cache
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
                                average_bpm = Math.round(average_total / 60); //bubbles over an hour
                            }

                        /* timeline
                        */
                            let timeline_item = {};
                            timeline_item['start'] = first_entry.timestamp; //Only entering on the hour
                            timeline_item['content'] = average_bpm.toString();
                            timeline_item['group'] = 0; //TODO make timeline ENUM
                            timeline_item['style'] = "color:purple; border-color: purple; background-color: white;";
                            dataset2.add(timeline_item);
                        /* graph2d
                        */
                            let item = {};
                            item['x'] = first_entry.timestamp; //Only entering on the hour
                            //TODO for now, scale to fit on graph
                            average_bpm = Math.round(average_bpm / 5);
                            item['y'] = average_bpm.toString();
                            item['group'] = sensorEnum.BUBBLES_AVG; //TODO make timeline ENUM
                            item['editable'] = false; //Note different group
                            dataset.add(item);
                        }
                    } // else is already in cache
                } else {
                    console.log("Jquery failed to get bubbles information");
                }
            });
        }
    }
    console.log("Bubbles average made " + actual_query_count + " queries to the database");
}

/* Main code starts here */

/* Setup caches */
globals.sensor_cache[sensorEnum.FERMENTER_TEMP] = new Object;
globals.sensor_cache[sensorEnum.AMBIENT_TEMP] = new Object;
globals.sensor_cache[sensorEnum.BUBBLES_AVG] = new Object;

/* For reference, log current timeframe */
let now_date = Date.now();
let eightHours = (60 * 60 * 8) * 1000;
let start_date = new Date(now_date - eightHours);
let end_date = new Date(now_date);

console.log("Start charts at:", start_date);
console.log("End charts at:", end_date);

/* setup main display graph

    graph2d - example setup code
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
    // legend: true
};

let graph2d = new vis.Graph2d(graph2dContainer, dataset, options);

let groups = new vis.DataSet();
groups.add(
 {
    id: sensorEnum.FERMENTER_TEMP,
    style: 'line',
    options: {
        drawPoints: {
            size:5,
            style: 'circle'
        }
    }
 }
);

groups.add(
 {
    id: sensorEnum.AMBIENT_TEMP,
    style: 'line',
    options: {
        drawPoints: {
            size:5,
            style: 'circle'
        }
    }
 }
);

groups.add(
 {
    id: sensorEnum.BUBBLES_AVG,
    /* There must be a bug, this gets assigned as vis-graph-group0 */
    className: "vis-graph-group2",
    style: 'line',
    options: {
        drawPoints: {
            size:5,
            style: 'circle',
        }
    }
 }
);

graph2d.setGroups(groups);
graph2d.on('rangechanged', getNewTimeRangeData);

/* Setup timeline graph

    Timeline - https://almende.github.io/vis/docs/timeline/
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
        item.style = " color:black; background-color: yellow;";
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

let timelineGroups = new vis.DataSet();

timelineGroups.add(
 { id: 0, content: '<p style="margin: 0;">Bubble</p> \
                    <p style="margin: 0;">avg</p>',
   visible: true,
   subgroupStack: true, //Pile bubble averages on top of each other
 }
);

timelineGroups.add(
 { id: 1, content: 'Events&nbsp;', // nbsp hack to set column width
   visible: true,
 }
);

timeline.setGroups(timelineGroups);
timeline.on('rangechanged', getNewTimelineData);
timeline.on('select', function(items, event){
    console.log(items);
});

export {graphAddItem, sensorEnum, formatDate};
