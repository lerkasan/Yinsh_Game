var globx;
var globy;
var counter;
var gameid;
var limits = null;
var old_xn, xn;
var old_yn, yn;
var free = true;
var valid = true;
var old_ext_lim;
var player_color = 'green';
var comp_color = 'magenta'

canvas_pic = new Image();              
canvas_pic.src = '/static/canvas.png'; 

canvas_pic.onload = function() {     
  canvas = document.getElementById('canvas'); 
  context = canvas.getContext('2d');
  context.drawImage(canvas_pic, 0, 0); 
}
            
erase_pic = new Image();  
erase_pic.src = '/static/erase4.png';
circle_pic = new Image();              
circle_pic.src = '/static/circle20.png'; 
disk_pic = new Image();
disk_pic.src = '/static/moon4.png';
allowed_pic = new Image();
allowed_pic.src = '/static/allowed.png';

circle_pic_comp = new Image();              
circle_pic_comp.src = '/static/circle_magenta.png'; 
disk_pic_comp = new Image();
disk_pic_comp.src = '/static/disk_magenta.png';

function isInteger(x) {
  return x % 1 === 0;
}

function makeid(n) {
  var text = "";
  var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
  for( var i=0; i < n; i++ )
    text += possible.charAt(Math.floor(Math.random() * possible.length));
  return text;
}

function erase(x,y) {
  context.drawImage(erase_pic, x + 11, y - 4);
}

function draw(x,y,image,color) {
  if (image == 'circle') 
    if (color == 1)
      context.drawImage(circle_pic, x + 14, y - 2);
    else
      context.drawImage(circle_pic_comp, x + 14, y - 2);
  if (image == 'disk')
    if (color == 1) 
      context.drawImage(disk_pic, x+28, y + 12);
    else
      context.drawImage(disk_pic_comp, x+28, y + 12);
  if (image == 'allowed')
    context.drawImage(allowed_pic, x + 11, y - 4); 
}

function process() {    	
  gameid=makeid(20);													
  $.get("http://localhost:8000/play/", {game_id: gameid}, process2);
}

function process2() {    
  counter = true; 
  canvas.onclick = function(e) {
    var x = (e.pageX - canvas.offsetLeft);
    var y = (e.pageY - canvas.offsetTop);	
    var delta_x = (x % 52) / 52;
    if (delta_x > 0.5)
      x = 52 * ((x / 52 >> 0)); 
    else
      x = 52 * ((x / 52 >> 0) - 1); 
    var delta_y = (y % 30) / 30;
    if (delta_y > 0.5)
      y = 30 * ((y / 30 >> 0));
    else 
      y = 30 * ((y / 30 >> 0) - 1);
    globx = x;
    globy = y;
    xn = x - 260;
    xn = xn / 52 >> 0;
    yn = 300 - y;
    yn = ((yn / 30 >> 0) + xn) / 2;	
    valid = true;

    if ((Math.abs(xn) > 5) || (Math.abs(yn) > 5) || (xn*yn == 25))
      valid = false;
    if ((Math.abs(xn) == 5) && (yn == 0))
      valid = false;
    if ((Math.abs(yn) == 5) && (xn == 0))
      valid = false;
    if ((Math.abs(xn) + Math.abs(yn) >= 6) && (xn*yn < 0) && (Math.abs(xn) >= 3) && (Math.abs(yn) <= 3))
      valid = false;
    if ((Math.abs(xn) + Math.abs(yn) >= 6) && (xn*yn < 0) && (Math.abs(xn) <= 3) && (Math.abs(yn) >= 3))
      valid = false;
    if ((x < 0) || (x > 520) || (y < 30) || (y > 570))
      valid = false;
    if (!isInteger(yn))
      valid = false;
    if (valid) {
      $.getJSON("http://localhost:8000/ajax/", {x: xn, y: yn, counts: counter, game_id: gameid}, onAjaxSuccess);
      counter = !counter;
    } else 
      alert('This move is not allowed');
  }
}

