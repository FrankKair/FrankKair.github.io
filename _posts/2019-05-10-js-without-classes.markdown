---
layout: post
title:  "Classy JavaScript 🎩"
date:   2019-05-10 21:08:00 +0100
categories: javascript
---

I find it odd that, for example, *classes* were introduced in the language, since we already have a *prototype* system in place. I think that gives a shortcut to developers that are not willing to learn a different concept.

I'm a big believer that languages should have less facelifts and more consistency. Not only that, I also enjoy learning languages that teach new concepts, making me think fundamentally different in at least one aspects. Some examples: 

- **Ruby** taught me metaprogramming (open classes, dynamic method creation);
- **Swift** taught me Optional types, protocol extensions and my first steps into functional programming;
- **Rust** taught me ownership, algebraic data types and pattern matching.

On "**How JavaScript Works**"[^fn1], Douglas Crockford says:

> "JavaScript also has more convetional looking `class` syntax that was designed specifically for developers who do not know nor ever will know how JavaScript works. It allows transfer of skills from lesser languages with no new learning."

This is a rather strong statement, but it does have some truth to it. If you use JavaScript as you would use any other language, you're missing the opportunity to learn new concepts, like prototypes and closures (of course, that also depends on your programming language upbringing).

### Classless

Classes are mainly used to hold state and have an attached behaviour, while also providing type extensibility via inheritance and composition. Let's try to have this semantics without the *class* keyword. The first idea is to use the prototype model:

```javascript
function Counter() {
  this.count = 0;
}

Counter.prototype.up = function() {
  this.count += 1;
  return this;
}

const c = new Counter();
const count = c.up().up().count;
console.log(count); // 2
```

In this example, we create Counter (with capital letter to signal that it needs the *new* keyword in order to be invoked) with a state, a property `count` set to zero and a *method* that it's attached to its prototype. What I like about this idea is that one uses the constructor for data and the prototype for behaviour, something like what Rust has with *struct* and *impl* or Go with *struct* and *receivers*.

One can tinker with the `count` property though (since it's basically public), and being able to modify data directly is not good encapsulation. We should always define a contract, an interface for our classes / structs / objects. Functions to the rescue!

```javascript
function counter() {
  let count = 0;

  function up() {
    count += 1;
    return Object.freeze({ up, val });
  }

  function val() {
    return count;
  }

  return Object.freeze({ up, val });
}

const c = counter();
const count = c.up().up().val();
console.log(count); // 2
```

Think about this for a second. We have state (the variable `count`) and we have behaviour (the methods `up` and `val`) as well. Not only that, but by controlling what we expose via returning `Object.freeze`, we effectively have *private* access level in our "class"! The bad thing is that every time we create a new `counter` object, we're recreating all of its functions, and that's why prototypes are good, because when you attach behaviour to them, every new instance comes clean with its properties. When you call a method, like `c.up()`, the JavaScript runtime asks the Counter prototype if it has something called `up` attached to it.

Ok, that solves grouping state and behaviour, but how do we introduce composition? Here's another example with functions:

```javascript
// Think of this constructor as an interface / protocol / trait
function flying(type) {
  function fly() {
    return `I am a ${type} and I can fly!`;
  }

  return Object.freeze({ fly });
}

// The "class" that "implements" the interface
function bird(type) {
  return Object.freeze({
    fly: flying(type).fly
  });
}

const b = bird('Canary');
console.log(b.fly()); // I am a Canary and I can fly!
```

We can include another function in our "class" to act as a building block, creating composition. Hopefully that shows that using "non traditional" methods to create custom data types is feasible and also cool to learn.

### Using class

Here's the Counter example using the `class` keyword and the new `#` symbol for private members[^fn2]:

```javascript
class Counter {
  #count = 0;

  get val() {
    return this.#count;
  }

  up() {
    this.#count += 1;
    return this;
  }
}

const c = new Counter();
const count = c.up().up().val;
console.log(count); // 2
```

### Links

[^fn1]: [How JavaScript Works](http://www.howjavascriptworks.com)

[^fn2]: [What’s new in JavaScript (Google I/O ’19)](https://www.youtube.com/watch?v=c0oy0vQKEZE)
