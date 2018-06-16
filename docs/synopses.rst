Synopses
========
The synopses app is a wikipedia-alike knowledge source.

| Students can freely submit content, with the content unit being called a **section**.
| Sections can be linked into two different sources:

* The first (mandatory) are synopses **topics**:

    * A **topic** is contained within a **subarea**.
    * A **subarea** is contained within an **area**.
    
    The proper hirarchy for the section `First degree differential equations` would be:
    
    * `Mathematics` (**Area**)
        
        * `Mathemathical analysis` (**Subarea**)
            
            * `Differential calculus` (**Topic**)
            
                * `First degree differential equations` (**Section**)

* The second (totally optional) are **class synopses**:

    * | Class synopses are small aggregations of sections.
      | Those sections are obviosly meant to have the corresponding class teachings.
      | Yet sections aren't ever meant to be exclusive for a class, they're meant to be reused.
      
| Topics, topic sections and class sections have order; that is, some index attached to their relations.
| Areas and subareas aren't sortable, and the frontend code will probably use alphabetic order.

| The **section** content is stored in HTML. It's not a perfect solution, but it's the least painful and it's a very powerful and flexible one.
| Besides markdown and LaTeX I think it is the only one which is standard, supports any screen format, OS, device, can embed images and LaTeX formulas.
| If you have any brilliant idea which is somehow way better and makes the conversion worth it, then feel free to tell.

Submodules
----------

synopses.forms module
---------------------

.. automodule:: synopses.forms
    :members:
    :undoc-members:
    :show-inheritance:

synopses.models module
----------------------

.. automodule:: synopses.models
    :members:
    :undoc-members:
    :show-inheritance:

synopses.views module
---------------------

.. automodule:: synopses.views
    :members:
    :undoc-members:
    :show-inheritance:

Module contents
---------------

.. automodule:: synopses
    :members:
    :undoc-members:
    :show-inheritance:
