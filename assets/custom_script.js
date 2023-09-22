// window.onresize = function() {
//   let windowSizeInput = document.getElementById('window-size-input');
//   console.log('Updating size!');
//   if (!windowSizeInput) {
//       // If the hidden input doesn't exist, create a new one.
//       windowSizeInput = document.createElement('input');
//       windowSizeInput.id = 'window-size-input';
//       // windowSizeInput.type = 'hidden';
//       document.body.appendChild(windowSizeInput);
//   }
//   // Update the value of the hidden input.
//   windowSizeInput.value = JSON.stringify({
//       width: window.innerWidth,
//       height: window.innerHeight
//   });
//   // Manually trigger an 'input' event so Dash can detect the change.
//   windowSizeInput.dispatchEvent(new Event('input', { bubbles: true }));
// }

if(!window.dash_clientside) {window.dash_clientside = {};}

window.dash_clientside.clientside = {
    get_window_size: function() {
        return {
            width: window.innerWidth,
            height: window.innerHeight
        };
    }
};
