"use strict";

// https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API/Tutorial/Basic_usage
let bubbleCanvas = document.getElementById("bubblesCanvas");
let ctx = bubbleCanvas.getContext('2d');

drawBubble(5, 10, 75);
drawBubble(7, 15, 75, true);

class bubbleGlobals {
    static x = bubbleCanvas.width / 2;
    static y = bubbleCanvas.height;
    static y_speed = 1 
    static active = true;

    static old_x;
    static old_y;
    static old_radius;
}

window.setTimeout(moveBubble, 250);


//setTimeout(moveBubble, 2000);
setInterval(moveBubble, 100);

function moveBubble() {
    ctx.clearRect(0, 0, bubbleCanvas.width, bubbleCanvas.height);
    //drawBubble(bubbleGlobals.old_radius, bubbleGlobals.old_y, bubbleGlobals.old_x, true);
    //drawBubble(5, bubbleGlobals.x, bubbleGlobals.y, true);

    bubbleGlobals.y = bubbleGlobals.y - bubbleGlobals.y_speed;
    bubbleGlobals.y_speed += .1;

    if (bubbleGlobals.y < -5) {
        bubbleGlobals.y = bubbleCanvas.height;
        bubbleGlobals.y_speed = 1;
        bubbleGlobals.x =  bubbleCanvas.width / 2;
    }

    let direction = Math.random() * 2 - 1;
    bubbleGlobals.x = bubbleGlobals.x + direction; 
    drawBubble(5, bubbleGlobals.x, bubbleGlobals.y);
    //bubbleGlobals.old_radius = 5;
    //bubbleGlobals.old_x = x;
    //bubbleGlobals.old_y = y;
}


function drawBubble(radius, x, y, reverse = false) {
    ctx.beginPath();
    ctx.arc(x, y, radius, 0, 2 * Math.PI, true);
    ctx.lineWidth = 3;
    if (reverse == false) {
        ctx.strokeStyle = 'blue';
    } else {
        ctx.strokeStyle = 'white';
    }
    ctx.stroke();
}

