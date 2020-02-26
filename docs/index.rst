Supernova
=========

Intro
-----

Welcome to the Supernova documentation.

| These webpages are not meant to be seen the end user (that's you caloiro!),
  they are instead meant as platform to describe the `magic` that makes Supernova work, leave some brainstorming and
  define future plans.

The writing contains both textual explanations and formal code documentation,
and while the former can be easily understood by anyone, the latter is meant to aid those who want to contribute code.

What is Supernova?
------------------

| Supernova will hopefully be a do-it-all university system.
| Right now it is more of a platform which piggybacks on the current FCT UNL system (CLIP) and adds a few
  features of its own.

It consists of two main parts:

* `CLIPy <https://gitlab.com/claudiop/CLIPy>`_  (`CLIP-Crawler on PyPi <https://pypi.org/project/CLIP-Crawler/>`_) which
  is an HTTP crawler that periodically fetches data from CLIP.
* The Supernova webapp, on which this documentation focuses.

Supernova is meant to be independent from CLIP, although it is currently heavily tied to the CLIP concepts.
The future intention is to have it completely independent from such systems,
leaving the system bridge completely up to a bridge (such as CLIPy + a few scripts to adapt the data).

Who develops Supernova?
-----------------------

| Currently, one of those "pesky students" who wants to have the UNL IT infrastructure improved.
| Therefore, it is safe to assume that this system has no official ties to any University, which takes us to
  the next point:

Who can contribute?
-------------------

| Anyone, feel free to do so.

Supernova's code is licensed with `GPLv3 <https://www.gnu.org/licenses/quick-guide-gplv3.html>`_;
as long as you agree to it, implement some cool idea of yours, reach a consensus with us on how to integrate it,
and stay within legal and ethical boundaries, you can change this service for better.

Something cool to have on your curriculum whenever you start your career huh `*wink wink*`.


So... what's the plan?
----------------------

In short: To make this project good enough to replace everything subpar that you can think of in your current
University management system.

Ideally this project will someday end up being gifted to the UNL administration, and those systems you hate will slowly
be transitioned to Supernova. Realistically that is the very best case scenario, and it is quite likely that this
system is doomed from the start due to the lack of manpower and bureaucracy within UNL.

| If you want to know about planned features check the :doc:`information/roadmap` to know more.
| As implicitly stated, Supernova is made with volunteer time, and as such things can get slow to progress.

.. toctree::
   :maxdepth: 1
   :caption: Information

   information/modules

.. toctree::
   :maxdepth: 1
   :caption: Apps

   apps/modules



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
