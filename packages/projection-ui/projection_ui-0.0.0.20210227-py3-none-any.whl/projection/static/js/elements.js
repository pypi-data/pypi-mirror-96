import { root_object, element_registry } from './stores.js';


function protomerge(what) {
  var stack = {};
  for (var i= 0; i < what.length; i++)
    stack = Object.assign(stack, Object.getOwnPropertyDescriptors(what[i]))
  return Object.create({}, stack);
}

/* Main api functions */

export function inject(element, data) {
  if (element in element_registry) {
    let res = new element_registry[element](data);
    root_object.id_tree[data.id] = res;
    root_object.id_tree[data.parent].children.push(res);
  } else {
    throw TypeException("Well this is embarrasing.");
  }
}

export function update(target, data) {
  if (target == 0) { // Special case, aliases to root
    root_object.root.update(data);
  } else if (target in root_object.id_tree) {
    root_object.id_tree[target].update(data);
  } else {
    throw ReferenceError("Well this is also embarrasing.");
  }
}

/* Some universal basics */

class Base {
  type = 'base';
  _id = null;
  _parent = null;
  _content = null;
  _obj = null;

  // These are the properties we want to make universal
  _border = null;
  _margin = null;
  _color = null;
  _background = null;
  _position = null // [top, left, height, width]

  update (data) {
    for(let prop in data) {
      this[prop] = data[prop];
    }
  }

  get id () { return _id; }
  set id (v) {
    this._id = v;
  }


  get obj () { return this._obj; }

  constructor(data) {
    this.id = data.id;
    this.parent = data.parent;
  }

  set position (position) {
    if (this._position == null) this._position = [];
    if (position[0]) this._obj.style('grid-row-start', (this._position[0] = position[0]))
    if (position[1]) this._obj.style('grid-column-start', (this._position[1] = position[1]))
    if (position[2]) this._obj.style('grid-row-end', `span ${(this._position[2] = position[2])}`)
    if (position[3]) this._obj.style('grid-column-end', `span ${(this._position[3] = position[3])}`)
  }

  get border () { return this._border; }
  set border (v) { this._obj.style('border', (this._border = v)); }

  get margin () { return this._margin; }
  set margin (v) { this._obj.style('margin', (this._margin = v)); }

  get padding () { return this._padding; }
  set padding (v) { this._obj.style('padding', (this._padding = v)); }
}

class ChildrenBase extends Base {  
  _children = null

  get children() { return (this._children || (this._children = [])); }
  set children(v) {
    this._children = v;
  }
}

class LeafBase extends Base {  
  _value = null
  get value() { return this._value; }
  set value(v) {
    this._value = v;
    this.obj.text(v);
  }
}

/* Root ... this one is a bit weird, we only really use one instance */

class Root extends ChildrenBase {
  constructor(target) {
    super({id: null, parent: null}); // We actually don't care about that constructor
    this._obj = d3.select(target);
    root_object.root = this;
  }
  set id (v) {
    super.id = v;
    root_object.id_tree[v] = root_object.root;
  }

  _title = null
  get title () { 
    if (!this._title) {
      this._title = d3.select('title').text();
    }
    return this._title;
  }
  set title (v) {
    this._title = v;
    d3.select('title').text(v);
  }
}

element_registry['root'] = Root;

/* Div - text only though */

class Div extends LeafBase {  
  type = 'div'
  constructor(data) {
    super(data);
    this._obj = root_object.id_tree[data.parent].obj.append('div')
    this.update(data);
  }
}

element_registry['div'] = Div;

/* Div - container edition ... contains nodes, not text */

class Container extends ChildrenBase {  
  type = 'container'
  constructor(data) {
    super(data);
    this._obj = root_object.id_tree[data.parent].obj.append('div')
    this.update(data);
  }
}

element_registry['container'] = Container;

/* Span - this is intended for combining with inline elements like links */

class Span extends LeafBase {
  type = 'span'
  constructor(data) {
    super(data);
    this._obj = root_object.id_tree[data.parent].obj.append('span')
    this.update(data);
  }
}

element_registry['span'] = Span;

/* Link */

class Link extends LeafBase {
  type = 'link'
  constructor(data) {
    super(data);
    this._obj = root_object.id_tree[data.parent].obj.append('a')
    this.update(data);
  }
}

element_registry['link'] = Link;

/* Button - Doesn't require a form */

class Button extends LeafBase {
  type = 'button'
  constructor(data) {
    super(data);
    this._obj = root_object.id_tree[data.parent].obj.append('button')
    this.update(data);
  }
}

element_registry['button'] = Button;

/* Tables ... This is only the <table> tag */

class Table extends ChildrenBase {  
  type = 'table'
  position = null // [top, left, height, width]
  constructor(data) {
    super(data);
    this._obj = root_object.id_tree[data.parent].obj.append('table')
    this.update(data);
  }
}

element_registry['table'] = Table;

/* Table rows */

class TableRow extends ChildrenBase {  
  type = 'tr'
  constructor(data) {
    super(data);
    this._obj = root_object.id_tree[data.parent].obj.append('tr');
    this.update(data);
  }
}

element_registry['tablerow'] = TableRow;
/* Div - text only though */

class List extends ChildrenBase {  
  type = 'ul'
  position = null // [top, left, height, width]
  constructor(data) {
    super(data);
    this._obj = root_object.id_tree[data.parent].obj.append('ul')
    this.update(data);
  }
}

element_registry['list'] = List;
