##Top-Down, Outside-In Design

The __user/__ directory is an inherent part of the framework.
API design from the client (user) perspective is done here.
All framework implementation should start _here_, whether by a framework product designer
or a framework implementor, but holding the perspective of the user of the framework—not that of
its implementor.

In the limit, no framework implementation work should start without the client code design done here first.