function onAjaxSuccess(json) {
  if ((limits != null) && json.free && json.previous != null) {
    old_xn = Number(json.previous.xn);
    old_yn = Number(json.previous.yn);
    old_realx = 52*old_xn+260;
    old_realy = 300-30*(2*old_yn-old_xn);
    //$('#answer').append("("+old_xn+", "+old_yn+"); ");
    //old_xn = Number(limits.old.xn);
    //old_yn = Number(limits.old.yn);
    xn_vert_gt = Number(limits.vert_gt.xn);
    yn_vert_gt = Number(limits.vert_gt.yn);
    xn_horiz_gt = Number(limits.horiz_gt.xn);
    yn_horiz_gt = Number(limits.horiz_gt.yn);
    xn_horiz_lt = Number(limits.horiz_lt.xn);
    yn_horiz_lt = Number(limits.horiz_lt.yn);
    xn_vert_lt = Number(limits.vert_lt.xn);
    yn_vert_lt = Number(limits.vert_lt.yn);
    xn_diag_gt = Number(limits.diag_gt.xn);
    yn_diag_gt = Number(limits.diag_gt.yn);
    xn_diag_lt = Number(limits.diag_lt.xn);
    yn_diag_lt = Number(limits.diag_lt.yn);

    if (old_ext_lim != null) {
      for (var key in old_ext_lim) {
        if (old_ext_lim[key] != null) {
          x = Number(old_ext_lim[key].xn);
          y = Number(old_ext_lim[key].yn);
          realx = 52*x+260;
          realy = 300-30*(2*y-x);
          erase(realx,realy);
        }
      }
      old_ext_lim = null;
    }

    realx = 52*xn_vert_gt+260;
    for (yi = old_yn+1; yi < yn_vert_gt; yi++) {
      realy = 300-30*(2*yi-xn_vert_gt);
      erase(realx, realy);
    }

    realx = 52*xn_vert_lt+260;
    for (yi = old_yn; yi > yn_vert_lt; yi--) {
      realy = 300-30*(2*yi-xn_vert_lt);
      erase(realx, realy);
    }

    for (xi = old_xn+1; xi < xn_horiz_gt; xi++) {
      realx = 52*(xi)+260;
      realy = 300-30*(2*yn_horiz_gt-xi);
      erase(realx, realy);
    }

    for (xi = old_xn; xi > xn_horiz_lt; xi--) {
      realx = 52*(xi)+260;
      realy = 300-30*(2*yn_horiz_lt-xi);
      erase(realx, realy);
    }

    for (xi = old_xn+1; xi < xn_diag_gt; xi++) {
      realx = 52*(xi)+260;
      realxdiag = 52*(xn_diag_gt)+260;
      yd = old_yn+(xi - old_xn)*(yn_diag_gt - old_yn)/(xn_diag_gt - old_xn);
      realy = 300-30*(2*yd-xi);
      erase(realx, realy);
    }

    for (xi = old_xn; xi > xn_diag_lt; xi--) {
      realx = 52*(xi)+260;
      yd = old_yn+(xi - old_xn)*(yn_diag_lt - old_yn)/(xn_diag_lt - old_xn);
      realy = 300-30*(2*yd-xi);
      erase(realx, realy);
    }
    if ((old_xn != xn ) || (old_yn != yn))
      draw(old_realx, old_realy, 'disk', 1);
  }

  if (json.free && valid) {
    free = true;
    draw(globx,globy,'circle', 1);
    $('#coordinates').html("("+xn+", "+yn+")");
    //$('#answer').html(JSON.stringify(json.changed));
    //$('#coordinates').append("("+xn+", "+yn+"); ");
   // $('#answer').html(JSON.stringify(json.ext_lim));

    if (json.ext_lim != null) {
      ext_lim = JSON.parse(json.ext_lim);
      for (var key in ext_lim) {
        if (ext_lim[key] != null) {
          x = Number(ext_lim[key].xn);
          y = Number(ext_lim[key].yn);
          realx = 52*x+260;
          realy = 300-30*(2*y-x);
          draw(realx,realy,'allowed',1);
          old_ext_lim = ext_lim;
        }
      } 
    }

    if (json.changed != null) {
      changed = JSON.parse(json.changed);
      if (changed != null) {
        for (var i = 0; i < changed.length; i++) { 
          x = Number(changed[i].xn);
          y = Number(changed[i].yn);
          color = Number(changed[i].player);
          realx = 52*x+260;
          realy = 300-30*(2*y-x);
          draw(realx,realy,'disk',color);
        }
      }
    }
    
    if (json.limits != null) {
      limits = JSON.parse(json.limits);
      xn_vert_gt = Number(limits.vert_gt.xn);
      yn_vert_gt = Number(limits.vert_gt.yn);
      xn_horiz_gt = Number(limits.horiz_gt.xn);
      yn_horiz_gt = Number(limits.horiz_gt.yn);
      xn_horiz_lt = Number(limits.horiz_lt.xn);
      yn_horiz_lt = Number(limits.horiz_lt.yn);
      xn_vert_lt = Number(limits.vert_lt.xn);
      yn_vert_lt = Number(limits.vert_lt.yn);
      xn_diag_gt = Number(limits.diag_gt.xn);
      yn_diag_gt = Number(limits.diag_gt.yn);
      xn_diag_lt = Number(limits.diag_lt.xn);
      yn_diag_lt = Number(limits.diag_lt.yn);

      realx = 52*xn_vert_gt+260;
      for (yi = yn+1; yi < yn_vert_gt; yi++) {
        realy = 300-30*(2*yi-xn_vert_gt);
        draw(realx, realy, 'allowed', 1);
      }

      realx = 52*xn_vert_lt+260;
      for (yi = yn-1; yi > yn_vert_lt; yi--) {
        realy = 300-30*(2*yi-xn_vert_lt);
        draw(realx, realy, 'allowed', 1);
      }

      for (xi = xn+1; xi < xn_horiz_gt; xi++) {
        realx = 52*(xi)+260;
        realy = 300-30*(2*yn_horiz_gt-xi);
        draw(realx, realy, 'allowed', 1);
      }

      for (xi = xn-1; xi > xn_horiz_lt; xi--) {
        realx = 52*(xi)+260;
        realy = 300-30*(2*yn_horiz_lt-xi);
        draw(realx, realy, 'allowed', 1);
      }

      for (xi = xn+1; xi < xn_diag_gt; xi++) {
        realx = 52*(xi)+260;
        realxdiag = 52*(xn_diag_gt)+260;
        yd = yn+(xi - xn)*(yn_diag_gt - yn)/(xn_diag_gt - xn);
        realy = 300-30*(2*yd-xi);
        draw(realx, realy, 'allowed', 1);
      }

      for (xi = xn-1; xi > xn_diag_lt; xi--) {
        realx = 52*(xi)+260;
        yd = yn+(xi - xn)*(yn_diag_lt - yn)/(xn_diag_lt - xn);
        realy = 300-30*(2*yd-xi);
        draw(realx, realy, 'allowed', 1);
      }
    }
 // $('#answer').html("choosen: "+json.choosen+"; occupied: "+json.occupied+"; allowed: "+json.check_allowed+"; previous: "+JSON.stringify(json.previous));
 // alert(json.previous);
  } else {
    alert(json.alert_text);
    //alert('valid='+valid+' json.free='+json.free+' json.limits='+json.limits);
  //  $('#answer').html("choosen: "+json.choosen+"; occupied: "+json.occupied+"; allowed: "+json.check_allowed+"; previous: "+JSON.stringify(json.previous));
  //  alert(json.previous);
    free = false;
  }
}

window.onunload = function (e) {
  $.get("http://localhost:8000/close/", {game_id: gameid});
}

window.onbeforeunload = function (e) {
  $.get("http://localhost:8000/close/", {game_id: gameid});
}