"use strict";


let alertsList = [
                {
                    on: false,
                    id: 'maxAmbientTemperatureAlert',
                    desc: "Ambient temperature rises over:",
                    value: null
                },
                {
                    on: false,
                    id: 'minAmbientTemperatureAlert',
                    desc: "Ambient temperature falls below:",
                    value: null
                },
                {
                    on: false,
                    id: 'maxFermenterTemperatureAlert',
                    desc: "Fermenter temperature rises above:",
                    value: null
                },
                {
                    on: false,
                    id: 'minFermenterTemperatureAlert',
                    desc: "Fermenter temperature falls below:",
                    value: null
                },
                {
                    on: false,
                    id: 'maxBubblesAlert',
                    desc: "Bubbles per minute (bpm) rise above:",
                    value: null
                },
];
                    

let alertsContainer = document.getElementById("alertsContainer");

alertsContainer.innerHTML="";


let html = "";

alertsList.forEach(function(entry) {
    html += "<p>";

            html += "<div style='float:left; width:5%'>";
                html += "<input id='" + entry.id + "' type='checkbox'>";
            html += "</div>";

            html += "<div style='float:left; width:40%'>";
                html += "<p style='font-size: 20px; margin:0;'>" + entry.desc + "</p>";
            html += "</div>";

            html += "<div style='float:left; width:5%'>";
                let value = 0;
                html += "<p style='font-size: 20px; margin:0;'>" + value + "</p>";
            html += "</div>";

            html += "<div style='float:left; width:50%'>";
                html += "<input id='maxAmbientTemperature' type='range' min='0' max='100' style='width:100%;' class='slider'>";
            html += "</div>";

            html += "<div class='clear_formatting'></div-->";
        html += "</p>";
});

alertsContainer.innerHTML=html;
/*
<!--Alerts-->
        <p>
            <div style="float:left; width:5%">
                <input id="maxAmbientTemperatureAlert" type="checkbox">          
            </div>
            <div style="float:left; width:45%">
                <p style="font-size: 20px; margin:0;">Ambient temperature rises over X degrees C</p>
            </div>
            <div style="float:left; width:50%">
                <input id="maxAmbientTemperature" type="range" min="0" max="100" style="width:100%;" class="slider">
            </div>
            <div class="clear_formatting"></div-->
        </p>
*/


