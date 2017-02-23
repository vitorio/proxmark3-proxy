# proxmark3-proxy

Web UI to manipulate a proxmark device proxied via expect

![Example of a web UI](https://zippy.gfycat.com/ForcefulDeadBlueshark.gif)

These are notes from a project worklog; this is not usable/production code, this is an example should you want to try building web-based UIs for proxmark work in the absence of a JSON API to the proxmark client

## 2015-07-11 22:57:32

Okay, so visualizers: https://gfycat.com/JoyfulSeparateIsabellinewheatear

I didn't see an easy way to include an HTTP server into the proxmark client's Lua implementation, so after playing around with Python expect, I have a simple Flask debug web server talking to the proxmark client using pexpect, running [Lua scripts that output JSON](https://github.com/vitorio/proxmark3/tree/securitoys/client/scripts).

```console
pi@raspberrypi ~/proxmark3/client $ python ~/pm3expect.py 
 * Running on http://0.0.0.0:8080/
 * Restarting with reloader
192.168.0.6 - - [12/Jul/2015 03:12:06] "GET / HTTP/1.1" 200 -
192.168.0.6 - - [12/Jul/2015 03:27:08] "GET /json-tnp3-reader HTTP/1.1" 200 -
```

In the background it's doing, like:

```console
proxmark3> script run jsonhfone
--- Executing: ./scripts/jsonhfone.lua, args''
{
  "atqa":"010F",
  "sak":1,
  "uid":"6F1230D7",
  "name":"NXP MIFARE TNP3xxx Activision Game Appliance"
}

-----Finished
```

And then the Python is finding the first `{` and the last `}` and returning that span.

It's way jankier than talking USB CDC directly using PySerial, but there isn't a maintained Python client.

Next is to visualize the entire card, reading and writing blocks, validating checksums, highlighting specific data areas, and then testing all the blocks and sectors...

## 2015-07-18 21:07:39

Okay, today's work involved finding a pure JavaScript templating system and XMLHTTPRequest wrapper that didn't require an entire goddamn toolchain.

[Garann's template-chooser](https://garann.github.io/template-chooser/) suggested:

* http://beebole.com/pure/
* https://github.com/flatiron/plates

Everything else had a template language, logic, a toolchain, jQuery dependencies, etc. Tried Pure first, seems alright. Tried Plates, it doesn't seem to support in-page DOM templates. Pure's only issues are it can't do partial updates, and when it does an update, you have to rebind anything that had function bindings.

There are even fewer XMLHTTPRequest wrappers that meet that criteria

* https://code.google.com/p/xhr/ doesn't help enough
* https://github.com/craig0990/xhr-ajax seems alright, but doesn't produce query strings for you
* https://github.com/ded/Reqwest does

So, Pure and Reqwest it is.

Then I added a new JSON proxy that reads data from the card and supports `#db#` error handling.

![Screen Shot 2015-07-18 at 8.16.30 PM.png](http://i.imgur.com/7PALtC0.png)

And, now we have a table that is in HTML first, and then is filled in with valid requests to the card, and this should not be ridiculous to extend to the entire card.

## 2015-07-29 03:59:22

And then I wrote and rewrote a bunch of JavaScript and now you can read an entire \[token\], or just a sector, or just a block, and retry all of those things in case of errors.

I think the error `th` should probably be a `td`, in retrospect.

It also renders the ASCII version of the data in the \[token\], and lets you show/hide trailer blocks.

![TNP3 test 09](http://i.imgur.com/Bf8uGnz.png)

I think now I want undo/redo of the visualization, maybe downloading of the \[token\], and then writing to it.

## 2015-08-08 17:55:45

The JS is pretty insane so I refactored my to-do list.

I need to be able to:

* Backup a \[token\]
* Restore a \[token\]
* Reset a \[token\]

To:

* Track changes in a \[token\] with repeated read/backups
* Display a \[token\]
* Write to a \[token\]

![tnp3brr](http://i.imgur.com/52U41uL.png)
