"use strict";


let alertsList = [
                {
                    on: false,
                    id: 'maxAmbientTemperature',
                    desc: "Ambient temperature rises over:",
                    value: null
                },
                {
                    on: false,
                    id: 'minAmbientTemperature',
                    desc: "Ambient temperature falls below:",
                    value: null
                },
                {
                    on: false,
                    id: 'maxFermenterTemperature',
                    desc: "Fermenter temperature rises above:",
                    value: null
                },
                {
                    on: false,
                    id: 'minFermenterTemperature',
                    desc: "Fermenter temperature falls below:",
                    value: null
                },
                {
                    on: false,
                    id: 'maxBubbles',
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
                html += "<input id='" + entry.id + "Alert" + "' type='checkbox'>";
            html += "</div>";

            html += "<div style='float:left; width:40%'>";
                html += "<p id='" + entry.id + "Desc" + "' class='greyedOut'>" + entry.desc + "</p>";
            html += "</div>";

            html += "<div style='float:left; width:5%'>";
                let value = 0;
                html += "<p id ='" + entry.id + "Value" + "' class='greyedOut'>" + value + "</p>";
            html += "</div>";

            html += "<div style='float:left; width:50%'>";
                html += "<input id='" + entry.id + "Slider" + "' type='range' min='0' max='100';' class='slider sliderOff' disabled>";
            html += "</div>";

            html += "<div class='clear_formatting'></div-->";
        html += "</p>";
});

alertsContainer.innerHTML=html;

let elementAlerts = [];
let elementDescs = [];
let elementSliders = [];
let elementValues = [];

alertsList.forEach(function(entry, index) {
    elementAlerts[index] = document.getElementById(entry.id + "Alert");
    elementDescs[index] = document.getElementById(entry.id + "Desc");
    elementSliders[index] = document.getElementById(entry.id + "Slider");
    elementValues[index]= document.getElementById(entry.id + "Value");

    console.log(entry.id + "Alert");
    elementAlerts[index].onclick = function(value) {
        if (elementAlerts[index].checked == true) {
            elementDescs[index].className = "turnedOn";
            elementValues[index].className = "turnedOn";
            elementSliders[index].className = "slider sliderOn";
            elementSliders[index].disabled = false;
        } else {
            elementDescs[index].className = "greyedOut";
            elementValues[index].className = "greyedOut";
            elementSliders[index].className = "slider sliderOff";
            elementSliders[index].disabled = true;
        }
    }

    console.log(entry.id + "Slider");
    elementSliders[index].onchange = function(value) {
        elementValues[index].innerHTML = elementSliders[index].value;
    }
});

/*
<!--Template-->
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


