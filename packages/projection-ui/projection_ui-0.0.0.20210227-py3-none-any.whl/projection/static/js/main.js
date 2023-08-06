import * as stores from './stores.js';
import * as elements from './elements.js';

function escapeHtml(str) {
    let div = document.createElement('div');
    div.appendChild(document.createTextNode(str));
    return div.innerHTML;
}

function websock_connect() {
  var websocket = new WebSocket(`${document.location.protocol == 'http:' ? 'ws' : 'wss'}://${document.location.hostname}:${document.location.port}/websocket`);
  websocket.onopen = function(evt) { onOpen(evt) };
  websocket.onclose = function(evt) { onClose(evt) };
  websocket.onmessage = function(evt) { onMessage(evt) };
  websocket.onerror = function(evt) { onError(evt) };  
}

document.onreadystatechange = function () {
  new stores.element_registry['root']('div#layout');
  if (document.readyState === "complete") {
    websock_connect();
  }
}

function onOpen(evt)
{
  console.log(evt)
}

function onClose(evt)
{
  console.log(evt)
  setTimeout(5000, websock_connect);
}

function onError(evt)
{
  console.log(evt)
}

export let websock_types = {
  inject: function (payload) {
    // {type: 'inject', element: 'div', data: {id: ..., parent: ..., value: ...}}
    elements.inject(payload.element, payload.data);
  },
  update: function (payload) {
    // {type: 'update', id: ..., data: {value: ...}}
    elements.update(payload.id, payload.data);
  }
}

function onMessage(evt)
{
  console.log(evt.data)
  let data = JSON.parse(evt.data);
  if (data.type in websock_types) {
    websock_types[data.type](data)
  }
}


function doSend(message)
{
  websocket.send(JSON.stringify(message));
}
