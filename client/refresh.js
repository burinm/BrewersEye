"using strict";

import {graphAddItem, sensorEnum, formatDate} from "./timelineGraph.js";


let ambientTemperature = document.getElementById("temperatureOutdoor");
let fermentationTemperature = document.getElementById("temperatureIndoor");
let bubbleRate = document.getElementById("bubbleRate");

let statusField = document.getElementById("statusField");
statusField.innerHTML="No current alerts";

//For alerts, local latest results
let latest_fermentation_temp = undefined;
let latest_ambient_temp = undefined;
let latest_bubbles_avg = undefined;

function updateStatistics() {



    let queryString = "./latest";
    jQuery.getJSON(queryString, function(all_stats, status) {
        if (status == "success") {
            //console.log(all_stats);
            if (all_stats.sensor1 !== undefined) {
                all_stats.sensor1.entries.forEach(function(entry) {
                    fermentationTemperature.innerHTML="<p style='margin:0;'>"
                        + Math.round(entry.temperature).toString()
                        + "&#176;C&nbsp;"
                        + "<span style='font-size:15px; color:blue;'>Fermentation</span>"
                        + "</p>";

                    graphAddItem(entry.temperature, entry.timestamp, sensorEnum.FERMENTER_TEMP, entry.index);
                    latest_fermentation_temp = entry.temperature;
                });


            }

            if (all_stats.sensor2 !== undefined) {
                all_stats.sensor2.entries.forEach(function(entry) {
                    ambientTemperature.innerHTML="<p style='margin:0'>"
                        + Math.round(entry.temperature).toString()
                        + "&#176;C&nbsp;"
                        + "<span style='font-size:15px; color:orange;'>Ambient</span>"
                        + "</p>";

                    graphAddItem(entry.temperature, entry.timestamp, sensorEnum.AMBIENT_TEMP, entry.index);
                    latest_ambient_temp = entry.temperature;
                });


            }

            let average_count = 0;
            let total_count = 0;
            let latest_time = 0; 
            let earliest_time = 0; 

            //The query returns the last 10 entries for bubbles, average them
            if (all_stats.bubbles !== undefined) {
                all_stats.bubbles.entries.forEach(function(entry) {
                    total_count += entry.average;
                    average_count +=1;
                    if (average_count == 1) {
                        earliest_time = entry.timestamp;
                    }
                    latest_time = entry.timestamp;
                });
            }


            if (average_count > 0) {
                let timeDiff = new Date(latest_time).getTime()/1000 - new Date(earliest_time).getTime()/1000;
                timeDiff = timeDiff / 60; //Seconds to minutes
                //console.log("bubble stat, retreived " + average_count + " entries totaling " + total_count + " over " + timeDiff + " minutes"); 
                let rate = Math.round(Math.round(total_count / timeDiff));
                    bubbleRate.innerHTML="<p style='margin:0'>"
                        + rate.toString()
                        + "<span style='font-size:15px;'>bpm</span>"
                        + "</p>";

                latest_bubbles_avg = rate;
            }

            
        } else {
            console.log("Jquery failed to get sensor2 information");
        }
    });

    let alert_messages = [];
    let alertsEnabledCount = 0;

    // https://theshravan.net/blog/storing-json-objects-in-html5-local-storage/
    let jsonString = localStorage.getItem('alertsList');
    if (jsonString != null) {

        let alertsCurrent = JSON.parse(jsonString);
        console.log(alertsCurrent);

        //Check for any alerts if they are turned on
        alertsCurrent.forEach(function(item) {
            if (item.on == true) {
                alertsEnabledCount += 1;

                // Ambient temperature alerts
                if (item.id == "maxAmbientTemperatureAlert") {
                    if (latest_ambient_temp !== undefined) {
                        if (latest_ambient_temp >= item.constraint) {
                            alert_messages.push( { 'message': "Ambient temperature rose above", 'constraint':item.constraint, 'value':latest_ambient_temp } );
                        }
                    }
                }

                if (item.id == "minAmbientTemperatureAlert") {
                    if (latest_ambient_temp !== undefined) {
                        if (latest_ambient_temp <= item.constraint) {
                            alert_messages.push( { 'message': "Ambient temperature fell below", 'constraint':item.constraint, 'value':latest_ambient_temp } );
                        }
                    }
                }

                // Fermenter temperature alerts
                if (item.id == "maxFermenterTemperatureAlert") {
                    if (latest_fermentation_temp !== undefined) {
                        if (latest_fermentation_temp >= item.constraint) {
                            alert_messages.push( { 'message': "Fermenter temperature rose above", 'constraint':item.constraint, 'value':latest_fermentation_temp } );
                        }
                    }
                }

                if (item.id == "minFermenterTemperatureAlert") {
                    if (latest_fermentation_temp !== undefined) {
                        if (latest_fermentation_temp <= item.constraint) {
                            alert_messages.push( { 'message': "Fermenter temperature fell below", 'constraint':item.constraint, 'value':latest_fermentation_temp } );
                        }
                    }
                }

                // Bubble average alerts
                if (item.id == "maxBubblesAlert") {
                    if (latest_bubbles_avg !== undefined) {
                        if (latest_bubbles_avg >= item.constraint) {
                            alert_messages.push( { 'message': "Average bubble per minute (bmp) exceeded", 'constraint':item.constraint, 'value':latest_bubbles_avg } );
                        }
                    }
                }
            }
        });
    }

    let newHtml = "";
    let currentDate = formatDate(new Date());

    if (alert_messages.length == 0) {
        newHtml="<p style='color:green;'>No current alerts as of: " + currentDate + " (" + alertsEnabledCount + " alerts enabled)</p>";
    }

    alert_messages.forEach(function(item) {
        newHtml += "<li style='color:red;'>" + item.message + "{" + item.constraint + "} Value = {" + item.value + "} " + currentDate + "</li>";
    });

    statusField.innerHTML = newHtml;
}

updateStatistics(); //Do one right away, then set every 10 seconds
setInterval(updateStatistics, 10000);
