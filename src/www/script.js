// Listen to message from child window
// window.attachEvent('onmessage',function(e) {
window.addEventListener('message',function(e) {
  console.log('Got message from child:', e)
}, false);
