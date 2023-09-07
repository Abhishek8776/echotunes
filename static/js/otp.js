function move(event, nextid, previd) {
  const nextInput = document.getElementById(nextid);
  const prevInput = document.getElementById(previd);
  if (event.key === 'Backspace') {
    prevInput.focus();
  } else {
    nextInput.focus();
  }
}

