// function timer(remaining) {
//   var m = Math.floor(remaining / 60);
//   var s = remaining % 60;
//   m = m < 10 ? "0" + m : m;
//   s = s < 10 ? "0" + s : s;
//   document.getElementById("countdown").innerHTML = `<small>Time left: ${m} : ${s}</small>`;
//   remaining -= 1;
//   if (remaining >= 0) {
//     setTimeout(function(){timer(remaining);}, 1000);
//     document.getElementById("resend").innerHTML = '&nbsp;';
//     return;
//   }
//   document.getElementById("resend").innerHTML = `<small class="d-none d-sm-block">Don't receive the code? &nbsp;</small> 
//   <small class="font-weight-bold fw-bold cursor" onclick="timer(60)" name='resend'>resend</small>`;
// }
// timer(60);

function move(event, nextid, previd) {
  const nextInput = document.getElementById(nextid);
  const prevInput = document.getElementById(previd);
  if (event.key === 'Backspace') {
    prevInput.focus();
  } else {
    nextInput.focus();
  }
}

