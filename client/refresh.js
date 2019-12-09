"using strict";

import {graphAddItem, sensorEnum} from "./timelineGraph.js";


let ambientTemperature = document.getElementById("temperatureOutdoor");
let fermentationTemperature = document.getElementById("temperatureIndoor");
let bubbleRate = document.getElementById("bubbleRate");


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
                //graphAddItem(entry.temperature, entry.timestamp, 0);
                     
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
                let rate = Math.round(total_count / timeDiff);
                    bubbleRate.innerHTML="<p style='margin:0'>"
                        + Math.round(rate).toString()
                        + "<span style='font-size:15px;'>bpm</span>"
                        + "</p>";
            }

            
        } else {
            console.log("Jquery failed to get sensor2 information");
        }
    });
}

updateStatistics(); //Do one right away, then set every 10 seconds
setInterval(updateStatistics, 10000);
