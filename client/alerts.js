/* alerts.js
    burin - (c) 2019

    Data structure that represents both the widgets
    on the alerts.html page and the alert constraints

    At the moment, localStorage is used to save the
    alerts to disk (like cookies)

    TODO: move alerts peristant storage to database

    Widgets are dynamically created and assigned from
    the alertsList structure. This means that in future
    versions, new alert types can be dynamically added to
    the alerts.html page and be activated.

*/
"use strict";

let submitAlerts = document.getElementById("submitAlerts");
let alertsPageStatus = document.getElementById("alertsPageStatus");

let alertsList = [
                {
                    'on': false,
                    'id': 'maxAmbientTemperatureAlert',
                    'desc': "Ambient temperature rises over:",
                    'constraint': 50
                },
                {
                    'on': false,
                    'id': 'minAmbientTemperatureAlert',
                    'desc': "Ambient temperature falls below:",
                    'constraint': 50
                },
                {
                    'on': false,
                    'id': 'maxFermenterTemperatureAlert',
                    'desc': "Fermenter temperature rises above:",
                    'constraint': 50
                },
                {
                    'on': false,
                    'id': 'minFermenterTemperatureAlert',
                    'desc': "Fermenter temperature falls below:",
                    'constraint': 50
                },
                {
                    'on': false,
                    'id': 'maxBubblesAlert',
                    'desc': "Bubbles per minute (bpm) rise above:",
                    'constraint': 50
                },
];

let alertsContainer = document.getElementById("alertsContainer");

alertsContainer.innerHTML="";
let html = "";

//Check for already stored alerts list
let jsonString = localStorage.getItem('alertsList');
if (jsonString !== null) {
    console.log("Loading alerts list from local storage");
    alertsList = JSON.parse(jsonString);
}

/*
<!--Template for code reference below-->
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

//Draw widgets
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

function enableAlertElement(index) {
    elementDescs[index].className = "turnedOn";
    elementValues[index].className = "turnedOn";
    elementSliders[index].className = "slider sliderOn";
    elementSliders[index].disabled = false;
}

function disableAlertElement(index) {
    elementDescs[index].className = "greyedOut";
    elementValues[index].className = "greyedOut";
    elementSliders[index].className = "slider sliderOff";
    elementSliders[index].disabled = true;
}

/* Fill up lists to keep track of widgets
   Fill with values in alertsList
*/
alertsList.forEach(function(entry, index) {
    console.log("Initializing:" + entry.id);

    elementAlerts[index] = document.getElementById(entry.id + "Alert");
    elementDescs[index] = document.getElementById(entry.id + "Desc");
    elementSliders[index] = document.getElementById(entry.id + "Slider");
    elementValues[index]= document.getElementById(entry.id + "Value");

    elementAlerts[index].checked = alertsList[index].on;
    elementSliders[index].value = alertsList[index].constraint;
    elementValues[index].innerHTML = alertsList[index].constraint;

    if (alertsList[index].on == true) {
        enableAlertElement(index);
    } else {
        disableAlertElement(index);
    }

    /* checkbox event */
    elementAlerts[index].onclick = function(value) {
        if (elementAlerts[index].checked == true) {
            enableAlertElement(index);
            alertsPageStatus.innerHTML = "changed";
            alertsList[index].on = true;
            console.log("new value checked");
        } else {
            disableAlertElement(index);
            alertsPageStatus.innerHTML = "changed";
            alertsList[index].on  = false;
            console.log("new value unchecked");
        }
    }

    /* slider event */
    elementSliders[index].onchange = function(value) {
        elementValues[index].innerHTML = elementSliders[index].value;
        alertsPageStatus.innerHTML = "changed";
        console.log(typeof(value));
        alertsList[index].constraint = elementSliders[index].value;
        console.log("new value set");
    }
});

/* Save changed values to persistant storage */
submitAlerts.onclick = (function() {
    let jsonString = JSON.stringify(alertsList);
    console.log("Saving: " + jsonString);
    localStorage.setItem('alertsList', jsonString);

    alertsPageStatus.innerHTML = "Current Settings (saved)"
});

/* Setup test email values */
let testEmail = document.getElementById("testEmail");
let emailAddress = document.getElementById("emailAddress");

testEmail.onclick = (function() {
    let destination=emailAddress.innerHTML;
    let subject="Brewers's eye test message - " + new Date();
    let message="<html>";

    message += "<p>This is a test email from the Brewer's Eye App";
    if  (alertsList.length == 0) {
        message += "<p>You have the no alerts enabled";
    } else {
        message += "<p>You have the following alerts enabled:";

        alertsList.forEach(function(item) {
            if (item.on) {
                message += "<li>";
                message += item.desc + " " + item.constraint;
                message += "</li>";
            }
        });
    }

    message += "<p><p>Have Fun!";
    message += "</html>";

    /* Send email through tonrnado API */
    let queryString="./email?destination=" + destination + "&subject=" + subject + "&message=" + message;
    jQuery.getJSON(queryString, function(ret, status) {
        if (status == "success") {
            if (ret['error'] == 200) {
               console.log("Sent!");
            } else {
               console.log("Error:" + ret['error']);
            }
        }
    });
});
