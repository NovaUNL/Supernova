Roadmap
=======
| These are just ideas. Some might never be done at all.
| Some can be found as issues in the `code repository <https://gitlab.com/claudiop/Supernova/issues>`_.

Next few months
---------------
* :doc:`../apps/exercises`
    * Synopses integration
    * User-based custom generation (based on enrollments)
    * User Q&A (stack exchange alike)
* :doc:`../apps/feedback`
    * Accept new ideas for Supernova
    * Track issues with UNL itself (eg. x users spent y daily votes to have the ed. II door fixed)
* Properly consider :doc:`../apps/planet` and either implement it or scrap it.
* :doc:`../apps/chat`
    * User-user private messages
    * User-group private messages
* Group schedules
* :doc:`../apps/events`
    * Generic calendar
    * Generation
    * Notification
    * User preferences
* Meals and campus services

    * Static information that is rarely changed (such as prices)
* :doc:`../apps/news`
    * User submitted content
* Maps

    * Add geospatial information such as building blueprints (stalled with bureaucracy)
* :doc:`../apps/api`
    * Expose interfaces required to make native applications
* Moderation

    * User roles
    * Account suspension
* Content search
* Infrastructure

    * Some worker that handles server outages and updates gracefully
    * Status page
    * Rate limit (we need to see if this is that important)

Hopefully before the sun engulfs us
-----------------------------------
* Locale support (for the erasmus folks)
* Campus routing
* Achievement system
* Karma point system
* Stores (eg. for the students association to "sell" shirts)

    * Classified items store (possibly a bad idea)

* User real-time chat
* Transportation calculation (partially implemented, can be improved)
* Lost & Found app
* Campus gallery, maybe with panoramas, something cool to impress future caloiros.
* Recommend places for studying based on position
* Add loggers everywhere

    * Abuse detection
    * Vandalism reversion
    * Banhammer employment

* Proper SMTP support and email notifications
* Custom news feed based on preferences
* Ignore lists (avoid dumping unwanted subjects or other users content onto a user)

Awaiting on CLIPy
-----------------
These are important tasks which require further progress on the CLIPy backend before getting implemented by Supernova:

* Grades
* Course curricular plans (probably unreliable, already attempted)
* Class

  * Summaries
  * Calendars
  * Schedule changes

* Information updates

  * Changes recording
  * Selective updates (eg. just a class instance)